"""Testes para gerenciador de carteira"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.wallet import WalletManager, WalletBalance, WalletType

@pytest.fixture
def wallet_manager():
    """Fixture para gerenciador de carteira"""
    with patch('src.wallet.Web3'):
        manager = WalletManager('http://localhost:8545', '0x' + '0'*64)
        return manager

@pytest.mark.asyncio
async def test_get_balance(wallet_manager):
    """Testa obtenção de saldo"""
    wallet_manager.w3.from_wei = Mock(return_value=1.5)
    wallet_manager.w3.eth.get_balance = Mock(return_value=1500000000000000000)
    
    balance = await wallet_manager.get_balance('0x123')
    assert balance > 0

@pytest.mark.asyncio
async def test_prepare_transaction(wallet_manager):
    """Testa preparação de transação"""
    wallet_manager.w3.eth.get_transaction_count = Mock(return_value=1)
    wallet_manager.w3.eth.gas_price = 1000000000
    wallet_manager.w3.to_wei = Mock(return_value=1000000000000000000)
    wallet_manager.account.address = '0xabc'
    
    tx = await wallet_manager.prepare_transaction('0x123', 1.0)
    assert tx is not None
    assert 'to' in tx
    assert 'value' in tx

def test_wallet_balance_dataclass():
    """Testa dataclass de saldo"""
    balance = WalletBalance(
        address='0x123',
        eth_balance=1.5,
        wallet_type=WalletType.PRINCIPAL,
        last_updated='2024-01-01',
        is_healthy=True
    )
    assert balance.eth_balance == 1.5
    assert balance.wallet_type == WalletType.PRINCIPAL
