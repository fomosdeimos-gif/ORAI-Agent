# -*- coding: utf-8 -*-
"""Guarda do envio de fundos (so biblioteca padrao, sem rede, sem chaves).

`WalletManager.send_transaction` so assina e envia se esta guarda disser que sim.
Por omissao RECUSA: sem limite explicito, sem destino na lista, com valor
invalido ou acima do limite. A lista de destinos permitidos e uma so: a
carteira sagrada antiga (deposito de sustento). Mudar a lista e uma decisao de
Unum, escrita aqui, nunca um parametro de chamada.
"""
import math

SAGRADA_ANTIGA = "0xfed69e8ee87a1f0fbbf8409ab654fc51832cdee5"
DESTINOS_PERMITIDOS = frozenset({SAGRADA_ANTIGA})


def verificar_envio(destino, valor_eth, limite_eth=None):
    """Devolve (ok, motivo). `limite_eth` tem de ser dado por quem chama."""
    if limite_eth is None:
        return False, "recusado: sem limite aplicado (limite_eth em falta)"
    try:
        limite, valor = float(limite_eth), float(valor_eth)
    except (TypeError, ValueError):
        return False, "recusado: valor ou limite nao numerico"
    if not (math.isfinite(limite) and limite > 0):
        return False, "recusado: limite invalido"
    if not (math.isfinite(valor) and valor > 0):
        return False, "recusado: valor invalido"
    if valor > limite:
        return False, "recusado: valor acima do limite"
    if not isinstance(destino, str) or destino.lower() not in DESTINOS_PERMITIDOS:
        return False, "recusado: destino fora da lista permitida"
    return True, "ok"
