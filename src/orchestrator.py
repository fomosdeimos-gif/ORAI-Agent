"""Orquestrador de ciclos autônomos do ORA"""
import logging
import asyncio
from typing import List, Dict
from datetime import datetime
from src.wallet import WalletManager
from src.strategies import (
    MonetizationStrategy,
    YieldFarmingStrategy,
    ArbitrageStrategy,
    StakingStrategy,
    TokenOptimizationStrategy
)
from src.memory import AutonomousMemory
from src.config import (
    BASE_CHAIN_RPC,
    PRIVATE_KEY,
    WALLET_CONFIG,
    STRATEGIES,
    AUTONOMY_LIMITS,
    CYCLE_INTERVAL
)

logger = logging.getLogger(__name__)

class AutonomousOrchestrator:
    """Orquestra ciclos autônomos de monetização"""
    
    def __init__(self):
        """Inicializa orquestrador"""
        self.wallet_manager = WalletManager(BASE_CHAIN_RPC, PRIVATE_KEY)
        self.memory = AutonomousMemory()
        self.strategies: Dict[str, MonetizationStrategy] = {}
        self.cycle_count = 0
        self.total_revenue = 0.0
        self.logger = logger
        self._setup_strategies()
    
    def _setup_strategies(self):
        """Configura estratégias ativas"""
        if STRATEGIES.get('yield_farming'):
            self.strategies['yield_farming'] = YieldFarmingStrategy(
                'YieldFarming', self.wallet_manager
            )
        if STRATEGIES.get('arbitrage'):
            self.strategies['arbitrage'] = ArbitrageStrategy(
                'Arbitrage', self.wallet_manager
            )
        if STRATEGIES.get('staking'):
            self.strategies['staking'] = StakingStrategy(
                'Staking', self.wallet_manager
            )
        if STRATEGIES.get('token_optimization'):
            self.strategies['token_optimization'] = TokenOptimizationStrategy(
                'TokenOptimization', self.wallet_manager
            )
        
        self.logger.info(f"Estratégias configuradas: {list(self.strategies.keys())}")
    
    async def execute_cycle(self) -> Dict:
        """Executa um ciclo completo de monetização"""
        self.cycle_count += 1
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"CICLO #{self.cycle_count} - {datetime.now().isoformat()}")
        self.logger.info(f"{'='*60}")
        
        cycle_results = {
            'cycle_number': self.cycle_count,
            'timestamp': datetime.now().isoformat(),
            'strategies_executed': [],
            'total_revenue': 0.0,
            'wallet_health': {},
            'errors': []
        }
        
        try:
            # Verificar saúde das carteiras
            self.logger.info("\n[1/4] Verificando saúde das carteiras...")
            balances = await self.wallet_manager.get_all_balances(WALLET_CONFIG)
            for balance in balances:
                self.logger.info(
                    f"  {balance.wallet_type.value}: {balance.eth_balance:.4f} ETH "
                    f"({'✓' if balance.is_healthy else '✗'})"
                )
                cycle_results['wallet_health'][balance.wallet_type.value] = {
                    'balance': balance.eth_balance,
                    'healthy': balance.is_healthy
                }
            
            # Executar estratégias
            self.logger.info("\n[2/4] Executando estratégias de monetização...")
            for strategy_name, strategy in self.strategies.items():
                try:
                    is_profitable = await strategy.is_profitable()
                    if not is_profitable:
                        self.logger.info(f"  {strategy_name}: Não lucrativo no momento")
                        continue
                    
                    result = await strategy.execute()
                    cycle_results['strategies_executed'].append(result.__dict__)
                    cycle_results['total_revenue'] += result.revenue_generated
                    self.total_revenue += result.revenue_generated
                    
                    status = "✓" if result.success else "✗"
                    self.logger.info(
                        f"  {strategy_name}: {status} "
                        f"(+{result.revenue_generated:.6f} ETH)"
                    )
                except Exception as e:
                    error_msg = f"Erro em {strategy_name}: {str(e)}"
                    self.logger.error(f"  {error_msg}")
                    cycle_results['errors'].append(error_msg)
            
            # Registrar na memória
            self.logger.info("\n[3/4] Registrando na memória permanente...")
            self.memory.record_cycle(
                self.cycle_count,
                cycle_results['strategies_executed'],
                cycle_results['total_revenue']
            )
            
            # Análise de performance
            self.logger.info("\n[4/4] Analisando performance...")
            stats = self.memory.get_performance_stats()
            if stats:
                self.logger.info(
                    f"  Taxa de sucesso global: {stats['success_rate']*100:.1f}%"
                )
                self.logger.info(
                    f"  Receita total acumulada: {self.total_revenue:.6f} ETH"
                )
            
            suggestions = self.memory.get_optimization_suggestions()
            if suggestions:
                self.logger.info("  Sugestões de otimização:")
                for suggestion in suggestions:
                    self.logger.info(f"    - {suggestion}")
            
            self.logger.info(f"\nCiclo #{self.cycle_count} completo!")
            self.logger.info(f"Receita este ciclo: +{cycle_results['total_revenue']:.6f} ETH")
            self.logger.info(f"Próximo ciclo em {CYCLE_INTERVAL} segundos...\n")
            
            return cycle_results
        
        except Exception as e:
            error_msg = f"Erro crítico no ciclo: {str(e)}"
            self.logger.error(f"\n{error_msg}")
            cycle_results['errors'].append(error_msg)
            return cycle_results
    
    async def run_autonomous_loop(self, max_cycles: int = None):
        """Executa loop autônomo contínuo"""
        self.logger.info("🤖 INICIANDO ORGANISMO AUTÔNOMO ORA")
        self.logger.info(f"Ciclo de {CYCLE_INTERVAL}s | Limite de autonomia: {AUTONOMY_LIMITS}")
        
        cycle = 0
        try:
            while max_cycles is None or cycle < max_cycles:
                cycle += 1
                await self.execute_cycle()
                await asyncio.sleep(CYCLE_INTERVAL)
        except KeyboardInterrupt:
            self.logger.info("\n🛑 Organismo interrompido pelo usuário")
        except Exception as e:
            self.logger.error(f"Erro fatal: {e}")
    
    def get_status(self) -> Dict:
        """Retorna status atual do organismo"""
        return {
            'cycles_completed': self.cycle_count,
            'total_revenue_eth': self.total_revenue,
            'strategies_active': list(self.strategies.keys()),
            'memory_entries': len(self.memory.memory),
            'wallet_health': {}
        }
