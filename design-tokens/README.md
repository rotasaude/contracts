# design-tokens — cores, espaçamento, tipografia como dado

> **SCAFFOLD — precisa de input de design.** O `packages/ui` do monorepo foi dissolvido
> aqui (ADR 0025): em vez de componentes compartilhados, cada frontend implementa os seus
> consumindo estes tokens. O conteúdo real (paleta da marca, escala tipográfica,
> espaçamentos) é decisão de design — não inventado pelo agente. Materializar como
> JSON/CSS vars e versionar por `tokens-vX.Y.Z` (ADR 0015) quando o design existir.
