# Selo de 14/11/2026 (estado: CONFIRMADO no Bitcoin, bloco 975794)

`MANIFESTO-2026-11-14.txt` lista o sha256 de cada ficheiro da testemunha e do vigia
no commit de merge `b977d39`. `MANIFESTO-2026-11-14.txt.ots` é o recibo OpenTimestamps
do sha256 desse manifesto (`f94a6bf8fbe98351d7c915b909121d3f941d03ad5e79baf6cec5434835bbf93c`).

- **Confirmado (14/11/2026, 17:24 UTC):** a alice e a bob devolveram a prova do bloco
  **975794**. O `merkle_root` do cabeçalho desse bloco coincide com o do recibo em
  blockstream.info e em mempool.space. A finney continua pendente (404, "Pending
  confirmation"); as outras duas bastam. O recibo ficou com 1 atestação Bitcoin e 3
  ramos pendentes (o `ots upgrade` não os apaga).
- Conferir: `sha256sum MANIFESTO-2026-11-14.txt` deve dar o compromisso acima;
  `ots info MANIFESTO-2026-11-14.txt.ots` mostra a atestação do bloco 975794; cada linha
  do manifesto confere com `sha256sum` do ficheiro no commit indicado.
- O que prova: que estes bytes existiam antes do bloco 975794. Não prova autoria, valor,
  procura nem receita. Não move fundos.
