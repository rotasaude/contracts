# Changelog — lab

## lab-v1.0.0 — 2026-10-15

Primeira versão do domínio (ADR 0037, módulo 21b, laboratório municipal).

- `lab-report-v1.json` (`rotasaude.lab_report.v1`): JSON canônico do laudo,
  fechado e sem CPF; laboratório com endereço e telefone; responsável técnico e
  liberador com conselho; componentes com `key`; `support_laboratory` (sempre
  `null` no 21b, mas o esquema já aceita o objeto).
- `hl7-v2-profile.md` (`rotasaude.lab.hl7.v1`): perfil HL7 v2.5.1 de
  `QBP^Q11`/`RSP^K11`, `OUL^R22`/`ACK^R22`; nosso código em `ERR-5` (D1);
  componente em `OBX-3` e exame em `OBR-4` (D2); `SPM-4` =
  `material_key^rótulo^99RSL`, opcional na leitura (B25); `ERR` repetível e a
  leitura do `OUL^R22` devolve todas as recusas, mensagem tudo ou nada (B26);
  `QAK-2` `NF` sem pendência.
- `examples/`: 4 laudos válidos (avançada, ICP, retificação, laboratório de
  apoio) e 1 inválido; 10 mensagens ER7 (inclusive `OUL^R22` sem `SPM-4`,
  `OUL^R22` com duas recusas e o `ACK` com dois `ERR`); `manifest.json`.
