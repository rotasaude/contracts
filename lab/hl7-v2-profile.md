# Perfil HL7 v2.5.1 do laboratório municipal (rotasaude.lab.hl7.v1)

ADR 0037. Porta única para o middleware do fornecedor do reagente. Conferido
contra a HL7 v2.5.1 e o IHE LAW em 2026-10-15 (docs/pesquisa/2026-10-15-laboratorio-provas-tecnicas.md).

## Transporte
- `POST https://<cidade>/hl7/v2`, `Authorization: Bearer <token do middleware>`,
  `Content-Type: application/hl7-v2`. Corpo = UMA mensagem ER7, sem envelope MLLP,
  segmentos separados por `\r` (o Rota Saúde aceita também `\n` e `\r\n`), UTF-8,
  até 1 MB.
- Resposta HTTP 200 com `ACK^R22^ACK` ou `RSP^K11^RSP_K11`
  (`Content-Type: application/hl7-v2; charset=utf-8`).
- Respostas HTTP sem corpo HL7: 401 sem token ou com token desconhecido; 403 com o
  interruptor `lab_hl7_inbound` desligado na cidade; 413 acima de 1 MB; 429 acima de
  120 mensagens/minuto por token. Token **revogado** não é 401: responde `AR`
  `token_revoked` (abaixo).
- Delimitadores só os padrão (`MSH-1` `|`, `MSH-2` `^~\&`); `MSH-12` = `2.5.1`;
  `MSH-9` sempre com os três componentes (`OUL^R22^OUL_R22`, `QBP^Q11^QBP_Q11`).
  Escapes da norma (`\F\ \S\ \T\ \R\ \E\`).
- Códigos locais no sistema `99RSL`.
- Mensagens aceitas: `QBP^Q11` e `OUL^R22`. Qualquer outra (inclusive `OML^O33`,
  fora desta entrega) → `AR` `unsupported_message_type`.

## Mensagens
### Lista de trabalho: QBP^Q11 → RSP^K11
```
MSH|^~\&|<app>|<instalação>|ROTA-SAUDE|<cidade>|<AAAAMMDDhhmmss>||QBP^Q11^QBP_Q11|<id>|P|2.5.1
QPD|LabWorklist^Lista de trabalho^99RSL|<etiqueta>|<código de barras>
RCP|I
```
`QPD-3` = código de barras (parâmetro do usuário).

Resposta com a amostra recebida (`MSH [SFT] MSA [ERR] QAK QPD` + grupo do perfil):
```
MSH|^~\&|ROTA-SAUDE|<cidade>|<app>|<instalação>|<agora>||RSP^K11^RSP_K11|<id>|P|2.5.1
MSA|AA|<MSH-10 da consulta>
QAK|<etiqueta>|OK|LabWorklist^Lista de trabalho^99RSL
QPD|LabWorklist^Lista de trabalho^99RSL|<etiqueta>|<código de barras>
SPM|1|<código de barras>||<material_key>^<rótulo do material>^99RSL|||||||||||||<coleta AAAAMMDDhhmmss>
ORC|NW|<id do item>
OBR|1|<id do item>||<instrument_test_code>^<nome do exame>^99RSL
```
- O grupo de conformidade do `RSP^K11` é o deste perfil: um `SPM` seguido de um par
  `ORC`/`OBR` por exame pendente da amostra (não se usa `RDF`/`RDT`).
- `SPM-4` (tipo do espécime, obrigatório na v2.5.1) = material da versão vigente do
  exame no sistema local: `SPM-4.1` = chave do material (`material_key`), `SPM-4.2` =
  o texto do `material` (rótulo, com os escapes HL7), `SPM-4.3` = `99RSL`. Não se usa
  a tabela HL7 0487. `SPM-17` = coleta.
- `material_key` (B28) é derivada do texto do `material` da versão: translitera (sem
  acento), passa para minúsculas, troca cada sequência de caracteres não
  alfanuméricos por `_` e tira `_` do começo e do fim. Ex.: `Soro` → `soro^Soro^99RSL`;
  `Sangue total (EDTA)` → `sangue_total_edta^Sangue total (EDTA)^99RSL`.
- `ORC-2` e `OBR-2` = id do item da requisição; `OBR-4` = `instrument_test_code`
  da versão vigente do exame.
- Sem `PID`: o Rota Saúde não manda identificação do paciente; o código de barras é a chave.
- `QAK-2` (tabela 0208): `OK` com pendências; `NF` quando a amostra está recebida mas
  não tem exame pendente com código de aparelho (sem `SPM`/`ORC`/`OBR`); `AE` na recusa.
- Recusas (`MSA-1` `AE`, `QAK-2` `AE`, com `ERR` antes do `QAK`): `unknown_barcode`,
  `sample_not_received` (`ERR-2` = `QPD^1^3`).

### Resultado: OUL^R22 → ACK^R22
```
MSH|^~\&|<app>|<instalação>|ROTA-SAUDE|<cidade>|<agora>||OUL^R22^OUL_R22|<id>|P|2.5.1
SPM|1|<código de barras>||<material_key>^<rótulo do material>^99RSL
OBR|1|||<instrument_test_code>^<nome>^99RSL
OBX|1|NM|<analyte_key>^<nome>^99RSL||<valor>|<unidade>^^UCUM|||||F|||<AAAAMMDDhhmmss>
```
- `SPM-2.1` (ou `SPM-2.2`, se o primeiro vier vazio) = código de barras.
- `SPM-4` é obrigatório na v2.5.1: o middleware deve repetir o que recebeu no
  `RSP^K11` (`material_key^rótulo^99RSL`, B28). Na leitura, porém, o Rota Saúde **aceita
  `OUL^R22` sem `SPM-4`** e não confere o valor: a amostra é identificada só pelo
  `SPM-2` (código de barras).
- `OBR-4.1` = `instrument_test_code` da versão vigente do exame (o exame vai no
  `OBR-4`, não no `OBX-3` — Divergência D2).
- `OBX-3.1` = `analyte_key` (`analyte_key^nome^99RSL`); `OBX-2` `NM` (numérico) ou
  `ST`/`CWE` (texto e lista, `OBX-5.1`); `OBX-6.1` deve ser a unidade do componente
  quando vier; `OBX-14` = hora da medição.
- Estrutura: `{ SPM { OBR { OBX } } }`. `OBX` antes do primeiro `OBR` de um `SPM`
  (observação da amostra) é ignorado.
- Vários `SPM`/`OBR`/`OBX` na mesma mensagem: tudo ou nada. A leitura confere a
  mensagem **inteira** e não para na primeira recusa: o `ACK` `AE` traz um `ERR` por
  recusa encontrada, e nada da mensagem é gravado.
- Componente calculado não é aceito (o Rota Saúde calcula).
- Repetição: outro `OUL^R22` com o mesmo componente acrescenta uma linha (nada é sobrescrito).
- Nenhum resultado é liberado sozinho: entra "aguardando conferência".

### Controle: OUL^R22 → ACK^R22 (ADR 0038, módulo 21c)
Resultado de controle interno da qualidade (CIQ) vai na mesma mensagem `OUL^R22`,
num `SPM` próprio. Conferido contra a HL7 v2.5.1 e o IHE LAW em 2026-10-18
(docs/pesquisa/2026-10-18-laboratorio-qualidade-provas-tecnicas.md).
```
MSH|^~\&|<app>|<instalação>|ROTA-SAUDE|<cidade>|<agora>||OUL^R22^OUL_R22|<id>|P|2.5.1
SPM|1|<código de barras do nível>|||||||||Q
OBR|1|||<instrument_test_code>^<nome>^99RSL
OBX|1|NM|<analyte_key>^<nome>^99RSL||<valor>|<unidade>^^UCUM|||||F|||<AAAAMMDDhhmmss>||||<hl7_equipment_id>
```
- **Quem decide que é controle é o `SPM-2`:** código de barras de um nível de lote de
  controle cadastrado no Rota Saúde. O lote, o nível e o material vêm do cadastro.
- `SPM-11` = `Q` (tabela 0369, "Control specimen") é recomendado. `SPM-11` = `Q` com um
  código que não é de controle é recusado (`unknown_barcode`): um controle nunca vira
  resultado de paciente. `SPM-4` é ignorado no controle; `INV` é aceito e ignorado.
- `OBR-4.1` = `instrument_test_code` da versão vigente de um exame ligado ao material.
- `OBX-3.1` = `analyte_key` (um analito do material para aquele exame); `OBX-2` `NM`;
  `OBX-5.1` com **ponto** decimal (até 4 casas); `OBX-6.1`, quando vem, igual à unidade
  do componente.
- **Aparelho em `OBX-18`** (EI, repetível): vale a repetição cuja 1ª parte casa, sem
  diferenciar maiúsculas, com o identificador HL7 do aparelho cadastrado. `EQU` não faz
  parte do `OUL^R22` na 2.5.1.
- Os valores de uma mensagem para o mesmo aparelho ficam na mesma corrida. Cada valor é
  avaliado por Westgard ao entrar; a corrida reprovada **não** muda a resposta (`AA`):
  a reprovação é resultado do CIQ, não erro da mensagem.
- Mensagem inteira ou nada, com as amostras de paciente (B26).

Exemplo: `examples/oul-r22-qc.hl7` (aprovada) e `examples/oul-r22-qc-2-2s.hl7`
(reprovada por 2-2s entre níveis: os dois níveis acima de +2 dp na mesma corrida;
responde `AA`). Recusa: `examples/ack-ae-qc.hl7`.

### ACK
```
MSH|^~\&|ROTA-SAUDE|<cidade>|<app>|<instalação>|<agora>||ACK^R22^ACK|<id>|P|2.5.1
MSA|AA|<MSH-10 recebido>
```
Recusa:
```
MSA|AE|<MSH-10 recebido>
ERR||SPM^1^2|204^Unknown key identifier^HL70357|E|unknown_barcode^Codigo de barras desconhecido^99RSL
```

### ERR (Divergência D1)
- `ERR-2` = local (`segmento^ocorrência^campo`); `ERR-3` = código HL7 da tabela 0357
  (obrigatório); `ERR-4` = severidade (`E`); `ERR-5` = **nosso** código, no sistema `99RSL`.
  O código da aplicação nunca vai em `ERR-3`.
- `ERR` é repetível no `ACK` e no `RSP^K11`: **um `ERR` por recusa**. A leitura do
  `OUL^R22` junta todas as recusas da mensagem (não para na primeira) e a mensagem
  continua entrando inteira ou nada. Ex. (`examples/oul-r22-two-refusals.hl7` →
  `examples/ack-ae-two-errors.hl7`): amostra conhecida e recebida, com o 1º `OBX`
  fora da faixa de digitação e o 2º `OBX` com componente desconhecido em `OBX-3` —
  duas recusas independentes, um `ERR` cada, na ordem dos `OBX`:
  ```
  MSA|AE|<MSH-10 recebido>
  ERR||OBX^1^5|207^Application internal error^HL70357|E|out_of_entry_range^Valor fora da faixa de digitacao^99RSL
  ERR||OBX^2^3|204^Unknown key identifier^HL70357|E|unknown_analyte^Componente desconhecido^99RSL
  ```
  Nenhum dos dois `OBX` é gravado (nem o 2º, nem um eventual `OBX` correto).
  O leitor do Rota Saúde também aceita `ERR` repetido.

## Códigos de recusa (ERR-5, sistema 99RSL) e ERR-3 (tabela 0357)
| ERR-5 | MSA-1 | ERR-3 | ERR-2 |
|---|---|---|---|
| `unknown_barcode` | AE | 204 | `SPM^n^2` ou `QPD^1^3` |
| `sample_not_received` | AE | 207 | `SPM^n^2` ou `QPD^1^3` |
| `exam_not_in_version` | AE | 204 | `OBR^n^4` |
| `unknown_analyte` | AE | 204 | `OBX^n^3` |
| `out_of_entry_range` | AE | 207 | `OBX^n^5` |
| `unit_mismatch` | AE | 207 | `OBX^n^6` |
| `invalid_value` | AE | 102 | `OBX^n^5` |
| `qc_lot_expired` | AE | 207 | `SPM^n^2` |
| `qc_lot_closed` | AE | 207 | `SPM^n^2` |
| `qc_disabled` | AE | 207 | `SPM^n^2` |
| `qc_no_target` | AE | 207 | `OBX^n^3` |
| `unknown_instrument` | AE | 204 | `OBX^n^18` |
| `invalid_message` | AR | 100 | — |
| `unsupported_message_type` | AR | 200 | `MSH^1^9` |
| `unsupported_version` | AR | 203 | `MSH^1^12` |
| `token_revoked` | AR | 207 | — |
| `feature_disabled` | AR | 207 | — |

`feature_disabled` = token do middleware simulado com o interruptor `fake_middleware`
desligado. Com `lab_hl7_inbound` desligado a resposta é HTTP 403 (sem HL7).

`qc_disabled` = controle com o interruptor `lab_quality_control` desligado na cidade. `qc_no_target` = analito do material sem referência vigente para o lote, o nível e o aparelho.

Nunca há dado do paciente em `ERR` nem no `ACK`.

## Idempotência
`MSH-10` já ACEITO (`AA`) do mesmo token → `AA` sem efeito. Mensagem recusada não
é guardada: reenviar com o mesmo `MSH-10` é avaliado de novo. A mensagem bruta
aceita é guardada uma vez, cifrada.

## Exemplos
`examples/*.hl7`, com `\r` real entre os segmentos, listados em
`examples/manifest.json`.
