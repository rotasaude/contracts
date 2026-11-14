# Changelog — field-sync

## field-sync-v1.2.0 — (não publicada até a tag) — MINOR

App de campo offline (módulo 24c, ADR 0053). Compatível com o v1.1.0: nada do
pedido v1.1.0 passa a ser recusado; nas respostas, os campos novos são emitidos
pelo api no mesmo deploy.

- `session-response-v1.json`: `map` (`{ version, size_bytes, sha256 }` ou
  `null`) e `reference_version`, obrigatórios.
- `upload-request-v1.json`: item `family` (`family_body`: domicílio por
  `household_id` ou `household_client_uuid`, `version` do domicílio,
  `responsible` aninhado); `family_client_uuid` no cadastro individual e na
  visita (no máximo um entre ele e `family_id`); `location` no domicílio
  (objeto ou `null`) e na visita (objeto); `$defs/location` com `accuracy_m`
  obrigatório só com `source: "gps"`.
- `upload-response-v1.json`: `family` nos tipos e no `stale_version` (com o
  `<household>` atual e `id` = o domicílio); `version` obrigatória no
  `accepted` de `household`, `family` e `individual_registration`, opcional no
  `duplicate` desses três e proibida no resto; `location` no `<household>`.
- `changes-response-v1.json`: `location` no `<household>` (obrigatório,
  `null` sem ponto).
- `reference-response-v1.json`: novo — `GET /field/v1/reference` (dicionários
  do cadastro em listas ordenadas, bairros, unidades, profissionais da equipe
  com `has_cns`, domínios da visita e da atividade).
- `domains-v1.json`: `errors.http` com `device_suspended`, `map_not_found`,
  `range_not_satisfiable`, `unknown_city`, `city_suspended` e
  `city_schema_behind`; `errors.item` com `invalid_location` e
  `family_not_found`; chave nova `location` (limites, casas, `sources` e
  `visit_sources`).
- `tools/check_domains.py`: cobre `reference-response-v1.json` nos `$defs` e
  confere `location` contra `domains-v1.json`.
- Exemplos: 124 (49 válidos, 75 inválidos). `invalid-upload-unknown-type.json`
  passa a usar `"type": "visit_sheet"`, porque `family` agora existe.

Pendências da revisão do v1.0.0/v1.1.0 (contracts#2, Q60 do 24c):

- `upload-response-v1.json`: `results` com `minItems: 1` e `candidates`
  obrigatório em `duplicate_suspected`. O api já responde assim; o esquema
  passa a cobrar.
- README: UUID sempre em minúsculas; `note` e `reason` enviados já aparados;
  recusas de forma da retirada (`reason` curta, `visit_client_uuid` e
  `visit_id` juntos ou ausentes) têm `path`; a troca de escopo chega como
  `reset: true`, e `out_of_scope` segue reservado.
- Exemplos dos pares exclusivos que faltavam:
  `invalid-home-visit-two-patients.json` e
  `invalid-registration-two-households.json`.
- Já estavam resolvidos: `cpf_or_reason_required` em `errors.item` e
  `json_required` (o 415) em `errors.http`, desde o v1.0.0; `overdue` com data
  em `changes-last-page.json`.
- Ficam para uma próxima versão, por serem refatorações sem efeito no app:
  candidato discriminado por `type`; `id` do `already_registered` preso ao
  `type`; fusão dos blocos `care_line`; metaesquema no `check.sh`; `expect`
  dizendo a chave que falta; forma de `proof` conferida pelo esquema.

## field-sync-v1.1.0 — 2026-11-13 — MINOR

- `domains-v1.json` (`errors.item`): `too_many_requests` (Q67). O item do envio
  pode voltar `rejected` `too_many_requests`, sem `path`, quando o usuário do
  aparelho estoura o orçamento compartilhado das buscas de pessoa (30 por minuto
  por usuário); não entra no livro de idempotência, e o app reenvia mais tarde.
  Exemplo novo: `upload-response-too-many-requests.json`.

## field-sync-v1.0.0 — 2026-11-12 — MAJOR

Primeira versão do domínio (ADR 0052, módulo 24b): a sincronização do app de
campo offline (24c) com o api.

- `session-response-v1.json`: usuário, profissional (CBO, `has_cns`), equipes
  com as microáreas do escopo do aparelho (`responsible` ou `assigned`),
  interruptores e `min_date`.
- `upload-request-v1.json`: lote de 1 a 50 itens `{ client_uuid, type, body }`
  — `home_visit`, `home_visit_withdrawal`, `collective_activity`, `patient`
  (registro rápido), `household` e `individual_registration` (corpos do 24a,
  com a versão esperada na atualização); `patient_client_uuid` e
  `household_client_uuid` citam um item criado offline (no máximo um entre o id
  e o `client_uuid`).
- `upload-response-v1.json`: um resultado por item — `accepted`, `duplicate`,
  `rejected` (código, `path`, `candidates` em `duplicate_suspected`) e
  `stale_version` (versão atual do domicílio ou do cadastro).
- `changes-response-v1.json`: página do download incremental com
  microáreas, domicílios (famílias e condições de moradia), cadastros,
  remoções, `reset`, "quem visitar" na última página e cursor opaco.
- `domains-v1.json`: domínios da ficha de visita (tipo 8) e de atividade
  coletiva (tipo 6) e as regras cruzadas, em dado.
- Fechados em todo nível, salvo as seções de dicionário do 24a; instantes com
  fuso explícito; CPF nunca desce.
- `domains-v1.json`: `invalid_patient` em `errors.item` (identidade inválida no
  registro rápido; `rejected` no app com `path`, 422 na rota da equipe; Q49).
- `domains-v1.json`: `json_required` em `errors.http` (`415` quando o corpo da
  escrita do app não é JSON; Q59).
- `domains-v1.json` e `upload-response-v1.json`: `internal_error` (exceção
  inesperada; `rejected` sem `path`, fora do livro de idempotência) e
  `household_changed` (cadastro individual novo com domicílio de versão
  vencida; `path` `household_id`) em `errors.item`; `stale_version` só para
  domicílio ou cadastro existente; `id` em `rejected` só com
  `already_registered`, e só no escopo do aparelho (Q63).
- `changes-response-v1.json`: `due_on` de motivo `care_line` com `status: overdue`
  pode ser `null` (prática atrasada nunca feita; o app mostra "nunca feita";
  Q60). `due_soon` e `registration_due` seguem exigindo data.
- `upload-response-v1.json`: `confirmable` (boolean) no resultado, obrigatório em
  `duplicate_participant` e proibido nos outros erros (Q54): `true` = só
  semelhança, o app pode reenviar com `duplicates_reviewed: true` no
  participante; `false` = não há como liberar.
- `examples/`: 86 exemplos (33 válidos, 53 inválidos) e `manifest.json`;
  `tools/`: gerador e verificadores.
- Domínios conferidos com a prova técnica do api (fcf23c87, contrato do 24b
  §10–§11): `proof` preenchido; sem mudança de código nem de faixa; 31 rótulos
  trocados pelos do dicionário oficial (29 dos domínios LEDI e 2 de
  `tipo_de_imovel`, Q39); `outro_procedimento_coletivo` (58 códigos SIGTAP,
  Q37) e `patient_unidentified` (Q41) entram no dado; `rules` ganha
  `without_person_allowed_reasons` (`1 27 28`, Q34/Q40), `male_forbidden_reasons`
  (`5 6`, Q35, no lugar de `reasons_forbidden_for_sex`), `non_residential_reasons`
  (nome do contrato, no lugar de `non_residential_allowed_reasons`),
  `responsible_document_reasons` (Q40, Q43, Q44), `reasons_max` e `list_max`
  (Q36). No esquema: `maxItems` nas listas de `reasons` (36),
  `meeting_topics` (7), `target_audience` (17), `health_topics` (16) e
  `health_practices` (14); `procedure_code` só dos 58 códigos; `altered_count`
  sai do corpo da atividade (derivado pelo api, Q38); `age` de "quem visitar"
  passa a `integer | null` (Q33).
- Q65 (só documentação, nenhum `*-v1.json` mudou): o `status` do cadastro no
  download é um retrato; o app recalcula `valid`/`due_soon`/`expired` na
  exibição a partir de `registered_at` (+ 24 meses; `due_soon` a 60 dias ou
  menos; `expired` a partir do dia do vencimento), regra do 24a. Os demais
  status valem como enviados.
- Q66 (só documentação, nenhum `*-v1.json` mudou): no download, a família cujo
  responsável é paciente provisório da UPA (Q47) fica fora do domicílio, mas
  os outros membros chegam como cadastros e o `family_id` deles aponta para uma
  família que o aparelho nunca recebe. O app tolera: mostra o membro sem
  família, sem falhar e sem criar família provisória.
