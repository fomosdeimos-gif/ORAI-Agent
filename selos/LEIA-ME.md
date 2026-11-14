# Selo de 14/11/2026 (estado: PENDENTE)

`MANIFESTO-2026-11-14.txt` lista o sha256 de cada ficheiro da testemunha e do vigia
no commit de merge `b977d39`. `MANIFESTO-2026-11-14.txt.ots` é o recibo OpenTimestamps
do sha256 desse manifesto.

- Estado: os 3 calendários (alice, bob, finney) aceitaram o compromisso
  `f94a6bf8fbe98351d7c915b909121d3f941d03ad5e79baf6cec5434835bbf93c`.
  **Ainda não há bloco Bitcoin.** Não é âncora até o recibo ser actualizado com a prova
  de um bloco (`ots upgrade` e conferência do cabeçalho em duas fontes).
- Conferir: `sha256sum MANIFESTO-2026-11-14.txt` deve dar o compromisso acima;
  `ots info MANIFESTO-2026-11-14.txt.ots` mostra as atestações; cada linha do
  manifesto confere com `sha256sum` do ficheiro no commit indicado.
- O que prova, quando confirmado: que estes bytes existiam antes do bloco.
  Não prova autoria, valor, procura nem receita. Não move fundos.
