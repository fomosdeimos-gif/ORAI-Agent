# -*- coding: utf-8 -*-
"""Estragos propositados dos pedidos supervisionados e da ligacao ao envio.
Correr: python3 tests/test_pedidos.py   (so biblioteca padrao; o web3 e simulado)"""
import asyncio
import json
import os
import sys
import tempfile
import types
from unittest.mock import AsyncMock, Mock

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "src"))
fake = types.ModuleType("web3")
fake.Web3 = Mock()
sys.modules["web3"] = fake
import pedidos as p  # noqa: E402
from src.wallet import WalletManager  # noqa: E402

SAG = "0xFEd69e8ee87A1F0fBbF8409ab654FC51832cDEe5"
NOVA = "0x2ef8cfB97EcCcf7C62f551639fe6dB79022d0d8C"
OUTRO = "0x89460d9e0590559e63860197dfe2ac648A753584"


def falha(f, nome):
    try:
        f()
    except (ValueError, json.JSONDecodeError):
        return 1
    raise AssertionError(f"estrago nao apanhado: {nome}")


def nova():
    return tempfile.mkdtemp()


n = 0
# --- o caminho bom
d = nova()
a = p.propor(d, SAG, "0.5", "sustento de Unum")
assert a["destino"] == SAG.lower() and a["valor_eth"] == "0.5"
r = p.rever(d)
assert r["cadeia_inteira"] and r["pedidos"][a["id"]]["estado"] == "proposto"
assert p.aprovado(d, a["id"], SAG, 0.5) == (False, "recusado: pedido sem decisao verificada")
dec = p.decidir(d, a["id"])
assert dec["resultado"] == "verificado" and p.rever(d)["pedidos"][a["id"]]["estado"] == "verificado"
assert p.aprovado(d, a["id"], SAG.lower(), 0.5) == (True, "ok")
assert p.aprovado(d, a["id"], SAG, 0.25)[0], "valor menor que o pedido passa"
assert p.propor(d, NOVA, 1e9, "sem tecto")["valor_eth"] == "1000000000", "nao ha tecto"

# --- propor recusa o que a guarda nunca deixaria passar
for nome, f in {
    "destino fora da lista": lambda: p.propor(nova(), OUTRO, "1", "x"),
    "destino vazio": lambda: p.propor(nova(), "", "1", "x"),
    "valor zero": lambda: p.propor(nova(), SAG, "0", "x"),
    "valor negativo": lambda: p.propor(nova(), SAG, "-1", "x"),
    "valor nan": lambda: p.propor(nova(), SAG, "nan", "x"),
    "valor infinito": lambda: p.propor(nova(), SAG, "inf", "x"),
    "valor texto": lambda: p.propor(nova(), SAG, "muito", "x"),
    "motivo vazio": lambda: p.propor(nova(), SAG, "1", "  "),
    "motivo enorme": lambda: p.propor(nova(), SAG, "1", "x" * 501),
    "motivo com chave": lambda: p.propor(nova(), SAG, "1", "usa 0x" + "a" * 64),
    "decidir pedido inexistente": lambda: p.decidir(d, "0" * 64),
    "decisao duplicada": lambda: p.decidir(d, a["id"]),
}.items():
    n += falha(f, nome)


# --- a cadeia detecta adulteracao e linhas apagadas
def adulterar(modo):
    dd = nova()
    x = p.propor(dd, SAG, "1", "um")
    p.decidir(dd, x["id"])
    p.propor(dd, NOVA, "2", "dois")
    cam = os.path.join(dd, p.FICHEIRO)
    linhas = open(cam, encoding="utf-8").read().splitlines()
    if modo == "valor":
        o = json.loads(linhas[0]); o["valor_eth"] = "999"; linhas[0] = json.dumps(o, sort_keys=True)
    elif modo == "apagar":
        del linhas[1]
    elif modo == "trocar":
        linhas[0], linhas[2] = linhas[2], linhas[0]
    elif modo == "id":
        o = json.loads(linhas[1]); o["resultado"] = "verificado"; o["id"] = "f" * 64; linhas[1] = json.dumps(o, sort_keys=True)
    open(cam, "w", encoding="utf-8").write("\n".join(linhas) + "\n")
    return lambda: p.rever(dd)


for modo in ("valor", "apagar", "trocar", "id"):
    n += falha(adulterar(modo), f"adulteracao {modo}")


# --- aprovado nao abre portas
def ap(destino=SAG, valor=1, decidir=True, usar=False):
    dd = nova()
    x = p.propor(dd, SAG, "1", "teste")
    if decidir:
        p.decidir(dd, x["id"])
    if usar:
        p.registar_uso(dd, x["id"], "antes")
    return p.aprovado(dd, x["id"], destino, valor)


assert ap()[0]
for nome, res in {
    "sem decisao": ap(decidir=False),
    "destino diferente": ap(destino=NOVA),
    "valor acima": ap(valor=1.5),
    "ja usado": ap(usar=True),
    "pedido inexistente": p.aprovado(nova(), "0" * 64, SAG, 1),
    "valor invalido": ap(valor="nan"),
}.items():
    assert not res[0] and res[1].startswith("recusado"), f"estrago nao apanhado: {nome}"
    n += 1
n += falha(lambda: p.registar_uso(nova(), "x", "meio"), "fase invalida")

# --- um pedido forjado com destino fora da lista fica 'recusado' e nunca e aprovado
dd = nova()
p.propor(dd, SAG, "1", "ok")
cam = os.path.join(dd, p.FICHEIRO)
o = json.loads(open(cam, encoding="utf-8").read())
o["destino"] = OUTRO.lower(); o.pop("id"); o["id"] = p._id(o)
open(cam, "w", encoding="utf-8").write(json.dumps(o, sort_keys=True) + "\n")
dec = p.decidir(dd, o["id"])
assert dec["resultado"] == "recusado" and not p.aprovado(dd, o["id"], OUTRO, 1)[0]
n += 1


# --- ligacao ao envio (web3 simulado): sem pedido nao envia; com pedido envia uma vez
def carteira():
    w = WalletManager.__new__(WalletManager)
    w.logger = Mock()
    w.w3 = Mock()
    w.account = Mock()
    w.prepare_transaction = AsyncMock(return_value={"to": SAG})
    h = Mock()
    h.hex = Mock(return_value="0xabc")
    w.w3.eth.send_raw_transaction = Mock(return_value=h)
    return w


def enviar(w, pasta, pedido, destino=SAG, valor=0.5):
    return asyncio.run(w.send_transaction(destino, valor, pedido_id=pedido, pasta_pedidos=pasta))


dd = nova()
x = p.propor(dd, SAG, "0.5", "envio de teste")
w = carteira()
for nome, res in {
    "sem pedido": enviar(w, dd, None),
    "pedido nao decidido": enviar(w, dd, x["id"]),
    "pedido inexistente": enviar(w, dd, "0" * 64),
    "destino fora da lista": enviar(w, dd, x["id"], destino=OUTRO),
}.items():
    assert res is None, f"estrago nao apanhado: {nome}"
    n += 1
assert w.w3.eth.send_raw_transaction.call_count == 0, "enviou sem pedido verificado"
p.decidir(dd, x["id"])
assert enviar(w, dd, x["id"], valor=0.6) is None, "enviou acima do pedido"
n += 1
assert enviar(w, dd, x["id"]) == "0xabc" and w.w3.eth.send_raw_transaction.call_count == 1
assert enviar(w, dd, x["id"]) is None and w.w3.eth.send_raw_transaction.call_count == 1, "usou o pedido duas vezes"
n += 1
usos = [r for r in p.ler(dd) if r["tipo"] == "uso"]
assert [u["fase"] for u in usos] == ["antes", "depois"] and usos[1]["tx"] == "0xabc"
assert p.rever(dd)["pedidos"][x["id"]]["estado"] == "usado"
print(f"estragos propositados apanhados: {n}")
