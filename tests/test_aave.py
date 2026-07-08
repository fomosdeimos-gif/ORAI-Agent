"""Testes para integração Aave"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.integrations.aave import AaveIntegration, ReserveData
from src.strategies.aave_yield import AaveYieldStrategy

@pytest.fixture
def aave_integration():
    """Fixture para Aave"""
    with patch('src.integrations.aave.Web3'):
        mock_w3 = Mock()
        aave = AaveIntegration(mock_w3, '0x123')
        return aave

@pytest.mark.asyncio
async def test_get_apy(aave_integration):
    """Testa obtenção de APY"""
    apy = await aave_integration.get_apy_for_asset('0x000')
    assert isinstance(apy, float)

@pytest.mark.asyncio
async def test_deposit(aave_integration):
    """Testa depósito"""
    tx_hash = await aave_integration.deposit('0x000', 1000000000000000000)
    assert tx_hash is not None
    assert '0x' in str(tx_hash)

@pytest.mark.asyncio
async def test_withdraw(aave_integration):
    """Testa saque"""
    await aave_integration.deposit('0x000', 1000000000000000000)
    tx_hash = await aave_integration.withdraw('0x000', 500000000000000000)
    assert tx_hash is not None

@pytest.mark.asyncio
async def test_claim_rewards(aave_integration):
    """Testa reivindicação de rewards"""
    aave_integration.active_deposits['0x000'] = 1.0
    reward = await aave_integration.claim_rewards()
    assert reward >= 0.0
    assert aave_integration.accumulated_rewards > 0.0

@pytest.mark.asyncio
async def test_get_stats(aave_integration):
    """Testa estatísticas"""
    aave_integration.active_deposits['0x000'] = 5.0
    aave_integration.accumulated_rewards = 0.1
    stats = aave_integration.get_stats()
    assert stats['total_deposited'] == 5.0
    assert stats['accumulated_rewards'] == 0.1

def test_reserve_data():
    """Testa dataclass ReserveData"""
    data = ReserveData(
        asset='0x000',
        symbol='ETH',
        decimals=18,
        apy=5.5,
        available_liquidity=1000.0,
        total_borrowed=500.0,
        reserve_factor=0.1,
        last_updated='2024-01-01'
    )
    assert data.apy == 5.5
    assert data.symbol == 'ETH'
