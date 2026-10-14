# Changelog — exams

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
