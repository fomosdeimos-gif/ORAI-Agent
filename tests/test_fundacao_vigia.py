# -*- coding: utf-8 -*-
"""Estragos propositados do vigia. Correr: python3 tests/test_fundacao_vigia.py"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import fundacao_vigia as v  # noqa: E402

F1, F2 = v.FONTES
FUN, SAG, EXT = v.FUNDACAO_BTC, "bc1qhcsh78k8jrn3qllvd9al8nq4af4cyzefx6vqqf", "bc1qexterno000000000000000000000000000000"


def tx(txid, origem, valor_in, gasto_de_fundacao=0, confirmada=True):
    vin = [{"prevout": {"scriptpubkey_address": origem, "value": valor_in or gasto_de_fundacao}}]
    vout = [{"scriptpubkey_address": FUN, "value": valor_in}] if valor_in else [{"scriptpubkey_address": EXT, "value": 1}]
    return {"txid": txid, "vin": vin, "vout": vout, "status": {"confirmed": confirmada, "block_height": 1 if confirmada else None}}


def fonte(txs, saldo):
    def f(base, caminho):
        if caminho.endswith("/txs"):
            return txs
        return {"chain_stats": {"funded_txo_sum": saldo, "spent_txo_sum": 0},
                "mempool_stats": {"funded_txo_sum": 0, "spent_txo_sum": 0}}
    return f


def duas(a, b):
    def f(base, caminho):
        return (a if base == F1 else b)(base, caminho)
    return f


ok = fonte([tx("a", EXT, 100)], 100)
r = v.vigiar(obter=duas(ok, ok))
assert r["estado"] == "concordam" and r["verificado"]
assert r["txs"][0]["classe"] == "por_classificar"  # nunca "externa"
assert all(t["classe"] != "externa" for t in r["txs"])
# entrada vinda do proprio organismo e interna
r = v.vigiar(obter=duas(fonte([tx("b", SAG, 100)], 100), fonte([tx("b", SAG, 100)], 100)))
assert r["txs"][0]["classe"] == "interna"
# fontes que discordam: nunca escolhe
r = v.vigiar(obter=duas(fonte([tx("a", EXT, 100)], 100), fonte([tx("a", EXT, 100)], 999)))
assert r["estado"] == "discordam" and not r["verificado"] and "txs" not in r
# uma fonte em baixo: nao verificado
def baixo(base, caminho):
    raise OSError("down")
r = v.vigiar(obter=duas(ok, baixo))
assert r["estado"] == "fonte_unica" and not r["verificado"] and len(r["fontes_falhadas"]) == 1
# todas em baixo
assert v.vigiar(obter=duas(baixo, baixo))["estado"] == "sem_fontes"
# saida nao e receita
r = v.vigiar(obter=duas(fonte([tx("s", FUN, 0, 50)], 0), fonte([tx("s", FUN, 0, 50)], 0)))
assert r["txs"][0]["sentido"] == "saida" and r["txs"][0]["classe"] == "saida"
print("estragos propositados apanhados: 6/6")
