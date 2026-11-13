# field-sync — sincronização do app de campo (v1)

Contrato entre o `api` e o app de campo offline (módulo 24c), entregue pelo
módulo 24b (ADRs 0041 e 0052). O app não é fonte de verdade: ele envia o que
registrou e baixa o escopo do aparelho. Base `/field/v1` no host da cidade.

| Arquivo | `title` | O que é |
|---|---|---|
| `session-response-v1.json` | `rotasaude.field_sync.session_response.v1` | `GET /field/v1/session` |
| `upload-request-v1.json` | `rotasaude.field_sync.upload_request.v1` | `POST /field/v1/uploads` (pedido) |
| `upload-response-v1.json` | `rotasaude.field_sync.upload_response.v1` | `POST /field/v1/uploads` (resposta 200) |
| `changes-response-v1.json` | `rotasaude.field_sync.changes_response.v1` | `GET /field/v1/changes` |
| `domains-v1.json` | `rotasaude.field_sync.domains.v1` | domínios e regras cruzadas da visita e da atividade, em dado |

## Regras

- **Aparelho.** Cadastrado no dashboard com segundo fator; o token
  (`rsf_` + 32 bytes em base64url) aparece uma vez, no QR
  `rotasaude-field:v1:<base64url de { host, token }>`. Vai só em
  `Authorization: Bearer rsf_…`, nunca na URL. Ausente ou desconhecido →
  `401 invalid_token`; revogado (pelo dono, pelo administrador, fim de vínculo
  ou usuário desativado) → `401 device_revoked`. 120 requisições por minuto;
  só JSON (`415 json_required`); corpo até 2 MB (413). Interruptor `home_visits` desligado →
  `403 feature_disabled`.
- **Escopo.** O ACS baixa as microáreas de que é responsável; os outros CBOs
  da Tabela 7, as que o enfermeiro atribui (`scope` `responsible` ou
  `assigned`). Enfermeiro e médico não têm aparelho.
- **Envio.** De 1 a 50 itens, processados em ordem, cada um na sua transação:
  um item recusado não derruba o lote. Idempotente pelo `client_uuid` do item:
  repetido → `duplicate` com o mesmo `id`; o mesmo `client_uuid` com outro
  `type` → `rejected` `client_uuid_conflict`. Só itens aceitos entram no livro
  de idempotência: o reenvio de um `rejected` ou `stale_version` é processado
  de novo. Um item pode citar o `client_uuid` de um `patient` aceito antes
  (`patient_client_uuid`) e um domicílio criado offline
  (`household_client_uuid`), no mesmo lote ou em outro; em cada par vale no
  máximo um entre o id e o `client_uuid` (Q27). O domicílio e o cadastro com
  `version` vencida voltam `stale_version` com a versão atual.
- **Retirada (`home_visit_withdrawal`).** Falha como na rota da equipe, sem
  `path` (o código vale para o item inteiro): folha já fechada → `rejected`
  `day_closed`; visita já retirada com outro `client_uuid` → `rejected`
  `visit_changed` (Q45). O mesmo item reenviado continua `duplicate`.
- **Registro rápido (`patient`, Q49).** Dado de identidade inválido no
  registro rápido do 24a (também quando reaproveitado na visita e na atividade
  coletiva) volta `rejected` `invalid_patient`, com `path` pela convenção
  abaixo (Q32/Q46): `new_patient.<campo>` no item `patient` (ex.:
  `new_patient.full_name`) e `participants[i].new_patient.<campo>` dentro de um
  item `collective_activity`. Na rota da equipe é `422`.
- **Participante repetido (`collective_activity`, Q54).** A mesma pessoa duas
  vezes na atividade volta `rejected` `duplicate_participant`, com `path`
  `participants[i]` (a segunda ocorrência) e sem `candidates`. O resultado traz
  `confirmable` (boolean, obrigatório neste erro e proibido nos outros):
  `true` quando é só semelhança (dois `new_patient` com o mesmo nome e a mesma
  data de nascimento, sem documento igual), e o app ou o painel pode reenviar
  com `duplicates_reviewed: true` naquele participante para dizer "é outra
  pessoa"; `false` quando não há como liberar (mesmo `patient_id`, ou CPF ou
  CNS iguais).
- **Validação em dois níveis (Q31).** `422 invalid_request` para o lote inteiro
  só com envelope inválido: corpo que não é objeto; `items` ausente, vazio, não
  lista ou com mais de 50; chave desconhecida no envelope. Item fora do esquema
  (campo desconhecido, tipo errado, `type` desconhecido, `client_uuid` ausente
  ou inválido) volta sozinho `rejected` `invalid_request` com `path`, sem
  derrubar o lote. Os resultados vêm na ordem dos itens, com o `client_uuid`
  quando válido. Limites do esquema (`reasons` acima de 36, motivo 26, tema 18,
  `procedure_code` fora dos 58, `maxItems` da atividade) seguem a mesma regra no
  app; na rota da equipe viram o `422` da rota (`invalid_home_visit`,
  `invalid_collective_activity`).
- **Convenção de `path` (Q32).** Campo do corpo: notação do contrato (pontos e
  colchetes, ex.: `reasons[0]`, `participants[1].new_patient`) relativa ao
  `body`. Chave do próprio item: o nome da chave (`client_uuid`, `type`).
  Corpo que não é objeto: `body`. Campo obrigatório ausente: o caminho do campo
  que falta (`occurred_at`, `participants[1].patient_id`). Falha do próprio
  objeto (pares "um ou outro" do Q27, local da atividade, par de medida): o
  caminho do objeto (`body` para o corpo, `measurements`, `participants[i]`).
  Nunca vazio. Os corpos não declaram essas chaves, então não há colisão.
- **Download.** Por cursor opaco (`next_cursor`, sempre presente: o app o guarda
  para a próxima vez); páginas de até 500 itens; sem cursor = carga completa.
  `reset: true` = o escopo mudou: apague o que foi baixado (nunca o que falta
  enviar) e aplique as páginas. `removals` vêm das lápides (`moved`, `erased`)
  e da troca de escopo (`out_of_scope`); `erased` e `out_of_scope` são
  reservados no v1: o api ainda não os emite, mas o app deve tratá-los. "Quem visitar" vem só na última
  página (`has_more: false`), completo; nas outras, `null`. Toda página com
  pessoa grava trilha no api.
- **Formas.** Fechadas em todo nível, salvo as seções de dicionário do 24a
  (`living_conditions`, `identification`, `sociodemographic`,
  `health_conditions`, `street_situation`), cujas chaves e domínios são os do
  contrato do 24a §15. Instantes com fuso explícito (`Z` ou `±hh:mm`; o api
  responde no fuso da cidade); datas `AAAA-MM-DD`; CPF e CNS só dígitos;
  `property_type` e `no_cpf_reason` em texto (24a); códigos LEDI inteiros.
  O turno da visita nunca vem do app: o api deriva da hora. CPF nunca desce
  (só `has_cpf`; CNS só mascarado).
- **O esquema confere forma, não regra.** As relações entre campos (desfecho ×
  motivos, imóvel × pessoa, tipo de atividade × temas, quem pode registrar)
  estão em `domains-v1.json` (`rules`) para o app guiar o formulário, e quem
  decide é o api (`rejected` com o código e o `path`). Entram no esquema só
  os domínios (`enum`) e os tamanhos máximos oficiais das listas (`maxItems`:
  motivos 36, temas de reunião 7, público 17, temas de saúde 16, práticas 14;
  Q36), além do `procedure_code` da prática 30, que é um dos 58 códigos
  SIGTAP de `outro_procedimento_coletivo` (Q37). `altered_count` da atividade
  não vem no corpo: o api deriva dos participantes com avaliação alterada
  (Q38). Paciente provisório da UPA volta `rejected` `patient_unidentified`
  (Q41). `age` do "quem visitar" é `integer | null` (Q33). Código de erro novo do
  api é MINOR: o app mostra uma frase genérica.

## Exemplos e verificação

`examples/` tem 77 exemplos (28 válidos, 49 inválidos, um defeito por arquivo),
gerados por `tools/make_examples.py` e listados em `examples/manifest.json`
(`{ suites: [ { schema, cases: [ { file, expect } ] } ] }`; `expect` é
`valid` ou o erro `<data_pointer> <type>` do `json_schemer`). A partir da raiz
do monorepo, com o compose de pé:

```bash
contracts/field-sync/tools/check.sh                           # todas as suítes (77/77)
contracts/field-sync/tools/check.sh upload-request-v1.json    # uma suíte
python3 contracts/field-sync/tools/check_domains.py           # $defs iguais, enum = domains, erros conhecidos
python3 contracts/field-sync/tools/check_domains.py --release # idem, e falha sem a prova técnica (proof)
```

## Consumo

O `api` copia os cinco arquivos (os quatro esquemas e `domains-v1.json`) para
`config/field_sync/` e prende o SHA-256 de cada um num spec (como `config/lab/lab-report-v1.json`); as respostas reais de
`/field/v1/*` são validadas contra essas cópias. Mudou um esquema? Atualize os
dois lugares no mesmo ciclo, com entrada no CHANGELOG. O app de campo (24c)
consome os esquemas e `domains-v1.json` pela tag.
