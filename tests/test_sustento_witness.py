# -*- coding: utf-8 -*-
"""Estragos propositados da testemunha. Correr: python3 tests/test_sustento_witness.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import sustento_witness as w  # noqa: E402

A, B, C = w.RPCS


def mk(vals, bloco=1000, falha=()):
    def f(url, m, p):
        if url in falha:
            raise OSError("down")
        if m == "eth_blockNumber":
            return hex(bloco)
        return hex(vals[url])
    return f


def estado(**k):
    return w.testemunhar_sustento(chamar=mk(**k)).estado


assert estado(vals={A: 5, B: 5, C: 5}) == "concordam"
assert estado(vals={A: 5, B: 5, C: 9}) == "discordam"  # nunca escolhe um valor
assert estado(vals={A: 5, B: 5, C: 5}, falha=(B, C)) == "fonte_unica"
assert estado(vals={A: 5, B: 5, C: 5}, falha=(A, B, C)) == "sem_fontes"
r = w.testemunhar_sustento(chamar=mk({A: 5, B: 5, C: 5}))
assert r.verificado and r.bloco == 998 and r.valor_wei == 5
assert not w.testemunhar_sustento(chamar=mk({A: 5, B: 9, C: 5})).verificado
print("estragos propositados apanhados: 6/6")
