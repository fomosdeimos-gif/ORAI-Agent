"""Gerenciador de carteira multi-nó"""
from web3 import Web3
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class WalletType(Enum):
    """Tipos de carteira no organismo"""
    PRINCIPAL = "principal"
    COLLATERAL_VALIUM = "valium_collateral"
    COLLATERAL_PRESENCA = "presenca_collateral"

@dataclass
class WalletBalance:
    """Informações de saldo de carteira"""
    address: str
    eth_balance: float
    wallet_type: WalletType
    last_updated: str
    is_healthy: bool

class WalletManager:
    """Gerencia múltiplas carteiras do ORA"""
    
    def __init__(self, web3_provider: str, private_key: str):
        """Inicializa gerenciador de carteira"""
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        self.account = self.w3.eth.account.from_key(private_key)
        self.logger = logger
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Falha ao conectar em {web3_provider}")
    
    async def get_balance(self, address: str) -> float:
        """Obtém saldo ETH de um endereço"""
        try:
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            self.logger.info(f"Saldo {address}: {balance_eth} ETH")
            return float(balance_eth)
        except Exception as e:
            self.logger.error(f"Erro ao obter saldo: {e}")
            return 0.0
    
    async def get_all_balances(self, wallet_config: Dict[str, str]) -> List[WalletBalance]:
        """Obtém saldos de todas as carteiras"""
        balances = []
        for wallet_type, address in wallet_config.items():
            balance = await self.get_balance(address)
            wallet_obj = WalletBalance(
                address=address,
                eth_balance=balance,
                wallet_type=WalletType[wallet_type.upper()],
                last_updated=str(__import__('datetime').datetime.now()),
                is_healthy=balance > 0.1  # Mínimo para operações
            )
            balances.append(wallet_obj)
        return balances
    
    async def prepare_transaction(self, to_address: str, amount_eth: float, gas_limit: int = 21000) -> Optional[Dict]:
        """Prepara uma transação sem enviar"""
        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.eth.gas_price
            
            tx = {
                'to': to_address,
                'value': self.w3.to_wei(amount_eth, 'ether'),
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': 8453,
            }
            return tx
        except Exception as e:
            self.logger.error(f"Erro ao preparar transação: {e}")
            return None
    
    async def send_transaction(self, to_address: str, amount_eth: float) -> Optional[str]:
        """Envia transação firmada"""
        try:
            tx = await self.prepare_transaction(to_address, amount_eth)
            if not tx:
                return None
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            self.logger.info(f"Transação enviada: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            self.logger.error(f"Erro ao enviar transação: {e}")
            return None
