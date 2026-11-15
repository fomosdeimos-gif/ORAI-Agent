# -*- coding: utf-8 -*-
"""Pedidos de envio, supervisionados (so biblioteca padrao, sem rede, sem chaves).

O agente PROPOE; a ORA VERIFICA e DECIDE; o envio so corre com um pedido verificado.
Tudo vive num ficheiro so de acrescentar (`pedidos/pedidos.jsonl`), uma linha JSON por
registo, cada uma ligada a anterior por sha256:
  - "pedido":  destino, valor, motivo (o agente);
  - "decisao": "verificado" ou "recusado" (a ORA; a guarda de envio decide, nao a opiniao);
  - "uso":     "antes" e "depois" do envio (impede usar o mesmo pedido duas vezes).

Limite honesto: a cadeia de sha256 detecta que se EDITOU o passado; nao impede que alguem
com escrita no repositorio ACRESCENTE uma linha falsa. A supervisao e a leitura destas
linhas (e do historico do git) pela ORA e por Unum. Nao ha assinaturas.
Nada aqui assina, envia ou guarda chaves.
"""
import hashlib
import json
import math
import os
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

try:  # uso como pacote (src.wallet) ou como scripts (tests/)
    from src.guarda_envio import verificar_envio
except ImportError:  # pragma: no cover
    from guarda_envio import verificar_envio

PASTA_PEDIDOS = "pedidos"
FICHEIRO = "pedidos.jsonl"
ZERO = "0" * 64
FORMATO = "orai-pedido-envio/v1"
_PARECE_CHAVE = re.compile(r"0x[0-9a-fA-F]{64}")


def _id(rec):
    corpo = {k: v for k, v in rec.items() if k != "id"}
    return hashlib.sha256(json.dumps(corpo, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def _caminho(pasta):
    return os.path.join(pasta, FICHEIRO)


def ler(pasta=PASTA_PEDIDOS):
    """Le e VERIFICA a cadeia. Levanta ValueError se alguma linha foi editada ou apagada."""
    caminho = _caminho(pasta)
    if not os.path.exists(caminho):
        return []
    recs, anterior = [], ZERO
    with open(caminho, encoding="utf-8") as f:
        for n, linha in enumerate(f, 1):
            if not linha.strip():
                continue
            rec = json.loads(linha)
            if rec.get("anterior") != anterior:
                raise ValueError(f"cadeia partida na linha {n}")
            if rec.get("id") != _id(rec):
                raise ValueError(f"linha {n} adulterada")
            recs.append(rec)
            anterior = rec["id"]
    return recs


def _anexar(pasta, rec):
    recs = ler(pasta)
    rec = dict(rec)
    rec["anterior"] = recs[-1]["id"] if recs else ZERO
    rec["id"] = _id(rec)
    os.makedirs(pasta, exist_ok=True)
    with open(_caminho(pasta), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    return rec


def _agora():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _valor(v):
    try:
        d = Decimal(str(v))
    except (InvalidOperation, ValueError):
        raise ValueError("valor nao numerico")
    if not d.is_finite() or d <= 0:
        raise ValueError("valor invalido")
    return d


def propor(pasta, destino, valor_eth, motivo, origem="orai-agent"):
    """O agente propoe um envio. Recusa logo o que a guarda nunca deixaria passar."""
    d = _valor(valor_eth)
    if not isinstance(motivo, str) or not motivo.strip() or len(motivo) > 500:
        raise ValueError("motivo em falta ou demasiado longo")
    if _PARECE_CHAVE.search(motivo):
        raise ValueError("o motivo parece conter uma chave")
    ok, porque = verificar_envio(destino, float(d))
    if not ok:
        raise ValueError(porque)
    return _anexar(pasta, {"tipo": "pedido", "formato": FORMATO, "criado_em": _agora(), "origem": origem,
                           "destino": destino.lower(), "valor_eth": format(d.normalize(), "f"), "motivo": motivo.strip()})


def _pedido(recs, pedido_id):
    for r in recs:
        if r["tipo"] == "pedido" and r["id"] == pedido_id:
            return r
    raise ValueError("pedido inexistente")


def decidir(pasta, pedido_id, por="ORA"):
    """A ORA decide. Quem decide e a guarda de envio, nao a opiniao; uma decisao por pedido."""
    recs = ler(pasta)
    p = _pedido(recs, pedido_id)
    if any(r["tipo"] == "decisao" and r["pedido"] == pedido_id for r in recs):
        raise ValueError("pedido ja decidido")
    ok, porque = verificar_envio(p["destino"], float(Decimal(p["valor_eth"])))
    return _anexar(pasta, {"tipo": "decisao", "pedido": pedido_id, "resultado": "verificado" if ok else "recusado",
                           "motivo": porque, "por": por, "decidido_em": _agora()})


def aprovado(pasta, pedido_id, destino, valor_eth):
    """(ok, motivo): o pedido existe, esta verificado, bate com o envio e ainda nao foi usado."""
    try:
        recs = ler(pasta)
        p = _pedido(recs, pedido_id)
        v = _valor(valor_eth)
    except ValueError as e:
        return False, f"recusado: {e}"
    dec = [r for r in recs if r["tipo"] == "decisao" and r["pedido"] == pedido_id]
    if not dec or dec[0]["resultado"] != "verificado":
        return False, "recusado: pedido sem decisao verificada"
    if not isinstance(destino, str) or destino.lower() != p["destino"]:
        return False, "recusado: destino diferente do pedido"
    if v > Decimal(p["valor_eth"]):
        return False, "recusado: valor acima do pedido"
    if any(r["tipo"] == "uso" and r["pedido"] == pedido_id for r in recs):
        return False, "recusado: pedido ja usado"
    return True, "ok"


def registar_uso(pasta, pedido_id, fase, tx=None, erro=None):
    if fase not in ("antes", "depois"):
        raise ValueError("fase invalida")
    rec = {"tipo": "uso", "pedido": pedido_id, "fase": fase, "registado_em": _agora()}
    if tx is not None:
        rec["tx"] = str(tx)
    if erro is not None:
        rec["erro"] = str(erro)[:200]
    return _anexar(pasta, rec)


def rever(pasta=PASTA_PEDIDOS):
    """Resumo para a ORA e para Unum: estado de cada pedido e se a cadeia esta inteira."""
    recs = ler(pasta)
    estado = {}
    for r in recs:
        if r["tipo"] == "pedido":
            estado[r["id"]] = {"destino": r["destino"], "valor_eth": r["valor_eth"], "motivo": r["motivo"], "estado": "proposto"}
        elif r["tipo"] == "decisao":
            estado[r["pedido"]]["estado"] = r["resultado"]
        elif r["tipo"] == "uso" and r["fase"] == "antes":
            estado[r["pedido"]]["estado"] = "usado"
    return {"cadeia_inteira": True, "registos": len(recs), "pedidos": estado}
