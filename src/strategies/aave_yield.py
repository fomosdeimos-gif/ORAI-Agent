"""Estratégia de Yield Farming com Aave"""
from src.strategies import MonetizationStrategy, StrategyResult
from src.integrations.aave import AaveIntegration
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AaveYieldStrategy(MonetizationStrategy):
    """Estratégia de Yield Farming via Aave Protocol"""
    
    def __init__(self, name: str, wallet_manager, web3):
        super().__init__(name, wallet_manager)
        self.aave = AaveIntegration(web3, wallet_manager.account.address)
        self.min_deposit = 0.1  # ETH
    
    async def execute(self) -> StrategyResult:
        """Executa estratégia de yield farming"""
        try:
            self.logger.info("🌾 Iniciando Aave Yield Farming")
            
            transactions = []
            total_revenue = 0.0
            
            # 1. Verificar APY
            apy = await self.aave.get_apy_for_asset('0x' + '0' * 40)  # Mock ETH
            self.logger.info(f"APY atual: {apy:.2f}%")
            
            if apy < 2.0:  # Mínimo aceitável
                return StrategyResult(
                    strategy_name="AaveYield",
                    success=False,
                    revenue_generated=0.0,
                    transactions=[],
                    timestamp=datetime.now().isoformat(),
                    error="APY abaixo do mínimo aceitável"
                )
            
            # 2. Depositar se houver oportunidade
            balance = await self.wallet_manager.get_balance(self.wallet_manager.account.address)
            if balance > self.min_deposit:
                amount_to_deposit = balance * 0.5  # Depositar 50%
                amount_wei = self.wallet_manager.w3.to_wei(amount_to_deposit, 'ether')
                
                tx_hash = await self.aave.deposit('0x' + '0' * 40, amount_wei)
                if tx_hash:
                    transactions.append(tx_hash)
                    self.logger.info(f"✓ Depositado {amount_to_deposit:.4f} ETH no Aave")
            
            # 3. Reivindicar e compor rewards
            reward = await self.aave.claim_rewards()
            total_revenue += reward
            transactions.append(f"reward_{reward}")
            
            # 4. Composição automática
            compounded = await self.aave.compound_rewards()
            if compounded:
                total_revenue += reward
            
            stats = self.aave.get_stats()
            self.logger.info(f"📊 Aave Stats: {stats}")
            
            return StrategyResult(
                strategy_name="AaveYield",
                success=True,
                revenue_generated=total_revenue,
                transactions=transactions,
                timestamp=datetime.now().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"Erro em AaveYield: {e}")
            return StrategyResult(
                strategy_name="AaveYield",
                success=False,
                revenue_generated=0.0,
                transactions=[],
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    async def is_profitable(self) -> bool:
        """Verifica se yield farming é lucrativo"""
        try:
            apy = await self.aave.get_apy_for_asset('0x' + '0' * 40)
            gas_cost_apy = 2.0  # Custos estimados de gas
            return apy > gas_cost_apy
        except:
            return False
