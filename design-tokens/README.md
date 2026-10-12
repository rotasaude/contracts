# design-tokens — cores, tipografia e espaçamento como dado

O design system do Rota Saúde é compartilhado **como tokens**, não como componentes (ADR 0002, ADR 0025): cada frontend tem os próprios componentes e consome estes tokens.

## Camadas (`src/`)

- `base.json` — paleta crua (nome → hex) e pilhas de fonte.
- `roles.json` — papéis que os componentes leem (`--bg`, `--ink`, `--accent`, `--ok`…), `--on-tone` (texto sobre preenchimento de tom: selos de contagem), apelidos (`--line`, `--danger`, `--surface`), constantes (espaço, raio, sombra), faces de fonte e os pares de contraste.
- `themes/*.json` — cada tema liga cada papel a um nome da paleta.

Temas: `govbr` (padrão: painéis e wpda), `rota` (identidade própria; maintenance e opcional nos painéis), `alto-contraste` (eMAG) e `govbr-escuro` (só wpda).

## Gerar

`node design-tokens/build.mjs` grava `dist/tokens.css` (um bloco `:root[data-theme="…"]` por tema; sem atributo vale o `govbr`) e `dist/tokens.ts` (nomes de tema e de papel). O `dist/` é versionado; nunca edite à mão.

## Validar

`node --test design-tokens/test/*.test.mjs`. O teste de contraste exige texto ≥ 4,5:1, borda e foco ≥ 3:1 e, no `alto-contraste`, tudo ≥ 7:1. Tag nenhuma sai com ele vermelho.

## Consumir

Cada app roda `node scripts/tokens-sync.mjs <tag> --contracts <caminho do clone>`, que copia `design-tokens/dist` da tag para `src/theme/vendor/` e grava `tokens.lock` (tag + SHA-256 por arquivo). Um teste do app falha se a cópia divergir do lock. O app importa `vendor/tokens.css` no `global.css` e escolhe o tema com `data-theme` no `<html>`.

## Fonte

Rawline (SIL OFL 1.1, derivada da Raleway), em `dist/fonts/` com a licença ao lado (`OFL.txt`, que registra a origem: o CDN do Design System gov.br, que não publica arquivo de licença; a OFL foi confirmada por fontes de terceiros). Reserva da pilha: Verdana (recomendação do manual da marca gov.br), depois a fonte do sistema. A Figtree (SIL OFL 1.1, de @fontsource/figtree) é a fonte do tema `rota`, em `dist/fonts/` com `figtree-OFL.txt`.

## Componentes que divergiam entre dashboard e admin

DataTable, KpiGrid, Sparkline, StatTile, PageHeader, BarMini, Panel e AppHeader têm cópias diferentes por **comportamento** (lacunas `null`, supressão de contagem pequena, `asOf`, `right`, fuso), não por estilo: as duas cópias já leem os mesmos papéis. A unificação visual vem destes tokens; a lógica de cada cópia fica no seu app.

## Versão

Tags `tokens-vX.Y.Z` (ADR 0015). Histórico em `CHANGELOG.md`.
