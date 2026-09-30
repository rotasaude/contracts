# Changelog — protocols

## protocols-v1.2.0 — 2026-09-30 — MINOR
- `analytic` (opcional, boolean) na pergunta (`$defs/step`): marca a pergunta para o Analytics
  (ADR 0025) — as respostas dela aparecem agregadas por bairro, nunca por pessoa. Só vale `true`
  com `answer_type` `boolean` ou `enum` (`if`/`then` no passo); `integer` e `text` com
  `analytic: true` são recusados. Ausente equivale a `false`.
- A marca é parte da versão do protocolo e passa pelo ciclo assinado (ADR 0016).
- Expand: nada vira obrigatório e nada foi removido — toda definição válida em `v1.1.0` continua
  válida, por isso MINOR. O `api` atualiza a cópia (`config/protocols/schema.json`) no mesmo ciclo,
  antes do `dashboard` passar a gravar a marca.

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
