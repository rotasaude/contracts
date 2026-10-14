# Changelog — exams

## Não publicado (antes da tag exams-v1.0.0)

- A45: `consultation_exam_request_id` (uuid | null; preenchido quando
  `origin: consultation`) em `exam-order-v1.json`, obrigatório, nas duas
  visões. O dashboard liga pedido e exame por esse id. Os três exemplos de
  pedido ganharam a chave.

- A42: a visão administrativa do regulador traz `cid10_justification` (o esquema
  já aceitava `string|null`; só a descrição mudou). `requester.cns` segue nulo.
  Novo exemplo `exam-order-administrative-regulator.json`.

## exams-v1.0.0 — 2026-10-13

Primeira versão do domínio (ADR 0036, módulo 21a, rastreamento de exames).

- `exam-order-v1.json` (`rotasaude.exam_order.v1`): o exame como o `api`
  devolve ao dashboard. Esquema fechado, com duas visões do `result` (clínica
  e administrativa); `events` e `result_fields` só no detalhe.
- `fhir-diagnostic-report-inbound.json`
  (`rotasaude.fhir.diagnostic_report_inbound.v1`): perfil mínimo do
  DiagnosticReport FHIR R4 que o prestador envia. Aberto; sistemas de CPF e CNS
  são os uniqueIds da RNDS.
- `examples/`: 7 arquivos (hemograma válido, 3 inválidos do laudo, 2 pedidos) e
  `manifest.json`.
