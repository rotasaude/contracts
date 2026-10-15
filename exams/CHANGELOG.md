# Changelog — exams

## exams-v1.1.0 — 2026-10-15

Laboratório municipal (ADR 0037, módulo 21b). MINOR: só acrescenta. Todo campo
novo é **opcional** no esquema (fora de `required`, aceita `null`; B24), então
documento da v1.0 continua válido; o `api` sempre envia as chaves. Novo exemplo
`exam-order-v1-0-shape.json` (forma da v1.0) no manifesto, como válido.

- `origin`: `lab_reception` (exame criado na recepção do laboratório, pedido em
  papel).
- `source` do `result` (visões clínica e administrativa): `lab`.
- `gal_requisition` (string | null, até 30), opcional: número da requisição no
  GAL. Os exemplos de pedido da v1.0 ganharam a chave (`null`).
- Substituição do resultado (retificação do laudo, B8): `result.replaces_result_id`
  e `superseded_at` (opcionais, visão clínica) e `superseded_results` (opcional,
  só na visão clínica do detalhe). Novo exemplo `exam-order-lab-rectified.json`.
- Evento `result_rectified` em `events[].kind`.

## Não publicado (antes da tag exams-v1.0.0)

- A47: `denied_reason` (string | null) em `exam-order-v1.json`, **opcional**
  (fora de `required`): só os itens de `denied` de
  `GET /exams/acknowledgements/pending` o trazem, com o motivo do evento
  `denied`, ao próprio solicitante (A32). Nunca ao cidadão. Novo exemplo
  `exam-order-denied-pending.json`. (A46, o contador `pending/count`, é rota
  do api sem forma de pedido; não muda este esquema.)

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
