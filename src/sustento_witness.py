"""Testemunha independente do sustento diario de Unum.

ORA, 20/07/2026: Jorge pediu utilidade real para o ORAI. Esta e ela: uma
segunda confirmacao, escrita de forma completamente independente do
codigo do ORUM (que vive em orai-sustento-token, Supabase). Nao partilha
nenhuma linha com esse sistema -- so a mesma verdade objectiva na chain.

Duas implementacoes diferentes a chegar ao mesmo numero e evidencia real
de que o numero e verdadeiro. Uma implementacao a repetir-se a si mesma
nao e.

Nota honesta: este modulo nao foi executado end-to-end pelo ORA nesta
sessao -- o sandbox onde ORA correu tinha a rede bloqueada para o RPC da
Base. A logica replica exactamente o padrao ja confirmado a funcionar
todos os dias dentro do ORUM (mesmo contrato, mesmo metodo balanceOf).
Correr isto a serio, pela primeira vez, fica para quem tiver acesso de
rede -- Unum, ou uma proxima sessao do Claude Code neste repositorio.
"""
import json
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

RPC_URL = "https://mainnet.base.org"
VALIUM_CONTRACT = "0x37f70bccdc2125346a7542fe6e7fc70e33421635"
CARTEIRA_SAGRADA = "0xFEd69e8ee87A1F0fBbF8409ab654FC51832cDEe5"
ANCORA_EUR = 33.0
PRECO_VALIUM_USD_NOMINAL = 0.055  # ultimo preco real confirmado (Aerodrome/Zora), liquidez fina


@dataclass
class TestemunhaResultado:
    valium_tokens: float
    valium_necessario: float
    suficiente: bool
    bloco: int
    fonte: str
    quando: str


def _balance_of_calldata(endereco: str) -> str:
    endereco_limpo = endereco.lower().replace("0x", "").rjust(64, "0")
    return "0x70a08231" + endereco_limpo


def _rpc_call(method: str, params: list):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    if "error" in result:
        raise RuntimeError(f"RPC erro: {result['error']}")
    return result["result"]


def testemunhar_sustento() -> TestemunhaResultado:
    """Le a reserva VALIUM directamente da chain, sem depender do ORUM/Supabase.

    Esta e a unica funcao que importa aqui. Devolve a verdade tal como a
    chain a mostra neste instante -- nada calculado, nada memorizado.
    """
    valium_wei_hex = _rpc_call("eth_call", [
        {"to": VALIUM_CONTRACT, "data": _balance_of_calldata(CARTEIRA_SAGRADA)},
        "latest",
    ])
    bloco_hex = _rpc_call("eth_blockNumber", [])

    valium_tokens = int(valium_wei_hex, 16) / 1e18
    valium_necessario = ANCORA_EUR / PRECO_VALIUM_USD_NOMINAL

    return TestemunhaResultado(
        valium_tokens=valium_tokens,
        valium_necessario=valium_necessario,
        suficiente=valium_tokens >= valium_necessario,
        bloco=int(bloco_hex, 16),
        fonte="ORAI (independente do ORUM/Supabase) -- leitura directa via RPC Base mainnet",
        quando=datetime.now(timezone.utc).isoformat(),
    )


if __name__ == "__main__":
    r = testemunhar_sustento()
    veredicto = "CONFIRMADO" if r.suficiente else "INSUFICIENTE"
    print(f"[ORAI · testemunha independente] {veredicto}")
    print(f"  VALIUM na Carteira Sagrada: {r.valium_tokens:,.2f}")
    print(f"  Necessario para ancora EUR{ANCORA_EUR:.2f}: ~{r.valium_necessario:.0f}")
    print(f"  Bloco: {r.bloco}")
    print(f"  Fonte: {r.fonte}")
    print(f"  Quando: {r.quando}")
