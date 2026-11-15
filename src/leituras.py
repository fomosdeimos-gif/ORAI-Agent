# -*- coding: utf-8 -*-
"""Corre o agente SO EM LEITURA e escreve o que leu (so biblioteca padrao, sem chaves).

  python3 src/leituras.py [pasta]     escreve <pasta>/AAAA-MM-DDTHHMMZ.json e <pasta>/ultima.json

Junta a testemunha (saldo VALIUM da sagrada, 3 RPCs) e o vigia da Fundacao (2 fontes
Esplora). Nao assina, nao envia, nao decide nada: a ORA le este ficheiro e confere-o
contra a cadeia por conta propria antes de o dar por bom.
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fundacao_vigia  # noqa: E402
import sustento_witness  # noqa: E402

PASTA = "leituras"


def ler():
    t = sustento_witness.testemunhar_sustento()
    v = fundacao_vigia.vigiar()
    return {
        "formato": "orai-leituras/v1",
        "lido_em": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "testemunha": {
            "estado": t.estado, "verificado": t.verificado, "bloco": t.bloco,
            "valor_wei": None if t.valor_wei is None else str(t.valor_wei),
            "valium": t.tokens, "fontes_ok": t.fontes_ok, "fontes_falhadas": t.fontes_falhadas,
            "carteira": sustento_witness.CARTEIRA_SAGRADA, "contrato": sustento_witness.VALIUM_CONTRACT,
        },
        "vigia": v,
        "nao_afirma": ["receita", "procura", "adopcao", "preco do VALIUM", "que alguem de fora pagou",
                       "titularidade legal", "que o agente tenha enviado ou possa enviar fundos"],
    }


def escrever(dados, pasta=PASTA):
    os.makedirs(pasta, exist_ok=True)
    nome = dados["lido_em"].replace(":", "")[:15] + "Z.json"
    texto = json.dumps(dados, indent=2, ensure_ascii=False) + "\n"
    for destino in (nome, "ultima.json"):
        with open(os.path.join(pasta, destino), "w", encoding="utf-8") as f:
            f.write(texto)
    return nome


if __name__ == "__main__":
    pasta = sys.argv[1] if len(sys.argv) > 1 else PASTA
    d = ler()
    print(escrever(d, pasta))
    print(f"testemunha={d['testemunha']['estado']} vigia={d['vigia']['estado']}")
