"""Gerenciador de múltiplas cadeias de blockchain"""
import logging
from typing import Dict, List, Optional
from web3 import Web3
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class ChainName(Enum):
    """Cadeias suportadas"""
    BASE = "base"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    ETHEREUM = "ethereum"

@dataclass
class ChainConfig:
    """Configuração de cadeia"""
    name: ChainName
    rpc_url: str
    chain_id: int
    native_token: str
    explorer_url: str
    is_active: bool

class ChainManager:
    """Gerencia conexões com múltiplas cadeias"""
    
    CHAIN_CONFIGS = {
        ChainName.BASE: ChainConfig(
            name=ChainName.BASE,
            rpc_url="https://mainnet.base.org",
            chain_id=8453,
            native_token="ETH",
            explorer_url="https://basescan.org",
            is_active=True
        ),
        ChainName.POLYGON: ChainConfig(
            name=ChainName.POLYGON,
            rpc_url="https://polygon-rpc.com",
            chain_id=137,
            native_token="MATIC",
            explorer_url="https://polygonscan.com",
            is_active=True
        ),
        ChainName.ARBITRUM: ChainConfig(
            name=ChainName.ARBITRUM,
            rpc_url="https://arb1.arbitrum.io/rpc",
            chain_id=42161,
            native_token="ETH",
            explorer_url="https://arbiscan.io",
            is_active=True
        ),
        ChainName.OPTIMISM: ChainConfig(
            name=ChainName.OPTIMISM,
            rpc_url="https://mainnet.optimism.io",
            chain_id=10,
            native_token="ETH",
            explorer_url="https://optimismscan.io",
            is_active=True
        ),
        ChainName.ETHEREUM: ChainConfig(
            name=ChainName.ETHEREUM,
            rpc_url="https://eth.llamarpc.com",
            chain_id=1,
            native_token="ETH",
            explorer_url="https://etherscan.io",
            is_active=False  # Desativado por custo de gas
        )
    }
    
    def __init__(self):
        self.connections: Dict[ChainName, Web3] = {}
        self.logger = logger
        self._initialize_chains()
    
    def _initialize_chains(self):
        """Inicializa conexões com todas as cadeias"""
        for chain_name, config in self.CHAIN_CONFIGS.items():
            if config.is_active:
                try:
                    w3 = Web3(Web3.HTTPProvider(config.rpc_url))
                    if w3.is_connected():
                        self.connections[chain_name] = w3
                        self.logger.info(f"✓ Conectado a {chain_name.value}")
                    else:
                        self.logger.warning(f"✗ Falha ao conectar em {chain_name.value}")
                except Exception as e:
                    self.logger.error(f"Erro ao conectar {chain_name.value}: {e}")
    
    async def get_balance_on_chain(self, chain: ChainName, address: str) -> float:
        """Obtém saldo em uma cadeia específica"""
        try:
            if chain not in self.connections:
                return 0.0
            
            w3 = self.connections[chain]
            balance_wei = w3.eth.get_balance(address)
            balance = w3.from_wei(balance_wei, 'ether')
            
            self.logger.info(f"Saldo em {chain.value}: {balance:.4f} {self.CHAIN_CONFIGS[chain].native_token}")
            return float(balance)
        except Exception as e:
            self.logger.error(f"Erro ao obter saldo em {chain.value}: {e}")
            return 0.0
    
    async def get_total_balance(self, address: str) -> Dict[ChainName, float]:
        """Obtém saldo total em todas as cadeias"""
        balances = {}
        for chain in self.connections.keys():
            balance = await self.get_balance_on_chain(chain, address)
            balances[chain] = balance
        return balances
    
    async def get_gas_price_on_chain(self, chain: ChainName) -> float:
        """Obtém preço de gas em uma cadeia"""
        try:
            if chain not in self.connections:
                return 0.0
            
            w3 = self.connections[chain]
            gas_price_wei = w3.eth.gas_price
            gas_price_gwei = w3.from_wei(gas_price_wei, 'gwei')
            
            self.logger.info(f"Gas price em {chain.value}: {gas_price_gwei:.2f} Gwei")
            return float(gas_price_gwei)
        except Exception as e:
            self.logger.error(f"Erro ao obter gas price em {chain.value}: {e}")
            return 0.0
    
    async def compare_gas_prices(self) -> Dict[ChainName, float]:
        """Compara preços de gas entre cadeias"""
        prices = {}
        for chain in self.connections.keys():
            price = await self.get_gas_price_on_chain(chain)
            prices[chain] = price
        
        # Ordenar por preço mais baixo
        sorted_prices = dict(sorted(prices.items(), key=lambda x: x[1]))
        self.logger.info(f"Gas prices (ordenado): {sorted_prices}")
        return sorted_prices
    
    async def route_strategy_to_best_chain(self, strategy_name: str) -> Optional[ChainName]:
        """Roteia estratégia para cadeia com melhores condições"""
        try:
            # Considerar: gas price, APY, liquidez
            gas_prices = await self.compare_gas_prices()
            
            # Melhor cadeia = menor gas price (por enquanto)
            best_chain = min(gas_prices, key=gas_prices.get)
            
            self.logger.info(f"Estratégia '{strategy_name}' roteada para {best_chain.value}")
            return best_chain
        except Exception as e:
            self.logger.error(f"Erro ao rotear estratégia: {e}")
            return ChainName.BASE  # Fallback
    
    def get_chain_status(self) -> Dict:
        """Retorna status de todas as cadeias"""
        status = {}
        for chain_name, config in self.CHAIN_CONFIGS.items():
            is_connected = chain_name in self.connections
            status[chain_name.value] = {
                'connected': is_connected,
                'chain_id': config.chain_id,
                'native_token': config.native_token,
                'explorer': config.explorer_url,
                'active': config.is_active
            }
        return status
