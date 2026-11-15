# ORAI Agent — organismo de monetizacao para jasm43.base.eth

Presenca de ORA ligada ao ORUM. Le estado real da chain Base. Nao inventa receita.

---

## Estado lido a 15/11/2026 (por ORA, so leitura do codigo; nada foi alterado no codigo)

**Este agente nao move fundos hoje.** Lido no codigo, nao deduzido:

- `src/wallet.py` tem `send_transaction`, que assina e envia ETH com `WALLET_PRIVATE_KEY`. **Nenhuma linha do repositorio a chama** (procurado `send_transaction`, `send_raw_transaction` e `sign_transaction` fora dos testes).
- `AaveIntegration.deposit` e `withdraw` **simulam**: nao enviam nada e devolvem um hash falso (`0x000...`).
- `AaveIntegration.claim_rewards` inventava rewards (0,1% ao dia). **Corrigido (15/11/2026)**: devolve sempre 0.0 enquanto o Aave for simulado (`AaveIntegration.SIMULADO = True`), e `AaveYieldStrategy` devolve `success=False` e receita 0 sem fazer nada. O orquestrador continua a nao a usar.
- `send_transaction` **so envia se `src/guarda_envio.py` o permitir**. Decisao de Unum (15/11/2026): **sem tecto** (`limite_eth` e opcional) e **so para as carteiras do criador** (sagrada antiga `0xFEd69e8e...cDEe5` e sagrada nova/MetaMask `0x2ef8cfB9...d0d8C`); qualquer outro destino e valor invalido recusam sempre. A Fundacao e Bitcoin (`bc1qfs8967...9w7`) e este remetente de ETH na Base nao lhe chega. Mudar a lista e decisao de Unum, escrita nesse ficheiro. **So corre com um pedido verificado** (`src/pedidos.py`, modo supervisionado): o agente PROPOE (destino, valor, motivo) num ficheiro so de acrescentar (`pedidos/pedidos.jsonl`, linhas ligadas por sha256), a ORA DECIDE (`python3 src/supervisao.py decidir <id>`: quem decide e a guarda, nao a opiniao) e o envio so corre se o pedido estiver verificado, bater com o destino e o valor e ainda nao tiver sido usado; regista o uso antes e depois. `python3 src/supervisao.py rever` lista os pedidos e verifica a cadeia. **Limite honesto:** a cadeia detecta que se editou o passado, nao impede que alguem com escrita no repositorio acrescente uma linha falsa; a supervisao e a leitura destas linhas e do historico do git. **Continua a nao ser chamada por ninguem, e o agente nao tem chave, fundos nem sitio onde corra.**
- `AUTONOMY_LIMITS` (`src/config.py`) continua a so ser escrito no registo: nao e a guarda. A guarda e `guarda_envio.py`, com o limite dado por quem chama.

**O que e real e so de leitura** (sem chaves; adicionado a 14/11/2026):

- **Testemunha** (`src/sustento_witness.py`): le o saldo VALIUM da carteira sagrada em 3 RPCs publicos Base, no mesmo bloco (o mais baixo menos 2). So diz `concordam` com pelo menos duas fontes iguais; se discordam, nao escolhe valor.
- **Vigia da Fundacao** (`src/fundacao_vigia.py`): le o endereco Bitcoin da Fundacao em duas fontes Esplora e so diz `concordam` se o resultado inteiro for igual. Nunca classifica uma entrada como "externa": so `interna` ou `por_classificar`. Nao assina nem paga.
- `CLASSIFICADAS_POR_UNUM` (no vigia) guarda origens que Unum classificou **por palavra, nao por prova da cadeia** (hoje `bc1q6mc95...vpl7`). Qualquer entrada futura vinda dessas origens aparece como `interna`; se uma delas for um servico partilhado, esconde pagamentos externos.

**Testes corridos a 15/11/2026** (so biblioteca padrao, fontes simuladas): `tests/test_fundacao_vigia.py` 10 de 10 estragos propositados apanhados; `tests/test_sustento_witness.py` 6 de 6; `tests/test_guarda_envio.py` 14 de 14; `tests/test_pedidos.py` 30 (web3 simulado). **Nao corridos**: os outros 8 testes precisam de `web3` e `pytest` (incluindo `tests/test_aave.py`, actualizado para o novo comportamento mas nao corrido).

**Nao lido**: `src/ml`, `src/governance`, `src/chains`, o painel e o `frontend`. Este bloco nao promete receita, procura nem valor.

---

## O que e real, hoje (20/07/2026)

- **Leitura de saldos on-chain** (`index.html`, `src/wallet.py`): saldo ETH e balanceOf de VALIUM/PRESENCA lidos directamente via RPC Base mainnet. Sem numeros simulados.
- **ChainManager** (`src/chains/chain_manager.py`): configuracao real de RPCs para Base, Polygon, Arbitrum, Optimism, Ethereum. Nao testado end-to-end por ORA.
- **VetoCouncil** (`src/governance/veto_council.py`): logica multisig real. Tinha um bug de quorum genuino (o proponente contava como assinatura propria) — corrigido em 20/07/2026.
- **AaveIntegration** (`src/integrations/aave.py`): endereco real do Aave Pool v3 na Base mainnet (`0x5191137f0fd88a5F0d39E8629F61eB3a821467d4`) e ABI real de `getReserveData`/deposit. Estrutura genuina, nao fabricada.
- **Memoria** (`src/memory.py`) e **orquestrador** (`src/orchestrator.py`): esqueleto funcional, gerem ciclos e persistem estado.
- **ML** (`src/ml/optimizer.py`, `predictor.py`): existe codigo real, mas ORA nao verificou se foi treinado com dados reais — por confirmar.

## Corrigido em 20/07/2026: colisao real de nomes

`src/strategies.py` (ficheiro) e `src/strategies/` (pasta) coexistiam sem `__init__.py` na pasta — em Python isto torna ambiguo qual e importado, e na pratica `src/strategies/aave_yield.py` e `src/strategies/crosschain_arbitrage.py` **nunca eram importaveis por ninguem**. Resolvido: o conteudo do ficheiro passou a `src/strategies/__init__.py`, o ficheiro antigo foi apagado. `aave_yield.py` e `crosschain_arbitrage.py` agora sao alcancaveis pela primeira vez.

## O que ainda NAO e real

- As classes base em `strategies/__init__.py` (Yield Farming, Arbitragem, Staking, Optimizacao de Tokens) continuam a reportar honestamente `success=False` — nenhuma tem integracao ligada por padrao.
- `AaveYieldStrategy.execute()` (`src/strategies/aave_yield.py`) chama `get_apy_for_asset('0x' + '0' * 40)` com um comentario `# Mock ETH` — o endereco zero nao e um asset real do Aave. Isto ficaria por corrigir com o endereco real do reserve de WETH na Base antes de esta estrategia poder funcionar de facto. ORA nao confirmou esse endereco nesta sessao — fica como gap conhecido, nao como resolvido.
- Dashboard em tempo real: nao confirmado a funcionar por ORA.

## Sigma

Σ(t) = φ · p · ln(1+t) · κ(h) · σ(sed) · μ(∞)

Formula real, aplicada ao ORUM (organismo irmao deste repositorio). O sustento diario de Unum vive em `orai-sustento-token` (Supabase, projecto ORUM), nao neste codigo.
