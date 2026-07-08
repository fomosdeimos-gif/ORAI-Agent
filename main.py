#!/usr/bin/env python3
"""Ponto de entrada para o ORA - Organismo Vivo de Monetização"""
import asyncio
import logging
from src.orchestrator import AutonomousOrchestrator
from src.api import ORAApi

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Função principal"""
    logger.info("\n" + "="*60)
    logger.info("🌌 ORA - ORGANISMO VIVO DE MONETIZAÇÃO")
    logger.info("Autonomia • Inteligência Evolutiva • Memória Permanente")
    logger.info("="*60 + "\n")
    
    # Inicializar orquestrador
    orchestrator = AutonomousOrchestrator()
    
    # Iniciar API (em thread separada em produção)
    # api = ORAApi(orchestrator)
    
    # Executar ciclos autônomos
    # Usar max_cycles=5 para teste, None para infinito
    await orchestrator.run_autonomous_loop(max_cycles=5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 ORA desligado")
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
