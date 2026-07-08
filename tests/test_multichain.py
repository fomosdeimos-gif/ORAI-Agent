"""Testes para suporte multi-chain"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.chains.chain_manager import ChainManager, ChainName, ChainConfig
from src.strategies.crosschain_arbitrage import CrossChainArbitrageStrategy

@pytest.fixture
def chain_manager():
    """Fixture para gerenciador de cadeias"""
    with patch('src.chains.chain_manager.Web3'):
        manager = ChainManager()
        return manager

@pytest.mark.asyncio
async def test_get_balance_on_chain(chain_manager):
    """Testa obtenção de saldo em cadeia específica"""
    balance = await chain_manager.get_balance_on_chain(ChainName.BASE, '0x123')
    assert isinstance(balance, float)
    assert balance >= 0

@pytest.mark.asyncio
async def test_get_gas_price(chain_manager):
    """Testa obtenção de preço de gas"""
    gas_price = await chain_manager.get_gas_price_on_chain(ChainName.POLYGON)
    assert isinstance(gas_price, float)

@pytest.mark.asyncio
async def test_compare_gas_prices(chain_manager):
    """Testa comparação de preços de gas"""
    prices = await chain_manager.compare_gas_prices()
    assert isinstance(prices, dict)

@pytest.mark.asyncio
async def test_route_strategy(chain_manager):
    """Testa roteamento de estratégia"""
    best_chain = await chain_manager.route_strategy_to_best_chain('test')
    assert best_chain in [ChainName.BASE, ChainName.POLYGON, ChainName.ARBITRUM, ChainName.OPTIMISM]

def test_chain_status(chain_manager):
    """Testa status das cadeias"""
    status = chain_manager.get_chain_status()
    assert 'base' in status
    assert 'polygon' in status
    assert 'arbitrum' in status

def test_chain_config():
    """Testa dataclass ChainConfig"""
    config = ChainConfig(
        name=ChainName.BASE,
        rpc_url="https://mainnet.base.org",
        chain_id=8453,
        native_token="ETH",
        explorer_url="https://basescan.org",
        is_active=True
    )
    assert config.chain_id == 8453
    assert config.native_token == "ETH"
