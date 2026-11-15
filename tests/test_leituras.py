# -*- coding: utf-8 -*-
"""Teste do corredor de leitura, com fontes simuladas (sem rede). Correr: python3 tests/test_leituras.py"""
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import leituras as L  # noqa: E402
import sustento_witness as W  # noqa: E402
import fundacao_vigia as V  # noqa: E402

W.testemunhar_sustento = lambda: W.Leitura("concordam", True, 100, 5 * 10**18, ["a", "b"], [], "agora")
V.vigiar = lambda: {"formato": "orai-vigia-fundacao/v1", "estado": "concordam", "verificado": True, "saldo_confirmado": 1}
d = L.ler()
assert d["formato"] == "orai-leituras/v1" and d["testemunha"]["valium"] == 5.0 and d["testemunha"]["valor_wei"] == str(5 * 10**18)
assert d["vigia"]["verificado"] is True and "receita" in d["nao_afirma"]
assert any("enviado" in x for x in d["nao_afirma"]), "tem de dizer que o agente nao envia"
pasta = tempfile.mkdtemp()
nome = L.escrever(d, pasta)
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{4}Z\.json", nome), nome
assert open(os.path.join(pasta, nome)).read() == open(os.path.join(pasta, "ultima.json")).read()
txt = open(os.path.join(pasta, "ultima.json")).read()
assert not re.search(r"0x[0-9a-fA-F]{64}\b", txt), "parece chave privada"
assert json.loads(txt)["testemunha"]["estado"] == "concordam"

# fontes que discordam ou falham nunca viram "verificado"
W.testemunhar_sustento = lambda: W.Leitura("discordam", False, 100, None, ["a"], [], "agora")
d2 = L.ler()
assert d2["testemunha"]["verificado"] is False and d2["testemunha"]["valor_wei"] is None and d2["testemunha"]["valium"] is None
print("leituras: 4 verificacoes e 1 estrago (fontes discordam) apanhados")
