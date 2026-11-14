# -*- coding: utf-8 -*-
"""Vigia da Fundacao ORA (so leitura, sem chaves).

Le o endereco Bitcoin da Fundacao em duas fontes Esplora independentes.
So afirma saldo e transaccoes quando as duas concordam. Cada entrada e
classificada, mas o vigia NUNCA diz "externa": quem classifica uma entrada
como receita externa e Unum. Aqui so se distingue:
  - "interna": todas as origens sao enderecos do organismo ou de Unum;
  - "por_classificar": qualquer outra coisa (nao e receita, nao e sustento).
Nao assina, nao paga, nao troca, nao contacta ninguem.
"""
import json
import urllib.request
from datetime import datetime, timezone

FUNDACAO_BTC = "bc1qfs8967x9mzhwhcse4z7kjuuhsmx0kmz5v6j9w7"
# Enderecos Bitcoin do organismo: Fundacao/operacional e sagrada antiga.
INTERNOS_BTC = frozenset({FUNDACAO_BTC, "bc1qhcsh78k8jrn3qllvd9al8nq4af4cyzefx6vqqf"})
FONTES = ("https://blockstream.info/api", "https://mempool.space/api")
USER_AGENT = "ORAI-vigia/1.0 (leitura publica; sem chaves)"


def _get(base, caminho):
    req = urllib.request.Request(base + caminho, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def _resumo_tx(tx, endereco, internos):
    recebido = sum(o.get("value", 0) for o in tx["vout"] if o.get("scriptpubkey_address") == endereco)
    gasto = sum(
        (i.get("prevout") or {}).get("value", 0)
        for i in tx["vin"]
        if (i.get("prevout") or {}).get("scriptpubkey_address") == endereco
    )
    origens = sorted({(i.get("prevout") or {}).get("scriptpubkey_address") or "?" for i in tx["vin"]})
    sentido = "entrada" if recebido > gasto else "saida"
    if sentido == "entrada":
        classe = "interna" if all(o in internos for o in origens) else "por_classificar"
    else:
        classe = "saida"  # sair nao e receita; o vigia so regista
    return {
        "txid": tx["txid"],
        "bloco": tx["status"].get("block_height") if tx["status"].get("confirmed") else None,
        "confirmada": bool(tx["status"].get("confirmed")),
        "sentido": sentido,
        "recebido_sats": recebido,
        "gasto_sats": gasto,
        "origens": origens,
        "classe": classe,
    }


def vigiar(endereco=FUNDACAO_BTC, fontes=FONTES, internos=INTERNOS_BTC, obter=_get):
    quando = datetime.now(timezone.utc).isoformat()
    leituras, falhadas = {}, []
    for f in fontes:
        try:
            info = obter(f, f"/address/{endereco}")
            txs = obter(f, f"/address/{endereco}/txs")
            cs, ms = info["chain_stats"], info["mempool_stats"]
            leituras[f] = {
                "saldo_confirmado": cs["funded_txo_sum"] - cs["spent_txo_sum"],
                "saldo_mempool": ms["funded_txo_sum"] - ms["spent_txo_sum"],
                "txs": sorted((_resumo_tx(t, endereco, internos) for t in txs), key=lambda x: x["txid"]),
            }
        except Exception as e:
            falhadas.append({"fonte": f, "erro": f"{type(e).__name__}: {e}"})

    base = {"formato": "orai-vigia-fundacao/v1", "lido_em": quando, "endereco": endereco,
            "fontes_falhadas": falhadas,
            "nao_afirma": ["receita externa (so Unum classifica)", "titularidade legal",
                           "valor em moeda corrente", "procura ou adopcao"]}
    if not leituras:
        return {**base, "estado": "sem_fontes", "verificado": False}
    chave = {f: json.dumps(v, sort_keys=True) for f, v in leituras.items()}
    if len(set(chave.values())) > 1:
        return {**base, "estado": "discordam", "verificado": False, "fontes": sorted(leituras)}
    unica = next(iter(leituras.values()))
    estado = "concordam" if len(leituras) >= 2 else "fonte_unica"
    return {**base, "estado": estado, "verificado": estado == "concordam",
            "fontes": sorted(leituras), **unica}


if __name__ == "__main__":
    print(json.dumps(vigiar(), indent=2, ensure_ascii=False))
