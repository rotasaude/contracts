# Changelog — lab

## lab-v1.1.0 — 2026-10-18 (não publicada até a tag)

Controle interno da qualidade pela HL7 (ADR 0038, módulo 21c). MINOR: nada do
perfil anterior muda.

- `hl7-v2-profile.md`: seção "Controle" — o controle é reconhecido pelo `SPM-2`
  (código de barras do nível do lote cadastrado); `SPM-11` = `Q` recomendado e
  recusado com código que não é de controle; aparelho em `OBX-18` (sem `EQU`);
  recusas `qc_lot_expired`, `qc_lot_closed`, `qc_disabled`, `qc_no_target`,
  `unknown_instrument`.
- `examples/`: `oul-r22-qc.hl7` (aprovada), `oul-r22-qc-2-2s.hl7` (reprovada por
  2-2s entre níveis, aceita como mensagem) e `ack-ae-qc.hl7`.
- Regras do controle: código de barras do nível `^[A-Za-z0-9._-]{3,30}$` (nunca só 10
  dígitos), `hl7_equipment_id` com até 50 caracteres, valor NM com ponto (até 9 inteiros e
  4 casas; vírgula ou malformado → `invalid_value`).

## lab-v1.0.0 — 2026-10-15

Primeira versão do domínio (ADR 0037, módulo 21b, laboratório municipal).

- `lab-report-v1.json` (`rotasaude.lab_report.v1`): JSON canônico do laudo,
  fechado e sem CPF; laboratório com endereço e telefone; responsável técnico e
  liberador com conselho; componentes com `key`; `support_laboratory` (sempre
  `null` no 21b, mas o esquema já aceita o objeto).
- `hl7-v2-profile.md` (`rotasaude.lab.hl7.v1`): perfil HL7 v2.5.1 de
  `QBP^Q11`/`RSP^K11`, `OUL^R22`/`ACK^R22`; nosso código em `ERR-5` (D1);
  componente em `OBX-3` e exame em `OBR-4` (D2); `SPM-4` =
  `material_key^rótulo^99RSL` com `material_key` derivada do texto do material (B28), opcional na leitura (B25); `ERR` repetível e a
  leitura do `OUL^R22` devolve todas as recusas, mensagem tudo ou nada (B26);
  `QAK-2` `NF` sem pendência.
- `examples/`: 4 laudos válidos (avançada, ICP, retificação, laboratório de
  apoio) e 1 inválido; 10 mensagens ER7 (inclusive `OUL^R22` sem `SPM-4`,
  `OUL^R22` com duas recusas independentes — valor fora da faixa e componente
  desconhecido na mesma amostra — e o `ACK` com dois `ERR`); `manifest.json`.
