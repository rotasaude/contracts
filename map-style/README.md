# map-style — estilo do mapa de campo

O estilo do mapa offline do Rota Saúde (módulo 24c, ADR 0053): o basemap do
Protomaps nos temas `light` e `dark`, com rótulos em português, mais as fontes
(glyphs) e os ícones (sprites) que ele pede. O app de campo e o dashboard
copiam `dist/` e servem tudo de dentro de casa.

**Nenhum serviço de mapa de terceiros.** O estilo não tem nenhuma URL
`http(s)`: o arquivo de mapa, as fontes e os ícones saem do próprio app ou do
próprio Rota Saúde. O teste cobra isso.

## O que tem em `dist/`

| Caminho | O que é |
|---|---|
| `style-light.json`, `style-dark.json` | Estilo MapLibre (`version: 8`), 71 camadas, com três marcadores no lugar dos endereços |
| `manifest.json` | Versão do `@protomaps/basemaps`, commit do `protomaps/basemaps-assets`, temas, pilhas de fonte, sprites e marcadores |
| `fonts/<pilha>/<faixa>.pbf` | As quatro pilhas de fonte, com as 256 faixas de cada uma |
| `fonts/OFL.txt` | Licença das fontes |
| `sprites/{light,dark}{.json,.png,@2x.json,@2x.png}` | Ícones dos dois temas |

### Marcadores

Quem consome troca os três antes de entregar o estilo ao MapLibre:

| Marcador | Onde está | Vira |
|---|---|---|
| `__PMTILES__` | `sources.protomaps.url` | o endereço do arquivo de mapa (`pmtiles://…`) |
| `__GLYPHS__` | `glyphs` (`__GLYPHS__/{fontstack}/{range}.pbf`) | a pasta das fontes |
| `__SPRITE__` | `sprite` (`__SPRITE__/<tema>`) | a pasta dos sprites |

A atribuição `© OpenStreetMap` vem em `sources.protomaps.attribution` e tem de
ficar sempre visível na tela.

### Fontes: as quatro pilhas, todas as faixas

As camadas pedem `Noto Sans Regular`, `Noto Sans Medium`, `Noto Sans Italic` e,
dentro das expressões de `text-field`, `Noto Sans Devanagari Regular v1`. Cada
pilha vem com as 256 faixas (`0-255` até `65280-65535`), em arquivo de verdade.

Isso não é sobra. No MapLibre Native, uma faixa pedida e sem arquivo faz o
mapa desistir de carregar: somem os nomes de rua, os pontos de interesse e até
os prédios (medido no app de campo, com um rótulo `Ω`; Q61 do contrato do
24c). Basta um nome em outro alfabeto num bloco do mapa. Com a faixa presente,
o caractere aparece, ou é pulado quando a fonte não o tem.

No `protomaps/basemaps-assets`, 252 faixas da pilha Devanagari são atalhos
para as da `Noto Sans Regular`; aqui elas são cópias, porque atalho não
sobrevive ao pacote do app nem ao lock por SHA-256.

## Gerar

```bash
cd map-style && npm ci && node build.mjs
```

Grava `dist/style-light.json`, `dist/style-dark.json` e `dist/manifest.json` a
partir do `@protomaps/basemaps` (versão exata em `package.json`) e de
`src/manifest.json`. As fontes e os sprites não são gerados: são cópias do
`protomaps/basemaps-assets` no commit de `src/manifest.json` (`fonts/` e
`sprites/v4/`). O `dist/` é versionado e ninguém o edita à mão.

## Validar

```bash
cd map-style && node --test test/*.test.mjs
```

O teste cobra: nenhuma URL `http(s)`; os três marcadores e a atribuição;
rótulos com `name:pt`; toda pilha pedida pelas camadas no manifesto, com as
256 faixas em arquivo; sprites completos; nenhum arquivo fora do manifesto; e
`dist/` igual à saída do gerador, byte a byte. Tag nenhuma sai com ele
vermelho.

## Consumir

O app copia `map-style/dist` da tag para a sua pasta de cópia e grava um lock
no formato do `tokens.lock`:

```json
{ "ref": "map-style-v1.0.0", "files": { "<caminho>": "<sha256>" } }
```

Um teste do app falha se a cópia divergir do lock. O app de campo copia os
temas `light` e `dark`; o dashboard, só o `light`. As fontes são as mesmas nos
dois temas.

## Licenças

- Estilo: `@protomaps/basemaps` (BSD-3-Clause).
- Fontes Noto Sans: SIL Open Font License 1.1 (`dist/fonts/OFL.txt`).
- Dados do mapa: © OpenStreetMap (ODbL), com a atribuição sempre visível.
