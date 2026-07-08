"""Testes para ML optimization"""
import pytest
import numpy as np
from src.ml.optimizer import StrategyOptimizer, MLPrediction
from src.ml.predictor import APYPredictor, MarketConditionAnalyzer

@pytest.fixture
def mock_memory():
    """Fixture de memória mock"""
    return [
        {'cycle_number': i, 'strategy_name': 'YieldFarming', 'revenue_generated': 0.001 * (i % 3), 'success': True}
        for i in range(20)
    ]

def test_strategy_optimizer(mock_memory):
    """Testa otimizador de estratégias"""
    optimizer = StrategyOptimizer(mock_memory)
    assert optimizer.model is not None

def test_predict_next_revenue(mock_memory):
    """Testa predição de receita"""
    optimizer = StrategyOptimizer(mock_memory)
    prediction = optimizer.predict_next_revenue()
    assert isinstance(prediction, float)
    assert prediction >= 0

def test_detect_anomalies(mock_memory):
    """Testa detecção de anomalias"""
    optimizer = StrategyOptimizer(mock_memory)
    anomalies = optimizer.detect_anomalies()
    assert isinstance(anomalies, list)

def test_recommend_strategy(mock_memory):
    """Testa recomendação de estratégia"""
    optimizer = StrategyOptimizer(mock_memory)
    recommendation = optimizer.recommend_strategy()
    assert recommendation in ['YieldFarming', None]

def test_strategy_ranking(mock_memory):
    """Testa ranking de estratégias"""
    optimizer = StrategyOptimizer(mock_memory)
    ranking = optimizer.get_strategy_performance_ranking()
    assert isinstance(ranking, list)

def test_optimal_cycle_time(mock_memory):
    """Testa predição de tempo de ciclo"""
    optimizer = StrategyOptimizer(mock_memory)
    cycle_time = optimizer.predict_optimal_cycle_time()
    assert isinstance(cycle_time, int)
    assert 200 < cycle_time < 500

def test_ml_insights(mock_memory):
    """Testa consolidação de insights"""
    optimizer = StrategyOptimizer(mock_memory)
    insights = optimizer.get_ml_insights()
    assert 'next_predicted_revenue' in insights
    assert 'recommended_strategy' in insights
    assert 'strategy_ranking' in insights

def test_apy_predictor():
    """Testa preditor de APY"""
    historical = [5.0, 5.2, 5.1, 5.3, 5.4, 5.2]
    predictor = APYPredictor(historical)
    predictions = predictor.predict_apy(periods_ahead=5)
    assert len(predictions) == 5
    assert all(p >= 0 for p in predictions)

def test_apy_trend():
    """Testa detecção de tendência de APY"""
    historical = [5.0, 5.5, 6.0, 6.5]
    predictor = APYPredictor(historical)
    trend = predictor.get_trend()
    assert trend in ['up', 'down', 'neutral']

@pytest.mark.asyncio
async def test_market_analyzer():
    """Testa analisador de condições de mercado"""
    analyzer = MarketConditionAnalyzer()
    gas_history = [{'price': 50 + i} for i in range(10)]
    result = await analyzer.analyze_gas_market(gas_history)
    assert 'status' in result
    assert result['status'] in ['high', 'low', 'normal', 'unknown']
