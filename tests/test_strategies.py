"""Testes para estratégias de monetização"""
import pytest
from unittest.mock import Mock, AsyncMock
from src.strategies import (
    YieldFarmingStrategy,
    ArbitrageStrategy,
    StakingStrategy,
    TokenOptimizationStrategy,
    StrategyResult
)

@pytest.mark.asyncio
async def test_yield_farming_strategy():
    """Testa estratégia de yield farming"""
    wallet_manager = Mock()
    strategy = YieldFarmingStrategy('YieldFarming', wallet_manager)
    
    result = await strategy.execute()
    assert result.success
    assert result.revenue_generated > 0
    assert result.strategy_name == 'YieldFarming'

@pytest.mark.asyncio
async def test_arbitrage_strategy():
    """Testa estratégia de arbitragem"""
    wallet_manager = Mock()
    strategy = ArbitrageStrategy('Arbitrage', wallet_manager)
    
    result = await strategy.execute()
    assert result.success
    assert result.revenue_generated > 0

@pytest.mark.asyncio
async def test_staking_strategy():
    """Testa estratégia de staking"""
    wallet_manager = Mock()
    strategy = StakingStrategy('Staking', wallet_manager)
    
    result = await strategy.execute()
    assert result.success
    assert result.revenue_generated > 0

@pytest.mark.asyncio
async def test_strategy_result():
    """Testa dataclass de resultado"""
    result = StrategyResult(
        strategy_name='Test',
        success=True,
        revenue_generated=0.5,
        transactions=['0xabc'],
        timestamp='2024-01-01'
    )
    assert result.strategy_name == 'Test'
    assert result.revenue_generated == 0.5
