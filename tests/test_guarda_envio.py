# -*- coding: utf-8 -*-
"""Estragos propositados da guarda de envio. Correr: python3 tests/test_guarda_envio.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import guarda_envio as g  # noqa: E402

SAG = "0xFEd69e8ee87A1F0fBbF8409ab654FC51832cDEe5"
OUTRO = "0x2ef8cfB97EcCcf7C62f551639fe6dB79022d0d8C"

# o caso bom passa (qualquer capitalizacao do destino permitido)
assert g.verificar_envio(SAG, 0.01, 0.05) == (True, "ok")
assert g.verificar_envio(SAG.lower(), 0.05, 0.05)[0]

estragos = {
    "sem limite": lambda: g.verificar_envio(SAG, 0.01),
    "limite zero": lambda: g.verificar_envio(SAG, 0.01, 0),
    "limite negativo": lambda: g.verificar_envio(SAG, 0.01, -1),
    "limite nan": lambda: g.verificar_envio(SAG, 0.01, float("nan")),
    "limite infinito": lambda: g.verificar_envio(SAG, 0.01, float("inf")),
    "limite texto": lambda: g.verificar_envio(SAG, 0.01, "muito"),
    "valor zero": lambda: g.verificar_envio(SAG, 0, 0.05),
    "valor negativo": lambda: g.verificar_envio(SAG, -0.01, 0.05),
    "valor nan": lambda: g.verificar_envio(SAG, float("nan"), 0.05),
    "valor acima do limite": lambda: g.verificar_envio(SAG, 0.06, 0.05),
    "destino fora da lista": lambda: g.verificar_envio(OUTRO, 0.01, 0.05),
    "destino vazio": lambda: g.verificar_envio("", 0.01, 0.05),
    "destino nao texto": lambda: g.verificar_envio(None, 0.01, 0.05),
}
n = 0
for nome, f in estragos.items():
    ok, motivo = f()
    assert not ok and motivo.startswith("recusado"), f"estrago nao apanhado: {nome}"
    n += 1
assert g.DESTINOS_PERMITIDOS == frozenset({g.SAGRADA_ANTIGA}), "a lista de destinos mudou"
print(f"estragos propositados apanhados: {n}/{len(estragos)}")
