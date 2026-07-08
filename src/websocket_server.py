"""Servidor WebSocket para dashboard em tempo real"""
import logging
import asyncio
from typing import Set
from aiohttp import web
import json

logger = logging.getLogger(__name__)

class WebSocketServer:
    """Servidor WebSocket para transmitir atualizações do ORA"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.clients: Set[web.WebSocketResponse] = set()
        self.logger = logger
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura rotas WebSocket"""
        self.app.router.add_get('/ws', self.websocket_handler)
        self.app.router.add_static('/', path='frontend/build', name='static')
    
    async def websocket_handler(self, request):
        """Handler WebSocket"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.clients.add(ws)
        self.logger.info(f"Cliente WebSocket conectado. Total: {len(self.clients)}")
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    # Processar mensagens do cliente
                    await self.handle_client_message(ws, msg.data)
                elif msg.type == web.WSMsgType.ERROR:
                    self.logger.error(f"Erro WebSocket: {ws.exception()}")
        finally:
            self.clients.discard(ws)
            self.logger.info(f"Cliente WebSocket desconectado. Total: {len(self.clients)}")
        
        return ws
    
    async def handle_client_message(self, ws, message: str):
        """Processa mensagens do cliente"""
        try:
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'trigger_cycle':
                # Disparar ciclo manual
                result = await self.orchestrator.execute_cycle()
                await self.broadcast({
                    'type': 'cycle_triggered',
                    'result': result
                })
            elif command == 'get_status':
                status = self.orchestrator.get_status()
                await ws.send_str(json.dumps({
                    'type': 'status',
                    'data': status
                }))
        
        except json.JSONDecodeError:
            self.logger.error("Erro ao decodificar mensagem WebSocket")
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem: {e}")
    
    async def broadcast(self, message: dict):
        """Envia mensagem para todos os clientes"""
        if not self.clients:
            return
        
        msg_json = json.dumps(message)
        for ws in self.clients.copy():
            try:
                await ws.send_str(msg_json)
            except Exception as e:
                self.logger.error(f"Erro ao enviar mensagem: {e}")
                self.clients.discard(ws)
    
    async def broadcast_cycle_complete(self, cycle_result: dict):
        """Notifica todos os clientes quando ciclo completa"""
        await self.broadcast({
            'type': 'cycle_complete',
            'data': cycle_result
        })
    
    async def broadcast_status_update(self, status: dict):
        """Notifica atualização de status"""
        await self.broadcast({
            'type': 'status_update',
            'data': status
        })
    
    def run(self, host: str = '0.0.0.0', port: int = 8000):
        """Inicia servidor WebSocket"""
        self.logger.info(f"🔌 Servidor WebSocket iniciando em {host}:{port}")
        web.run_app(self.app, host=host, port=port)
