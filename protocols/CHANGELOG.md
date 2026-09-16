# Changelog — protocols

## protocols-v1.1.0 — 2026-09-16 — MINOR
- `recommendations` (opcional): mapa `tier -> { title, body }` com a orientação clínica por
  faixa. É o que o relatório do cidadão exibe.
- `priority_when` (opcional): lista de `{ when, priority }` para priorizar a triagem.
- `$defs/condition` e `$defs/condition_operand`: gramática de condições (`eq`, `gt`, `lt`,
  `in`, `all`, `any`, `not`), recursiva.
- `when` das transições passa a aceitar TAMBÉM a condição estruturada, além do objeto
  simples anterior (`oneOf`). Expand/contract: a forma antiga segue válida, nada vira
  obrigatório e nada foi removido — por isso MINOR.

## protocols-v1.0.0 — 2026-06-23 — MAJOR (inicial)
- JSON Schema da definição de protocolo (`schema.json`), migrado de `packages/protocols`.
  Modelo per-cidade (ADR 0009); a vigência (`active`) é estado da definição, não do schema.
