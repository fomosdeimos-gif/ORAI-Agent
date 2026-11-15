# -*- coding: utf-8 -*-
"""Estragos propositados da guarda de envio. Correr: python3 tests/test_guarda_envio.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import guarda_envio as g  # noqa: E402

SAG = "0xFEd69e8ee87A1F0fBbF8409ab654FC51832cDEe5"
NOVA = "0x2ef8cfB97EcCcf7C62f551639fe6dB79022d0d8C"
OUTRO = "0x89460d9e0590559e63860197dfe2ac648A753584"  # a operacional: nao esta na lista

# os dados da lista batem com os enderecos escritos em checksum
assert g.SAGRADA_ANTIGA == SAG.lower() and len(g.SAGRADA_ANTIGA) == 42
assert g.SAGRADA_NOVA == NOVA.lower() and len(g.SAGRADA_NOVA) == 42
assert g.DESTINOS_PERMITIDOS == frozenset({g.SAGRADA_ANTIGA, g.SAGRADA_NOVA}), "a lista de destinos mudou"
assert g.FUNDACAO_BTC.startswith("bc1q") and g.FUNDACAO_BTC not in g.DESTINOS_PERMITIDOS

# sem tecto: valores enormes passam para as carteiras do criador, com ou sem limite
for dest in (SAG, SAG.lower(), NOVA, NOVA.lower()):
    assert g.verificar_envio(dest, 0.01) == (True, "ok"), dest
    assert g.verificar_envio(dest, 1e9) == (True, "ok"), "nao pode haver tecto"
    assert g.verificar_envio(dest, 0.05, 0.05)[0]

estragos = {
    "valor zero": lambda: g.verificar_envio(SAG, 0),
    "valor negativo": lambda: g.verificar_envio(SAG, -0.01),
    "valor nan": lambda: g.verificar_envio(SAG, float("nan")),
    "valor infinito": lambda: g.verificar_envio(SAG, float("inf")),
    "valor texto": lambda: g.verificar_envio(SAG, "muito"),
    "limite dado e ultrapassado": lambda: g.verificar_envio(SAG, 0.06, 0.05),
    "limite dado zero": lambda: g.verificar_envio(SAG, 0.01, 0),
    "limite dado nan": lambda: g.verificar_envio(SAG, 0.01, float("nan")),
    "limite dado texto": lambda: g.verificar_envio(SAG, 0.01, "x"),
    "destino fora da lista (operacional)": lambda: g.verificar_envio(OUTRO, 0.01),
    "destino fundacao btc": lambda: g.verificar_envio(g.FUNDACAO_BTC, 0.01),
    "destino quase igual": lambda: g.verificar_envio(SAG[:-1] + "6", 0.01),
    "destino vazio": lambda: g.verificar_envio("", 0.01),
    "destino nao texto": lambda: g.verificar_envio(None, 0.01),
}
n = 0
for nome, f in estragos.items():
    ok, motivo = f()
    assert not ok and motivo.startswith("recusado"), f"estrago nao apanhado: {nome}"
    n += 1
print(f"estragos propositados apanhados: {n}/{len(estragos)}")
