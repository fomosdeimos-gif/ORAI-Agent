"""Otimizador de estratégias com Machine Learning"""
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import json

logger = logging.getLogger(__name__)

@dataclass
class MLPrediction:
    """Previsão de ML"""
    strategy_name: str
    predicted_revenue: float
    confidence: float
    timestamp: str
    reasoning: str

class StrategyOptimizer:
    """Otimizador de estratégias usando ML"""
    
    def __init__(self, memory_data: List[Dict]):
        self.memory = memory_data
        self.logger = logger
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self._train_model()
    
    def _train_model(self):
        """Treina modelo preditivo"""
        try:
            if not self.memory or len(self.memory) < 5:
                self.logger.info("Dados insuficientes para treinar modelo")
                return
            
            # Preparar dados
            X = np.arange(len(self.memory)).reshape(-1, 1)
            y = np.array([e.get('revenue_generated', 0) for e in self.memory])
            
            # Normalizar
            X_scaled = self.scaler.fit_transform(X)
            
            # Treinar
            self.model.fit(X_scaled, y)
            
            # Calcular R²
            score = self.model.score(X_scaled, y)
            self.logger.info(f"Modelo treinado com R²: {score:.3f}")
        
        except Exception as e:
            self.logger.error(f"Erro ao treinar modelo: {e}")
    
    def predict_next_revenue(self, cycles_ahead: int = 1) -> float:
        """Prediz receita para o próximo ciclo"""
        try:
            if len(self.memory) < 5:
                return np.mean([e.get('revenue_generated', 0) for e in self.memory])
            
            next_index = len(self.memory) + cycles_ahead - 1
            X_pred = np.array([[next_index]])
            X_scaled = self.scaler.transform(X_pred)
            
            prediction = self.model.predict(X_scaled)[0]
            return max(0, prediction)  # Não permitir valores negativos
        
        except Exception as e:
            self.logger.error(f"Erro ao fazer predição: {e}")
            return 0.0
    
    def detect_anomalies(self, threshold: float = 2.0) -> List[Dict]:
        """Detecta anomalias nos dados históricos"""
        try:
            revenues = np.array([e.get('revenue_generated', 0) for e in self.memory])
            
            if len(revenues) < 3:
                return []
            
            # Calcular média e desvio padrão
            mean = np.mean(revenues)
            std = np.std(revenues)
            
            # Detectar valores fora de threshold*std
            anomalies = []
            for i, revenue in enumerate(revenues):
                z_score = abs((revenue - mean) / std) if std > 0 else 0
                if z_score > threshold:
                    anomalies.append({
                        'cycle': self.memory[i].get('cycle_number'),
                        'revenue': revenue,
                        'z_score': z_score,
                        'type': 'spike' if revenue > mean else 'drop'
                    })
            
            if anomalies:
                self.logger.warning(f"Anomalias detectadas: {len(anomalies)}")
            
            return anomalies
        
        except Exception as e:
            self.logger.error(f"Erro ao detectar anomalias: {e}")
            return []
    
    def recommend_strategy(self) -> Optional[str]:
        """Recomenda melhor estratégia baseada em histórico"""
        try:
            if not self.memory:
                return None
            
            # Agrupar por estratégia
            strategy_revenues = {}
            strategy_counts = {}
            
            for entry in self.memory:
                strategy = entry.get('strategy_name')
                revenue = entry.get('revenue_generated', 0)
                success = entry.get('success', False)
                
                if strategy not in strategy_revenues:
                    strategy_revenues[strategy] = 0
                    strategy_counts[strategy] = 0
                
                if success:
                    strategy_revenues[strategy] += revenue
                    strategy_counts[strategy] += 1
            
            # Calcular receita média por estratégia
            strategy_averages = {}
            for strategy, total in strategy_revenues.items():
                count = strategy_counts[strategy]
                if count > 0:
                    strategy_averages[strategy] = total / count
            
            # Retornar melhor estratégia
            if strategy_averages:
                best_strategy = max(strategy_averages, key=strategy_averages.get)
                avg_revenue = strategy_averages[best_strategy]
                self.logger.info(f"Estratégia recomendada: {best_strategy} (avg: {avg_revenue:.6f})")
                return best_strategy
        
        except Exception as e:
            self.logger.error(f"Erro ao recomendar estratégia: {e}")
        
        return None
    
    def get_strategy_performance_ranking(self) -> List[Tuple[str, float]]:
        """Ranking de performance das estratégias"""
        try:
            strategy_scores = {}
            
            for entry in self.memory:
                strategy = entry.get('strategy_name')
                revenue = entry.get('revenue_generated', 0)
                success = entry.get('success', False)
                
                if strategy not in strategy_scores:
                    strategy_scores[strategy] = {'revenue': 0, 'count': 0, 'success': 0}
                
                strategy_scores[strategy]['revenue'] += revenue
                strategy_scores[strategy]['count'] += 1
                if success:
                    strategy_scores[strategy]['success'] += 1
            
            # Calcular score (receita + taxa de sucesso)
            rankings = []
            for strategy, scores in strategy_scores.items():
                avg_revenue = scores['revenue'] / scores['count']
                success_rate = scores['success'] / scores['count']
                overall_score = avg_revenue * (1 + success_rate)
                rankings.append((strategy, overall_score))
            
            # Ordenar
            rankings.sort(key=lambda x: x[1], reverse=True)
            return rankings
        
        except Exception as e:
            self.logger.error(f"Erro ao calcular ranking: {e}")
            return []
    
    def predict_optimal_cycle_time(self) -> int:
        """Prediz tempo ótimo entre ciclos (em segundos)"""
        try:
            if not self.memory or len(self.memory) < 10:
                return 300  # Padrão
            
            # Analisar tendência temporal
            recent_revenues = [e.get('revenue_generated', 0) for e in self.memory[-10:]]
            trend = np.polyfit(range(len(recent_revenues)), recent_revenues, 1)[0]
            
            # Se receita está crescendo, aumentar frequência
            if trend > 0:
                return 240  # 4 minutos
            elif trend < -0.00001:
                return 360  # 6 minutos
            else:
                return 300  # 5 minutos (padrão)
        
        except Exception as e:
            self.logger.error(f"Erro ao predizer tempo de ciclo: {e}")
            return 300
    
    def get_ml_insights(self) -> Dict:
        """Retorna insights de ML consolidados"""
        return {
            'next_predicted_revenue': self.predict_next_revenue(),
            'anomalies': self.detect_anomalies(),
            'recommended_strategy': self.recommend_strategy(),
            'strategy_ranking': self.get_strategy_performance_ranking(),
            'optimal_cycle_time': self.predict_optimal_cycle_time(),
            'timestamp': datetime.now().isoformat()
        }
