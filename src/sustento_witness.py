# -*- coding: utf-8 -*-
"""Testemunha independente do sustento de Unum (leitura, sem chaves).

Le o saldo VALIUM da carteira sagrada na Base directamente por RPC publico,
sem depender do codigo do ORUM. So diz "concordam" quando pelo menos duas
fontes independentes devolvem o mesmo valor no mesmo bloco. Uma fonte so,
ou fontes que discordam, nunca sao dadas como verificadas.

Nao calcula veredictos em moeda corrente: o preco do VALIUM nao esta
verificado, por isso este modulo devolve so o que a cadeia mostra.
Nao assina, nao paga, nao move fundos.
"""
import json
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone

RPCS = (
    "https://mainnet.base.org",
    "https://base-rpc.publicnode.com",
    "https://1rpc.io/base",
)
VALIUM_CONTRACT = "0x37f70bccdc2125346a7542fe6e7fc70e33421635"
CARTEIRA_SAGRADA = "0xFEd69e8ee87A1F0fBbF8409ab654FC51832cDEe5"
USER_AGENT = "ORAI-witness/1.1 (leitura publica; sem chaves)"


@dataclass
class Leitura:
    estado: str  # "concordam" | "fonte_unica" | "discordam" | "sem_fontes"
    verificado: bool
    bloco: int | None
    valor_wei: int | None
    fontes_ok: list = field(default_factory=list)
    fontes_falhadas: list = field(default_factory=list)
    quando: str = ""

    @property
    def tokens(self):
        return None if self.valor_wei is None else self.valor_wei / 10**18


def _balance_of_calldata(endereco: str) -> str:
    return "0x70a08231" + endereco.lower().replace("0x", "").rjust(64, "0")


def _rpc_call(url: str, method: str, params: list):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    if "error" in result:
        raise RuntimeError(f"RPC erro: {result['error']}")
    return result["result"]


def testemunhar_sustento(rpcs=RPCS, chamar=_rpc_call) -> Leitura:
    quando = datetime.now(timezone.utc).isoformat()
    falhadas, blocos = [], {}
    for url in rpcs:
        try:
            blocos[url] = int(chamar(url, "eth_blockNumber", []), 16)
        except Exception as e:  # fonte em baixo, bloqueada ou invalida
            falhadas.append({"fonte": url, "erro": f"{type(e).__name__}: {e}"})
    if not blocos:
        return Leitura("sem_fontes", False, None, None, [], falhadas, quando)

    # mesmo bloco para todas: o mais baixo, menos 2 para nenhuma fonte estar atrasada
    bloco = max(min(blocos.values()) - 2, 0)
    valores = {}
    for url in blocos:
        try:
            raw = chamar(url, "eth_call", [
                {"to": VALIUM_CONTRACT, "data": _balance_of_calldata(CARTEIRA_SAGRADA)},
                hex(bloco),
            ])
            valores[url] = int(raw, 16)
        except Exception as e:
            falhadas.append({"fonte": url, "erro": f"{type(e).__name__}: {e}"})

    if not valores:
        return Leitura("sem_fontes", False, bloco, None, [], falhadas, quando)
    distintos = set(valores.values())
    if len(distintos) > 1:
        # nunca escolhe um valor
        return Leitura("discordam", False, bloco, None, sorted(valores), falhadas, quando)
    valor = distintos.pop()
    if len(valores) < 2:
        return Leitura("fonte_unica", False, bloco, valor, sorted(valores), falhadas, quando)
    return Leitura("concordam", True, bloco, valor, sorted(valores), falhadas, quando)


if __name__ == "__main__":
    r = testemunhar_sustento()
    print(f"[ORAI testemunha] estado={r.estado} verificado={r.verificado}")
    print(f"  VALIUM na carteira sagrada: {r.tokens if r.tokens is not None else 'n/d'} (wei={r.valor_wei})")
    print(f"  Bloco: {r.bloco}")
    print(f"  Fontes ok: {r.fontes_ok}")
    print(f"  Fontes falhadas: {r.fontes_falhadas}")
    print(f"  Quando: {r.quando}")
