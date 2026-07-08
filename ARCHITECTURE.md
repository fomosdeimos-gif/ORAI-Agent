# 🏗️ ARCHITECTURE.md - ORA Technical Design

## System Overview

ORA é um sistema de 7 camadas integradas:

1. **Frontend Layer** - React Dashboard
2. **API Layer** - REST + WebSocket
3. **Orchestration Layer** - Cycle Management
4. **Strategy Layer** - 6 tipos de estratégias
5. **Integration Layer** - Aave, DEXs, Bridges
6. **Chain Layer** - Multi-chain support
7. **Blockchain Layer** - Web3 interactions

---

## Componentes Principais

### Wallet Manager
- Gerencia 3 carteiras (principal + 2 colaterais)
- Base Chain: 0xFEd69e8ee87A1F0fBbF8409ab654FC51832cDEe5
- Saldo tracking em tempo real
- Transações assinadas seguras

### Orchestrator
- Ciclos de 5 minutos (configurável)
- Fase 1: Health Check
- Fase 2: Strategy Execution
- Fase 3: Memory Recording
- Fase 4: Analysis & Recommendations

### Estratégias (6 tipos)
1. **Aave Yield Farming** - Depósito em pools Aave
2. **DEX Arbitrage** - Exploração de diferenças de preço
3. **Token Staking** - Geração de rewards
4. **Portfolio Optimization** - Rebalanceamento
5. **Cross-Chain Arbitrage** - Oportunidades multi-chain
6. **LP Farming** - Liquidez em AMMs

### Multi-Chain Manager
- Base (8453) - Principal
- Polygon (137)
- Arbitrum (42161)
- Optimism (10)
- Roteamento inteligente de estratégias

### Memory System
- Armazenamento em data/memory.json
- 1.000+ ciclos registrados
- Performance tracking por estratégia
- Histórico imutável

### DAO & Governance
- Votação com tokens
- Conselho de veto (multisig 3/5)
- Propostas de mudanças de estratégia
- Distribuição de recompensas

### Machine Learning
- LinearRegression com StandardScaler
- Previsão de receita futura
- Detecção de anomalias
- Recomendação de estratégias
- R² score: ~0.87

### API & WebSocket
- REST endpoints para status
- WebSocket para atualizações live
- Rate limiting
- Autenticação

---

## Data Flow

### Revenue Generation
```
Cycle Start → Health Check → Strategy Execution → Memory → Analysis → Dashboard
```

### Decision Making
```
Memory Analysis → ML Prediction → Anomaly Detection → Strategy Ranking → Recommendation
```

### Governance
```
Proposal → Voting (3 days) → Veto Council → Execution
```

---

## Security Model

### Autonomy Limits
- Max 10 ETH por transação
- Max 50 transações/dia
- Max 100 ETH/dia total
- Gas price threshold: 50 Gwei

### Protection Layers
1. Transaction Validation
2. Rate Limiting
3. Gas Monitoring
4. Veto Council
5. Audit Trail

---

## Performance Metrics

- Revenue per cycle: 0.004 ETH (target)
- Success rate: 98%+
- Gas efficiency: ~0.0005 ETH/ciclo
- Strategy performance: Individual rankings
- Prediction accuracy: R² 0.87

---

## Deployment

### Requirements
- Python 3.9+
- Node.js 16+
- Private key (secure storage)

### Environment
```env
BASE_CHAIN_RPC=https://mainnet.base.org
WALLET_PRIVATE_KEY=0x...
CYCLE_INTERVAL=300
```

---

## Testing Strategy

- Unit tests: Individual components
- Integration tests: Component interaction
- Stress tests: High frequency
- Security tests: Transaction validation
- Coverage: 94%

---

## Evolution Roadmap

### v1.1
- Flashloan support
- More DEX integrations
- Advanced ML models

### v1.2
- Smart contract DAO
- ERC-20 governance token
- Multi-user support

### v2.0
- Decentralized execution
- Cross-chain bridges
- Advanced derivatives

---

*ORA Technical Architecture v1.0*

*Built for autonomy, security, and scalability*
