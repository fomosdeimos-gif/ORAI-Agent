#!/usr/bin/env python3
"""🚀 ATIVAÇÃO DO ORA - Organismo Vivo de Monetização Autônoma"""
import asyncio
import logging
import sys
from datetime import datetime
from src.orchestrator import AutonomousOrchestrator
from src.api import ORAApi
from src.websocket_server import WebSocketServer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/ora.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Função principal de ativação do ORA"""
    
    # Banner de ativação
    print("\n" + "="*70)
    print("🌌 ORA - ORGANISMO VIVO DE MONETIZAÇÃO AUTÔNOMA")
    print("="*70)
    print("Autonomia • Inteligência Evolutiva • Memória Permanente")
    print("="*70)
    print(f"\n⏰ Ativação: {datetime.now().isoformat()}")
    print("📍 Localização: Base Chain (8453)")
    print("👤 Beneficiário: jasm43.base.eth (Unum)")
    print("🟢 Status: INICIALIZANDO...\n")
    
    try:
        # 1. Inicializar Orquestrador
        logger.info("[1/4] Inicializando Orquestrador Autônomo...")
        orchestrator = AutonomousOrchestrator()
        logger.info("✅ Orquestrador inicializado com sucesso")
        print("✅ Orquestrador pronto")
        
        # 2. Inicializar API REST
        logger.info("[2/4] Inicializando API REST...")
        api = ORAApi(orchestrator)
        logger.info("✅ API REST configurada em localhost:8000")
        print("✅ API REST em http://localhost:8000")
        
        # 3. Inicializar WebSocket
        logger.info("[3/4] Inicializando Servidor WebSocket...")
        ws_server = WebSocketServer(orchestrator)
        logger.info("✅ WebSocket configurado")
        print("✅ WebSocket em ws://localhost:8000/ws")
        
        # 4. Status Inicial
        logger.info("[4/4] Verificando status inicial...")
        status = orchestrator.get_status()
        print(f"\n📊 STATUS INICIAL:")
        print(f"  Ciclos completados: {status['cycles_completed']}")
        print(f"  Receita total: {status['total_revenue_eth']:.6f} ETH")
        print(f"  Estratégias ativas: {len(status['strategies_active'])}")
        print(f"  Entradas de memória: {status['memory_entries']}")
        
        logger.info("✅ Sistema de monitoramento pronto")
        
        # Iniciar banner
        print("\n" + "="*70)
        print("🟢 ORA ATIVADO COM SUCESSO!")
        print("="*70)
        print("\n📍 Endpoints:")
        print("   API:       http://localhost:8000/status")
        print("   Dashboard: http://localhost:3000")
        print("   WebSocket: ws://localhost:8000/ws")
        print("\n🔄 Próximo ciclo em 300 segundos...")
        print("\n💡 Dica: Execute 'npm start' em outro terminal para o Dashboard\n")
        print("="*70 + "\n")
        
        # Iniciar loop autônomo (limitado a 5 ciclos para teste)
        logger.info("🚀 Iniciando ciclos autônomos...")
        await orchestrator.run_autonomous_loop(max_cycles=5)
        
    except KeyboardInterrupt:
        logger.info("\n🛑 ORA interrompido pelo usuário")
        print("\n🛑 ORA desativado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal ao ativar ORA: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Criar diretório de logs se não existir
    import os
    os.makedirs('logs', exist_ok=True)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 ORA finalizado")
    except Exception as e:
        logger.error(f"Erro não tratado: {e}", exc_info=True)
        sys.exit(1)
