"""Sistema de memória persistente para aprendizado autônomo"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Entrada na memória do organismo"""
    id: str
    cycle_number: int
    strategy_name: str
    revenue_generated: float
    success: bool
    timestamp: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)

class AutonomousMemory:
    """Memória persistente do organismo autônomo"""
    
    def __init__(self, storage_path: str = "data/memory.json"):
        self.storage_path = storage_path
        self.logger = logger
        self.memory: List[MemoryEntry] = []
        self.load_memory()
    
    def load_memory(self):
        """Carrega memória do armazenamento"""
        try:
            import os
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.memory = [
                        MemoryEntry(**entry) for entry in data
                    ]
                self.logger.info(f"Memória carregada: {len(self.memory)} entradas")
            else:
                self.logger.info("Memória vazia - novo ciclo de vida")
                os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        except Exception as e:
            self.logger.error(f"Erro ao carregar memória: {e}")
    
    def save_memory(self):
        """Persiste memória em armazenamento"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(
                    [entry.to_dict() for entry in self.memory],
                    f,
                    indent=2
                )
            self.logger.info(f"Memória persistida: {len(self.memory)} entradas")
        except Exception as e:
            self.logger.error(f"Erro ao persistir memória: {e}")
    
    def record_cycle(self, cycle_number: int, results: List[Dict], total_revenue: float):
        """Registra resultados de um ciclo"""
        for result in results:
            entry_id = hashlib.md5(
                f"{cycle_number}-{result['strategy_name']}-{datetime.now()}".encode()
            ).hexdigest()
            
            entry = MemoryEntry(
                id=entry_id,
                cycle_number=cycle_number,
                strategy_name=result['strategy_name'],
                revenue_generated=result['revenue_generated'],
                success=result['success'],
                timestamp=datetime.now().isoformat(),
                metadata={
                    'error': result.get('error'),
                    'transaction_count': len(result.get('transactions', [])),
                    'total_revenue_cycle': total_revenue
                }
            )
            self.memory.append(entry)
        
        self.save_memory()
        self.logger.info(f"Ciclo {cycle_number} registrado na memória")
    
    def get_performance_stats(self, strategy_name: str = None) -> Dict:
        """Calcula estatísticas de desempenho"""
        filtered = self.memory
        if strategy_name:
            filtered = [e for e in self.memory if e.strategy_name == strategy_name]
        
        if not filtered:
            return {}
        
        total_revenue = sum(e.revenue_generated for e in filtered)
        success_count = sum(1 for e in filtered if e.success)
        total_count = len(filtered)
        
        return {
            'strategy': strategy_name or 'all',
            'total_cycles': total_count,
            'successful': success_count,
            'success_rate': success_count / total_count if total_count > 0 else 0,
            'total_revenue_generated': total_revenue,
            'average_revenue_per_cycle': total_revenue / total_count if total_count > 0 else 0,
        }
    
    def get_optimization_suggestions(self) -> List[str]:
        """Analisa histórico e sugere otimizações"""
        suggestions = []
        
        # Analisar estratégias mais lucrativas
        strategy_revenues = {}
        for entry in self.memory:
            if entry.strategy_name not in strategy_revenues:
                strategy_revenues[entry.strategy_name] = 0
            strategy_revenues[entry.strategy_name] += entry.revenue_generated
        
        # Sugerir focar nas mais lucrativas
        if strategy_revenues:
            best_strategy = max(strategy_revenues, key=strategy_revenues.get)
            suggestions.append(f"Aumentar frequência de {best_strategy}")
        
        # Analisar taxa de sucesso
        for entry in self.memory[-10:]:  # Últimos 10 ciclos
            if not entry.success:
                suggestions.append(f"Revisar {entry.strategy_name} - falhas detectadas")
        
        return suggestions
