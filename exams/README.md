# exams — pedido de exame e laudo FHIR de entrada

Contratos do módulo 21a (rastreamento de exames, ADR 0036). JSON Schema 2020-12.

| Arquivo | O que é |
|---|---|
| `exam-order-v1.json` | `rotasaude.exam_order.v1`: o exame como o `api` devolve ao dashboard. **Fechado** (`additionalProperties: false`). |
| `fhir-diagnostic-report-inbound.json` | `rotasaude.fhir.diagnostic_report_inbound.v1`: perfil mínimo do `DiagnosticReport` FHIR R4 que o prestador envia em `POST /fhir/DiagnosticReport`. **Aberto**. |
| `examples/` | Exemplos válidos e inválidos, listados em `examples/manifest.json`. |

## Regras

- **Perfil aberto, `exam-order` fechado.** O laboratório pode mandar mais do que
  o perfil descreve; o Rota Saúde lê só o que está nele. O pedido que o `api`
  devolve é fechado.
- **Duas visões do `result`.** Clínica (valores, `critical`, `pdf_url`,
  `acknowledged_at`) e administrativa (reduzida: `id`, `origin`, `source`,
  `released_on`, `laboratory_name`). Na administrativa, `requester.cns` vai
  nulo e `cid10_justification` também, exceto para o regulador (`exam_regulator`,
  ou `municipal_admin` na fila de regulação), que o recebe na fila e no detalhe
  (A42). Recepção, unidade e prestador não veem CID nem CNS.
- **`denied_reason` opcional (A47).** Só os itens de `denied` da lista de
  pendentes do solicitante o trazem; as demais formas não têm a chave.
- **Laboratório municipal (v1.1, ADR 0037).** `origin: lab_reception`,
  `source: lab`, `gal_requisition` (número no GAL, ou `null`). Retificação não
  apaga nada: o resultado vigente traz `replaces_result_id`; os substituídos vão em
  `superseded_results` (com `superseded_at`), só na visão clínica do detalhe, e o
  evento é `result_rectified`. O cidadão vê só o vigente.
- **dom-3 fica no `api`.** O esquema não prova que cada `contained[].id` aparece
  em `result`. O `api` recusa com `invalid_resource` (`details: ["/result"]`). O
  exemplo `invalid-diagnostic-report-uncontained-observation.json` é válido
  para o esquema e está marcado `"enforced_by": "api"` no manifesto.
- **Sistemas da RNDS.** CPF `http://rnds.saude.gov.br/fhir/r4/NamingSystem/cpf`,
  CNS `http://rnds.saude.gov.br/fhir/r4/NamingSystem/cns`.
- **Crítico.** `interpretation` com `HH`, `LL` ou `AA`
  (`http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation`) em
  qualquer `Observation` marca o resultado como `critical`.
- **Idempotência** por `identifier` + prestador: reenvio devolve o mesmo
  `result_id`.
- **Transporte:** corpo até 15 MB; só `application/fhir+json`.
- Só `final` e `amended` entram; `preliminary` é recusado pelo esquema.

## Consumo

O `api` copia o perfil FHIR para `config/exams/` e prende o SHA-256 do arquivo
commitado; mudou o esquema, a spec do `api` quebra de propósito. Atualize os dois
lugares no mesmo ciclo, com entrada no CHANGELOG.

## Verificação

A partir da raiz do monorepo, com o compose de pé (usa o `json_schemer` do `api`):

```bash
docker compose run --rm -v "$PWD/contracts:/contracts" -w /rails api bundle exec ruby -rjson -rjson_schemer -e '
m = JSON.parse(File.read("/contracts/exams/examples/manifest.json"))
m["suites"].each do |s|
  schemer = JSONSchemer.schema(JSON.parse(File.read("/contracts/exams/#{s["schema"]}")))
  s["cases"].each do |c|
    errs = schemer.validate(JSON.parse(File.read("/contracts/exams/examples/#{c["file"]}"))).map { |e| "#{e["data_pointer"]} #{e["type"]} #{e.dig("details", "missing_keys")}" }
    puts "#{c["file"]}: #{errs.empty? ? "valid" : errs.uniq.join(" | ")}"
  end
end'
```

Esperado: os cinco pedidos e o hemograma `valid`; `without-pdf` com `required`
`["presentedForm"]` na raiz; `preliminary` com `/status`; `uncontained-observation`
`valid` (o `api` recusa).
