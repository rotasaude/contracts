# Changelog — map-style

## map-style-v1.0.0 — 2026-11-14 — MAJOR

Primeira versão do domínio (ADR 0053, módulo 24c): o estilo do mapa offline do
app de campo e do dashboard.

- `dist/style-light.json` e `dist/style-dark.json`: basemap do Protomaps
  (`@protomaps/basemaps` 5.7.2), rótulos em português, com os marcadores
  `__PMTILES__`, `__GLYPHS__` e `__SPRITE__` e a atribuição `© OpenStreetMap`.
- `dist/fonts/`: as quatro pilhas que as camadas pedem (`Noto Sans Regular`,
  `Noto Sans Medium`, `Noto Sans Italic`, `Noto Sans Devanagari Regular v1`),
  com as 256 faixas de cada uma, do `protomaps/basemaps-assets` no commit
  `028c18f`. Faixa sem arquivo faz o MapLibre Native desistir do mapa (Q61).
- `dist/sprites/`: ícones `light` e `dark` (v4), em 1x e 2x.
- `dist/manifest.json`: versões, temas, pilhas, sprites e marcadores.
