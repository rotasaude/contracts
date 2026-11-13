# Changelog — field-sync

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
- `upload-response-v1.json`: `confirmable` (boolean) no resultado, obrigatório em
  `duplicate_participant` e proibido nos outros erros (Q54): `true` = só
  semelhança, o app pode reenviar com `duplicates_reviewed: true` no
  participante; `false` = não há como liberar.
- `examples/`: 77 exemplos (28 válidos, 49 inválidos) e `manifest.json`;
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
