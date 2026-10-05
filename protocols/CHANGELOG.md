# Changelog — protocols

## protocols-v1.4.0 — 2026-10-05 — MINOR
- `$defs/condition` ganha `gte` e `lte`, com o mesmo operando de `gt`/`lt`
  (`[operando, valor]`). Valem em todo lugar que usa a condição (`offer`, `suggestions`,
  `priority_when`, regras de `decision_table`): o `api` avalia os dois antes de adotar esta
  versão do schema. "60 anos ou mais" passa a ser `gte`, não `gt 59` (ADR 0027).
- `offer` (opcional, na raiz): o que o catálogo do cidadão mostra e a quem. `title` (1..60),
  `summary` (1..200), `eligibility` (condição) e `retake_after_days` (1..3650), todos
  opcionais; `offer: {}` equivale a não ter o bloco. Parte do conteúdo assinado (ADR 0016).
- `suggestions` (opcional, na raiz, até 10): `{ protocol, when }`, ambos obrigatórios — o
  protocolo que a conclusão desta triagem pode sugerir (`pattern` igual ao do `name`) e a condição para isso.
- O schema não distingue variáveis por lugar: `profile.*` em `offer.eligibility`;
  `profile.*`, `outcome.*` e ids de passo em `suggestions[].when` — quem confere é o gate do
  `api`, assim como "sugestão para o próprio protocolo" e "protocolo inexistente na cidade".
- `examples/` + `examples/manifest.json`: definições válidas e inválidas com o erro esperado,
  verificadas com o `json_schemer` do `api` (comando em `protocols/README.md`).
- Expand: nada vira obrigatório e nada foi removido — toda definição válida em `v1.3.0`
  continua válida, por isso MINOR. O `api` atualiza a cópia (`config/protocols/schema.json`)
  no mesmo ciclo, antes do `dashboard` passar a gravar `offer`/`suggestions`.

## protocols-v1.3.0 — 2026-09-30 — MINOR
- `answer_type: "enum"` passa a exigir `options` com ao menos 1 item (`if`/`then` em
  `$defs/step`, ao lado do `if`/`then` do `analytic`, agora em `allOf`). A regra já estava
  escrita na descrição de `options` ("Obrigatório quando answer_type=enum"), mas o schema não a
  aplicava: uma pergunta `enum` sem opções era aceita e não tinha resposta possível.
- Classificação (ADR 0015): MINOR. Nenhum campo foi removido, renomeado ou mudou de tipo, e
  nenhum protocolo publicado tem `enum` sem `options` — toda definição real válida em `v1.2.0`
  continua válida. É um endurecimento que só recusa definições que já eram inutilizáveis; o
  `api` recusa o rascunho no envio/publicação com o erro do schema.
- O `api` atualiza a cópia (`config/protocols/schema.json`) no mesmo ciclo.

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
