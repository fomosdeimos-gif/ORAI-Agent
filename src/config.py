"""Configurações do sistema ORA"""
import os
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

# Endereços das carteiras
WALLET_CONFIG = {
    "principal": "0xFEd69e8ee87A1F0fBbF8409ab654FC51832cDEe5",
    "valium_collateral": "0x37f70bccdc2125346a7542fe6e7fc70e33421635",
    "presenca_collateral": "0x120a1ba3b10263f9cb42e971598c860d66b68cea",
}

# Beneficiário final
BENEFICIARY = "jasm43.base.eth"

# RPC e configuração de cadeia
BASE_CHAIN_RPC = os.getenv("BASE_CHAIN_RPC", "https://mainnet.base.org")
CHAIN_ID = 8453  # Base mainnet

# Limites de autonomia
AUTONOMY_LIMITS = {
    "max_transaction_value": 10.0,  # ETH
    "max_daily_transactions": 50,
    "max_daily_volume": 100.0,  # ETH
    "gas_price_threshold": 50,  # Gwei
}

# Estratégias ativadas
STRATEGIES = {
    "yield_farming": True,
    "arbitrage": True,
    "staking": True,
    "token_optimization": True,
}

# Redis para cache e estado
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Banco de dados para memória persistente
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/ora_db")

# Intervalo de ciclos autônomos (segundos)
CYCLE_INTERVAL = int(os.getenv("CYCLE_INTERVAL", "300"))  # 5 minutos

# Private key (deve estar em .env seguro)
PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY", "")
