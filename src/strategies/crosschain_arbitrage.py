"""Estratégia de arbitragem cross-chain"""
from src.strategies import MonetizationStrategy, StrategyResult
from src.chains.chain_manager import ChainManager, ChainName
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CrossChainArbitrageStrategy(MonetizationStrategy):
    """Estratégia de arbitragem entre múltiplas cadeias"""
    
    def __init__(self, name: str, wallet_manager):
        super().__init__(name, wallet_manager)
        self.chain_manager = ChainManager()
    
    async def execute(self) -> StrategyResult:
        """Executa arbitragem cross-chain"""
        try:
            self.logger.info("🔀 Iniciando arbitragem cross-chain")
            
            transactions = []
            total_revenue = 0.0
            
            # 1. Comparar preços de gas entre cadeias
            gas_prices = await self.chain_manager.compare_gas_prices()
            cheapest_chain = min(gas_prices, key=gas_prices.get)
            most_expensive_chain = max(gas_prices, key=gas_prices.get)
            
            self.logger.info(f"Cadeia mais barata: {cheapest_chain.value} ({gas_prices[cheapest_chain]:.2f} Gwei)")
            self.logger.info(f"Cadeia mais cara: {most_expensive_chain.value} ({gas_prices[most_expensive_chain]:.2f} Gwei)")
            
            # 2. Simular arbitragem (diferença de preço)
            price_difference = gas_prices[most_expensive_chain] - gas_prices[cheapest_chain]
            if price_difference > 5:  # Threshold de diferença mínima
                # Simular lucro da arbitragem
                revenue = (price_difference / 100) * 0.0001  # Simulado: 0.01% de diferença
                total_revenue += revenue
                transactions.append(f"arbitrage_{cheapest_chain.value}_to_{most_expensive_chain.value}")
                
                self.logger.info(f"✓ Oportunidade de arbitragem detectada: +{revenue:.6f} ETH")
            
            # 3. Rotear para melhor cadeia
            best_chain = await self.chain_manager.route_strategy_to_best_chain('arbitrage')
            self.logger.info(f"Estratégia roteada para: {best_chain.value}")
            
            return StrategyResult(
                strategy_name="CrossChainArbitrage",
                success=True,
                revenue_generated=total_revenue,
                transactions=transactions,
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"Erro em CrossChainArbitrage: {e}")
            return StrategyResult(
                strategy_name="CrossChainArbitrage",
                success=False,
                revenue_generated=0.0,
                transactions=[],
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    async def is_profitable(self) -> bool:
        """Verifica se há oportunidades de arbitragem"""
        try:
            gas_prices = await self.chain_manager.compare_gas_prices()
            price_diff = max(gas_prices.values()) - min(gas_prices.values())
            return price_diff > 5  # Mínimo de 5 Gwei de diferença
        except:
            return False
