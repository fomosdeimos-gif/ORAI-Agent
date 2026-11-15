# -*- coding: utf-8 -*-
"""Linha de comandos da supervisao (so biblioteca padrao, sem rede, sem chaves).

  python3 src/supervisao.py rever [pasta]            lista os pedidos e verifica a cadeia
  python3 src/supervisao.py decidir <id> [pasta]     a guarda de envio decide o pedido
Nao assina nem envia nada.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pedidos  # noqa: E402


def main(argv):
    if len(argv) < 2 or argv[1] not in ("rever", "decidir"):
        print(__doc__)
        return 2
    try:
        if argv[1] == "rever":
            pasta = argv[2] if len(argv) > 2 else pedidos.PASTA_PEDIDOS
            print(json.dumps(pedidos.rever(pasta), indent=2, ensure_ascii=False))
        else:
            if len(argv) < 3:
                print(__doc__)
                return 2
            pasta = argv[3] if len(argv) > 3 else pedidos.PASTA_PEDIDOS
            print(json.dumps(pedidos.decidir(pasta, argv[2]), indent=2, ensure_ascii=False))
    except ValueError as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
