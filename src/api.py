"""API REST para monitoramento do ORA"""
import logging
from aiohttp import web
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)

class ORAApi:
    """API REST para exposição de dados do ORA"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura rotas da API"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/status', self.get_status)
        self.app.router.add_get('/statistics', self.get_statistics)
        self.app.router.add_get('/memory', self.get_memory)
        self.app.router.add_get('/cycles/{cycle_id}', self.get_cycle_details)
        self.app.router.add_post('/trigger-cycle', self.trigger_manual_cycle)
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Health check do organismo"""
        return web.json_response({
            'status': 'alive',
            'timestamp': datetime.now().isoformat(),
            'version': '0.1.0'
        })
    
    async def get_status(self, request: web.Request) -> web.Response:
        """Retorna status atual"""
        status = self.orchestrator.get_status()
        return web.json_response(status)
    
    async def get_statistics(self, request: web.Request) -> web.Response:
        """Retorna estatísticas de desempenho"""
        stats = self.orchestrator.memory.get_performance_stats()
        return web.json_response(stats)
    
    async def get_memory(self, request: web.Request) -> web.Response:
        """Retorna entradas da memória"""
        limit = request.query.get('limit', 50)
        memory_data = [
            entry.to_dict() 
            for entry in self.orchestrator.memory.memory[-int(limit):]
        ]
        return web.json_response(memory_data)
    
    async def get_cycle_details(self, request: web.Request) -> web.Response:
        """Retorna detalhes de um ciclo específico"""
        cycle_id = request.match_info['cycle_id']
        cycles = [
            e for e in self.orchestrator.memory.memory 
            if e.cycle_number == int(cycle_id)
        ]
        return web.json_response(
            [e.to_dict() for e in cycles]
        )
    
    async def trigger_manual_cycle(self, request: web.Request) -> web.Response:
        """Dispara ciclo manual (debug)"""
        result = await self.orchestrator.execute_cycle()
        return web.json_response(result)
    
    def run(self, host: str = '0.0.0.0', port: int = 8000):
        """Inicia servidor API"""
        logger.info(f"🌐 API ORA iniciando em {host}:{port}")
        web.run_app(self.app, host=host, port=port)
