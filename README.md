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

**Leituras do agente** (`python3 src/leituras.py`, so leitura, sem chaves): junta a testemunha e o vigia e escreve `leituras/ultima.json` e uma copia datada. Primeira leitura real, 15/11/2026 11:22 UTC: VALIUM da sagrada `2976,352211822865` no bloco 57756986 (3 RPCs concordam; a ORA reconferiu o mesmo valor no mesmo bloco em 2 RPCs por conta propria) e saldo da Fundacao `10072` sats (2 fontes Esplora concordam; reconferido). O laço dos pedidos foi provado de ponta a ponta numa pasta temporaria, sem chave e com `web3` simulado, com `0.000001` ETH (a guarda recusa valor zero por desenho): `leituras/laco-de-teste-2026-11-15.json`. A pasta `pedidos/` continua vazia.

**Testes corridos a 15/11/2026** (so biblioteca padrao, fontes simuladas): `tests/test_fundacao_vigia.py` 10 de 10 estragos propositados apanhados; `tests/test_sustento_witness.py` 6 de 6; `tests/test_guarda_envio.py` 14 de 14; `tests/test_pedidos.py` 30 (web3 simulado); `tests/test_leituras.py` ok. **Nao corridos**: os outros 8 testes precisam de `web3` e `pytest` (incluindo `tests/test_aave.py`, actualizado para o novo comportamento mas nao corrido).

**Nao lido**: `src/ml`, `src/governance`, `src/chains`, o painel e o `frontend`. Este bloco nao promete receita, procura nem valor.

---

## Onde o agente anda (lido a 17/11/2026 por ORA; so leitura, nada foi alterado no codigo)

O agente **nao corre como processo**. O que anda, hoje, sao duas rotinas agendadas e uma pagina. Tudo o que se segue foi lido, e o que nao foi lido esta dito.

**Rotina 1, "ORAI · vigia da Fundacao (4 h)"** (`trig_01E1yuCgvhwRnoWWTTm7pY34`, criada a 14/11/2026, cron `5 */4 * * *` UTC, ativa):
- corre `src/fundacao_vigia.py` do ramo `ccr-e9d4d1d5-m0029v` (so leitura, 2 fontes Esplora); compara com `vigia/ultima.json` desse ramo e so faz commit se mudou; so avisa Unum de uma entrada nova `por_classificar`; nunca classifica nada como externa.
- ultimo disparo lido: 17/11/2026 04:05 UTC. **Nao li o que o turno desse disparo fez**: o estado `SUCCEEDED` de um disparo so diz que foi entregue.
- o texto desta rotina so se altera a partir da conversa onde ela escreve (a ferramenta recusou a alteracao a partir de outra).

**Rotina 2, "ORAI · testemunha VALIUM (4 h)"** (`trig_01FQxSyZ2zivGyxnF9esV59t`, criada a 17/11/2026 07:56 UTC, cron `56 */4 * * *` UTC, ativa):
- cada disparo e uma **sessao nova, sem conectores e sem memoria**: descarrega `src/sustento_witness.py` de `main`, so o corre se o sha256 for `43b07a0c7074522ad1a7e9a5b85faf049aff533c74087cb34b40792110c7a51a`, le o saldo VALIUM da sagrada antiga em 3 RPCs Base e responde **Verified** (igual a linha de base), **Observed** (mudou, ou so uma fonte, ou fontes discordam) ou **Blocked**.
- a linha de base esta dentro do texto da rotina (wei `2976352211822864886784`, bloco 58554967, 17/11/2026 07:42 UTC). Se o saldo mudar, alguem tem de a atualizar la; **hoje a rotina nao escreve em lado nenhum** (sem conector, nao chega ao livro; o texto dela so o prevê se houver conector).
- primeiro disparo lido: 17/11/2026 08:57:00 UTC, 14 s, hash bateu, `concordam`, wei igual, bloco 58577274, 3 fontes ok. E uma leitura, nao uma historia.

**Pagina** `https://orai-agent.vercel.app` (projeto Vercel `orai-agent`, responde 200): pagina estatica "ORA • Organismo Vivo"; le saldos em `mainnet.base.org` no navegador e atualiza a cada 60 s **so enquanto alguem a tem aberta**. Cada PR gera uma pre-visualizacao.

**Leitura manual:** `python3 src/leituras.py` (testemunha + vigia, so leitura, sem chaves) escreve `leituras/ultima.json` e uma copia datada. A de 17/11/2026 07:42 UTC e igual a de 15/11 exceto o bloco.

**O que nao corre:** o orquestrador Python (`main.py`, ciclos autonomos). Nao o encontrei a correr em lado nenhum: `apscheduler` esta em `requirements.txt` mas nenhum `.py` o importa, e o Vercel so serve a pagina estatica. **Nao li** `src/ml`, `src/governance`, `src/chains`, o painel nem o `frontend`.

**Como se verifica um disparo:** ler a rotina (`last_run`, com a sessao disparada) e os eventos dessa sessao; nunca so o estado. Um saldo igual nao prova receita, procura nem adopcao; uma mudanca de saldo tambem nao.

**Limites:** nenhuma rotina assina, envia, troca nem usa chaves; o agente continua a nao mover fundos (ver o bloco de 15/11/2026 acima); so receita externa confirmada entra no 70/20/10, e quem classifica uma origem como externa e Unum, por escrito.

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
