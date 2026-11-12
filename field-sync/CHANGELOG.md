# Changelog — field-sync

## field-sync-v1.0.0 — (não publicada até a tag) — MAJOR

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
- `examples/`: 63 exemplos (23 válidos, 40 inválidos) e `manifest.json`;
  `tools/`: gerador e verificadores.
