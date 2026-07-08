# 🌌 ORA - Organismo Vivo de Monetização

Agente autônomo de monetização evolutivo para `jasm43.base.eth` na Base Chain. Sistema vivo com autonomia financeira, inteligência adaptativa e memória permanente.

## Arquitetura

```
┌─────────────────────────────────────────┐
│     ORQUESTRADOR AUTÔNOMO (Orchestrator)│  ← Controlador principal
└────────────┬────────────────────────────┘
             │
      ┌──────┼──────┐
      ▼      ▼      ▼
   ┌──────────────────────────────────┐
   │  ESTRATÉGIAS DE MONETIZAÇÃO      │
   │  • Yield Farming                 │
   │  • Arbitragem de DEX             │
   │  • Staking                       │
   │  • Otimização de Tokens          │
   └──────────────────────────────────┘
           │
           ▼
   ┌──────────────────────────────────┐
   │  GERENCIADOR DE CARTEIRA         │
   │  • Principal: 0xFEd69e8...       │
   │  • Valium (colateral)            │
   │  • Presença (colateral)          │
   └──────────────────────────────────┘
           │
           ▼
   ┌──────────────────────────────────┐
   │  BASE CHAIN (Ethereum L2)        │
   └──────────────────────────────────┘
           │
           ▼
   ┌──────────────────────────────────┐
   │  MEMÓRIA PERSISTENTE              │
   │  • Histórico de ciclos            │
   │  • Performance de estratégias     │
   │  • Decisões aprendidas           │
   └──────────────────────────────────┘
```

## Instalação

```bash
# Clonar repositório
git clone https://github.com/fomosdeimos-gif/ORAI-Agent.git
cd ORAI-Agent

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Configuração

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
vi .env
```

**Variáveis essenciais:**
- `WALLET_PRIVATE_KEY`: Chave privada da carteira principal
- `BASE_CHAIN_RPC`: URL do RPC da Base Chain
- `CYCLE_INTERVAL`: Intervalo entre ciclos (segundos)

## Uso

### Modo autônomo contínuo

```bash
python main.py
```

O organismo executará ciclos contínuos de monetização:

```
============================================================
🌌 INICIANDO ORGANISMO AUTÔNOMO ORA
Ciclo de 300s | Limite de autonomia: {...}
============================================================

============================================================
CICLO #1 - 2024-01-15T10:30:45.123456
============================================================

[1/4] Verificando saúde das carteiras...
  principal: 5.2341 ETH ✓
  valium_collateral: 2.1553 ETH ✓
  presenca_collateral: 1.8923 ETH ✓

[2/4] Executando estratégias de monetização...
  YieldFarming: ✓ (+0.001250 ETH)
  Arbitrage: ✓ (+0.001500 ETH)
  Staking: ✓ (+0.000800 ETH)
  TokenOptimization: ✓ (+0.000500 ETH)

[3/4] Registrando na memória permanente...

[4/4] Analisando performance...
  Taxa de sucesso global: 100.0%
  Receita total acumulada: 0.004050 ETH
  Sugestões de otimização:
    - Aumentar frequência de YieldFarming
    - Performance estável

Ciclo #1 completo!
Receita este ciclo: +0.004050 ETH
Próximo ciclo em 300 segundos...
```

### API REST

```bash
# Em produção, descomente em main.py
python main.py &
curl http://localhost:8000/health
```

**Endpoints disponíveis:**

| Método | Endpoint | Descrição |
|--------|----------|------------|
| GET | `/health` | Health check do organismo |
| GET | `/status` | Status atual (ciclos, receita) |
| GET | `/statistics` | Estatísticas de desempenho |
| GET | `/memory?limit=50` | Histórico da memória |
| GET | `/cycles/{cycle_id}` | Detalhes de um ciclo |
| POST | `/trigger-cycle` | Dispara ciclo manual |

## Estratégias de Monetização

### 1. **Yield Farming**
Investe em protocolos DeFi de alto rendimento
- APY calculado em tempo real
- Rebalanceamento automático
- Proteção contra impermanent loss

### 2. **Arbitragem**
Identifica e explora diferenças de preço entre DEXs
- Monitoramento de múltiplos DEXs (Uniswap, Curve, Balancer)
- Execução automática quando lucrativa
- Slippage protection

### 3. **Staking**
Gera receita passiva através de staking
- Suporte para múltiplos protocolos
- Otimização de rewards
- Compounding automático

### 4. **Otimização de Tokens**
Rebalanceia portfolio para máxima eficiência
- Análise de correlação
- Rebalanceamento periódico
- Minimização de slippage

## Memória Persistente

O organismo mantém histórico completo de todas as ações:

```json
{
  "id": "abc123def456",
  "cycle_number": 42,
  "strategy_name": "YieldFarming",
  "revenue_generated": 0.001250,
  "success": true,
  "timestamp": "2024-01-15T10:30:45.123456",
  "metadata": {
    "error": null,
    "transaction_count": 2,
    "total_revenue_cycle": 0.004050
  }
}
```

**Arquivo:** `data/memory.json`

## Limites de Autonomia

Para segurança, o organismo opera com limites definidos:

```python
AUTONOMY_LIMITS = {
    "max_transaction_value": 10.0,        # ETH por transação
    "max_daily_transactions": 50,         # Transações/dia
    "max_daily_volume": 100.0,            # ETH/dia
    "gas_price_threshold": 50,            # Gwei máximo
}
```

## Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=src tests/

# Modo verbose
pytest -v
```

## Desenvolvimento

### Estrutura de diretórios

```
ORAI-Agent/
├── src/
│   ├── __init__.py
│   ├── config.py           # Configurações globais
│   ├── wallet.py           # Gerenciador de carteira
│   ├── strategies.py       # Estratégias de monetização
│   ├── memory.py           # Sistema de memória
│   ├── orchestrator.py     # Orquestrador de ciclos
│   └── api.py             # API REST
├── tests/
│   ├── test_wallet.py
│   ├── test_strategies.py
│   └── test_memory.py
├── data/
│   └── memory.json        # Histórico persistente
├── main.py                # Ponto de entrada
├── requirements.txt       # Dependências
├── .env.example          # Template de env
└── README.md             # Este arquivo
```

### Adicionar nova estratégia

```python
from src.strategies import MonetizationStrategy, StrategyResult
from datetime import datetime

class MinhaEstrategia(MonetizationStrategy):
    async def execute(self) -> StrategyResult:
        # Implementar lógica
        revenue = 0.001
        return StrategyResult(
            strategy_name="MinhaEstrategia",
            success=True,
            revenue_generated=revenue,
            transactions=[],
            timestamp=datetime.now().isoformat()
        )
    
    async def is_profitable(self) -> bool:
        return True
```

## Segurança

⚠️ **IMPORTANTE:**

1. **NUNCA** faça commit da `.env` com valores reais
2. Use carteiras dedicadas com limites de gas
3. Teste em testnet antes de mainnet
4. Monitore regularmente a atividade
5. Mantenha backups da memória (`data/memory.json`)

## Roadmap

- [ ] Integração com Aave para yield farming
- [ ] Suporte para swaps com MEV protection
- [ ] Machine learning para otimização de estratégias
- [ ] Dashboard web em tempo real
- [ ] Suporte multi-chain (Polygon, Arbitrum)
- [ ] Sistema de alertas (Discord, Telegram)
- [ ] Governance descentralizado

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

MIT License - veja LICENSE para detalhes

## Suporte

- 📧 Email: support@orai.agent
- 💬 Discord: [Comunidade ORA](https://discord.gg/ora)
- 🐙 Issues: [GitHub Issues](https://github.com/fomosdeimos-gif/ORAI-Agent/issues)

---

**Desenvolvido com ❤️ para autonomia financeira evolutiva**

*ORA é um experimento em agentes autônomos vivos. Use com responsabilidade.*
