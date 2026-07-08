"""Testes para dashboard"""
import pytest
from unittest.mock import Mock, AsyncMock
from src.websocket_server import WebSocketServer

@pytest.fixture
def mock_orchestrator():
    """Fixture para orquestrador mock"""
    orchestrator = Mock()
    orchestrator.execute_cycle = AsyncMock(return_value={'success': True})
    orchestrator.get_status = Mock(return_value={'cycles_completed': 42})
    return orchestrator

def test_websocket_server_init(mock_orchestrator):
    """Testa inicialização do servidor WebSocket"""
    server = WebSocketServer(mock_orchestrator)
    assert server.orchestrator == mock_orchestrator
    assert len(server.clients) == 0

@pytest.mark.asyncio
async def test_broadcast(mock_orchestrator):
    """Testa broadcast de mensagens"""
    server = WebSocketServer(mock_orchestrator)
    # Adicionar mock de cliente
    mock_client = Mock()
    mock_client.send_str = AsyncMock()
    server.clients.add(mock_client)
    
    await server.broadcast({'type': 'test', 'data': 'hello'})
    mock_client.send_str.assert_called_once()
