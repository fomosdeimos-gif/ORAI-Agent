"""Preditor de APY e condições de mercado"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)

class APYPredictor:
    """Preditor de APY usando séries temporais"""
    
    def __init__(self, historical_apy: List[float]):
        self.historical_apy = historical_apy
        self.logger = logger
        self.model = LinearRegression()
        self._train()
    
    def _train(self):
        """Treina modelo preditivo"""
        if len(self.historical_apy) < 3:
            return
        
        X = np.arange(len(self.historical_apy)).reshape(-1, 1)
        y = np.array(self.historical_apy)
        self.model.fit(X, y)
    
    def predict_apy(self, periods_ahead: int = 24) -> List[float]:
        """Prediz APY para os próximos períodos"""
        try:
            if len(self.historical_apy) < 3:
                return [np.mean(self.historical_apy)] * periods_ahead
            
            predictions = []
            for i in range(periods_ahead):
                X = np.array([[len(self.historical_apy) + i]])
                pred = self.model.predict(X)[0]
                predictions.append(max(0, pred))  # Não permitir APY negativo
            
            return predictions
        
        except Exception as e:
            self.logger.error(f"Erro ao predizer APY: {e}")
            return []
    
    def get_trend(self) -> str:
        """Retorna tendência de APY"""
        if len(self.historical_apy) < 2:
            return "neutral"
        
        recent_change = self.historical_apy[-1] - self.historical_apy[-2]
        if recent_change > 0.5:
            return "up"
        elif recent_change < -0.5:
            return "down"
        else:
            return "neutral"

class MarketConditionAnalyzer:
    """Analisador de condições de mercado"""
    
    def __init__(self):
        self.logger = logger
    
    async def analyze_gas_market(self, gas_history: List[Dict]) -> Dict:
        """Analisa tendências de gas"""
        if not gas_history:
            return {'status': 'unknown'}
        
        try:
            recent_prices = [g['price'] for g in gas_history[-10:]]
            avg = np.mean(recent_prices)
            current = recent_prices[-1]
            
            status = "high" if current > avg * 1.2 else ("low" if current < avg * 0.8 else "normal")
            
            return {
                'status': status,
                'current_price': current,
                'average_price': avg,
                'trend': 'increasing' if current > avg else 'decreasing'
            }
        
        except Exception as e:
            self.logger.error(f"Erro ao analisar mercado de gas: {e}")
            return {'status': 'unknown'}
