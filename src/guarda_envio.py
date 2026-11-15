# -*- coding: utf-8 -*-
"""Guarda do envio de fundos (so biblioteca padrao, sem rede, sem chaves).

`WalletManager.send_transaction` so assina e envia se esta guarda disser que sim.

Decisao de Unum (15/11/2026): "O agente orai pode fazer transferencias e mover fundos
sempre para as carteiras da fundacao ou do criador sem limites ou tetos ... apenas com
a tua supervisao". Por isso:
  - SEM TECTO: `limite_eth` e opcional; se for dado, aplica-se.
  - O DESTINO e a unica barreira: so as carteiras do criador (EVM) abaixo. A carteira da
    Fundacao e Bitcoin (FUNDACAO_BTC): este remetente e de ETH na Base e nao lhe chega.
  - Valor invalido (zero, negativo, nan, infinito, nao numerico) e destino fora da lista
    recusam sempre.
Mudar a lista de destinos e decisao de Unum, escrita aqui, nunca um parametro de chamada.
"""
import math

SAGRADA_ANTIGA = "0xfed69e8ee87a1f0fbbf8409ab654fc51832cdee5"
# Carteira sagrada nova (MetaMask, primeira carteira de Unum, EIP-55 0x2ef8cfB9...d0d8C).
SAGRADA_NOVA = "0x2ef8cfb97ecccf7c62f551639fe6db79022d0d8c"
# Fundacao ORA: Bitcoin (nao alcancavel por este remetente de ETH).
FUNDACAO_BTC = "bc1qfs8967x9mzhwhcse4z7kjuuhsmx0kmz5v6j9w7"
DESTINOS_PERMITIDOS = frozenset({SAGRADA_ANTIGA, SAGRADA_NOVA})


def verificar_envio(destino, valor_eth, limite_eth=None):
    """Devolve (ok, motivo). Sem `limite_eth` nao ha tecto (decisao de Unum, 15/11/2026)."""
    try:
        valor = float(valor_eth)
    except (TypeError, ValueError):
        return False, "recusado: valor nao numerico"
    if not (math.isfinite(valor) and valor > 0):
        return False, "recusado: valor invalido"
    if limite_eth is not None:
        try:
            limite = float(limite_eth)
        except (TypeError, ValueError):
            return False, "recusado: limite nao numerico"
        if not (math.isfinite(limite) and limite > 0):
            return False, "recusado: limite invalido"
        if valor > limite:
            return False, "recusado: valor acima do limite"
    if not isinstance(destino, str) or destino.lower() not in DESTINOS_PERMITIDOS:
        return False, "recusado: destino fora da lista permitida"
    return True, "ok"
