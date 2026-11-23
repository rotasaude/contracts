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
| `reference-response-v1.json` | `rotasaude.field_sync.reference_response.v1` | `GET /field/v1/reference` (v1.2.0) |
| `domains-v1.json` | `rotasaude.field_sync.domains.v1` | domínios e regras cruzadas da visita, da atividade, da vigilância ambiental (35a) e do centro de zoonoses (35b), em dado |

## Regras

- **Aparelho.** Cadastrado no dashboard com segundo fator; o token
  (`rsf_` + 32 bytes em base64url) aparece uma vez, no QR
  `rotasaude-field:v1:<base64url de { host, token }>`. Vai só em
  `Authorization: Bearer rsf_…`, nunca na URL. Ausente ou desconhecido →
  `401 invalid_token`. Revogação manual (pelo dono ou pelo administrador:
  motivos `user` e `admin`) → `401 device_revoked`, e o app apaga tudo.
  Revogação por substituição do aparelho (`replaced`, Q17) ou automática (fim
  de vínculo ou usuário desativado: `membership_ended`, `user_disabled`) →
  `401 device_suspended`, sem dizer qual: o app guarda a fila de envio e apaga
  o território. `invalid_token` o app trata como `device_suspended`.
  120 requisições por minuto;
  só JSON (`415 json_required`); corpo até 2 MB (413). Interruptor `home_visits` desligado →
  `403 feature_disabled`.
- **Sessão (v1.2.0).** `map` descreve o mapa offline do município: `null`
  enquanto não há arquivo publicado; durante uma regeração ou depois de uma
  falha continua o publicado (Q30). `sha256` é o `ETag` do
  `GET /field/v1/map`, que aceita um `Range` por requisição, `If-Range` e
  `If-None-Match`, responde `416 range_not_satisfiable` com
  `Content-Range: bytes */<tamanho>` e `404 map_not_found` sem mapa (Q34).
  `reference_version` é um resumo opaco: o app compara, nunca recalcula;
  mudou → `GET /field/v1/reference`.
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
  `version` vencida voltam `stale_version` com a versão atual, `current_version`
  e `current`; isso vale só para um domicílio ou cadastro que JÁ EXISTE.
- **Família (`family`, v1.2.0).** Só o ACS (`cbo_not_allowed`). Sem
  `family_id` é família nova; com `family_id`, atualização. `version` é a do
  **domicílio**. O responsável vai em `responsible.patient_id` ou em
  `responsible.patient_client_uuid` (Q1); na família nova ele é obrigatório
  (`invalid_family`, `path` `responsible.patient_id`). Se o responsável tem
  cadastro individual ativo no domicílio, ele entra na família (L28 do 24a,
  Q25); quando é pessoa nova, o cadastro dele vai antes na fila. `family_id`
  desconhecido ou de outro domicílio → `family_not_found`. `stale_version`
  traz o `<household>` atual, e `id` é o domicílio, também na família nova
  (Q4). A troca de responsável fica fora do app. A versão nova do cadastro do
  responsável, gravada pela família, não volta no `accepted`: o próximo envio
  desse cadastro recebe `stale_version` e a mescla resolve (Q35).
- **Citação de pessoa (`patient_client_uuid`).** Cita um item `patient` ou um
  `individual_registration` que criou a pessoa (`new_patient`): o
  `client_uuid` do cadastro vale pelo paciente criado por ele (Q26).
- **`family_client_uuid` (v1.2.0).** No cadastro individual e na visita, cita
  um item `family` aceito antes, no lugar de `family_id`; no máximo um dos dois.
- **`version` no resultado (v1.2.0, Q5).** Obrigatória no `accepted` de
  `household`, `family` e `individual_registration` (a versão do domicílio nos
  dois primeiros, a do cadastro no terceiro). No `duplicate`, é a gravada
  naquele recebimento, e falta em recibo anterior ao v1.2.0: o app marca a
  linha para recarga, sem mescla. Os outros tipos nunca a trazem.
- **Coordenada (`location`, v1.2.0).** `latitude` (−90 a 90) e `longitude`
  (−180 a 180) com até 8 casas, e `source` (`gps` ou `map`), sempre presentes;
  `accuracy_m` (0 a 10000, 1 casa) é obrigatório com `gps` e opcional com
  `map` (Q3). Ausente = mantém o ponto (domicílio) ou sem ponto (visita);
  `null` só no domicílio, e apaga; na visita, `null` → `invalid_location`. A
  visita só aceita `gps` (`location.visit_sources` em `domains-v1.json`,
  regra do api: `map` → `invalid_location`). Mudar só o ponto gera versão e
  ficha de atualização. A coordenada nunca vai em URL, log ou evento. Erro de
  esquema sob `/body/location` volta `rejected` `invalid_location` com o mesmo
  `path`; os demais erros de esquema seguem `invalid_request` (Q2). No Ajv,
  `multipleOf: 1e-8` exige `multipleOfPrecision: 8` (Q49).
- **Referência (`GET /field/v1/reference`, v1.2.0).** Os domínios do cadastro
  vêm como listas `[{ code, label }]` na ordem do YAML do api (Q27).
  `team_professionals` traz só os profissionais das equipes do aparelho, com
  `has_cns`, nunca CPF nem CNS. `health_units.cnes` `null` = unidade sem CNES
  (Q6). Os domínios da visita e da atividade vêm num bloco só (Q7).
- **Códigos HTTP.** `errors.http` de `domains-v1.json` lista todo código que o
  `/field/v1` devolve, inclusive os de borda da cidade (`unknown_city`,
  `city_suspended`, `city_schema_behind`; Q8).
- **Resultados de erro (Q63).** `rejected` leva `error` e, quando o erro é de
  um campo, `path`; os outros `status` são `accepted`, `duplicate` e
  `stale_version`. Quatro regras:
  (a) item que levanta exceção inesperada é desfeito sozinho, no próprio
  savepoint, e volta `rejected` `internal_error`, sem `path` (o código vale
  para o item inteiro, como `day_closed`); não entra no livro de idempotência,
  então o reenvio o processa de novo, e o lote continua;
  (b) cadastro individual NOVO cujo domicílio citado mudou de versão volta
  `rejected` `household_changed` com `path` `household_id`, não
  `stale_version`;
  (d) `too_many_requests` (Q67): o usuário do aparelho estourou o orçamento
  compartilhado das buscas de pessoa, 30 por minuto por usuário; ele cobre a
  busca de duplicado e a checagem de unicidade de CPF/CNS que o item com
  `new_patient` dispara. O item volta `rejected` `too_many_requests`, sem
  `path`, e não entra no livro de idempotência: o reenvio o processa de novo.
  O app mostra uma frase genérica e reenvia mais tarde;
  (c) `already_registered` pode trazer `id` (o `registration_id` existente)
  SÓ quando esse cadastro está no escopo do aparelho (6A); fora do escopo não
  há `id`. Em qualquer outro `rejected`, `id` é proibido.
- **Retirada (`home_visit_withdrawal`).** As recusas de regra falham como na
  rota da equipe, sem `path` (o código vale para o item inteiro): folha já
  fechada → `rejected` `day_closed`; visita já retirada com outro
  `client_uuid` → `rejected` `visit_changed` (Q45). As recusas de forma têm
  `path`: `reason` fora de 10 a 500 caracteres → `invalid_request` com `path`
  `reason`; `visit_client_uuid` e `visit_id` juntos, ou nenhum dos dois →
  `invalid_request` com `path` `body`; visita desconhecida → `not_found` com
  `path` na chave usada. O mesmo item reenviado continua `duplicate`.
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
- **Download.** O `<household>` traz `location` (`null` sem ponto; v1.2.0).
  Por cursor opaco (`next_cursor`, sempre presente: o app o guarda
  para a próxima vez); páginas de até 500 itens; sem cursor = carga completa.
  `reset: true` = o escopo mudou: apague o que foi baixado (nunca o que falta
  enviar) e aplique as páginas. `removals` vêm das lápides (`moved`). A troca de escopo
  chega hoje como `reset: true`, não como remoção; `erased` e `out_of_scope`
  são motivos reservados no v1: o api ainda não os emite, mas o app deve
  tratá-los. "Quem visitar" vem só na última
  página (`has_more: false`), completo; nas outras, `null`. Toda página com
  pessoa grava trilha no api. Em `who_to_visit`, `due_on` do motivo é data, exceto em
  `care_line` com `status: overdue` de prática nunca feita: aí é `null` (sem prazo, sem
  data inventada) e o app mostra "nunca feita" no lugar do prazo (Q60); `due_soon` e
  `registration_due` sempre trazem data.
  Faixa de validade do cadastro (Q65): o `status` do cadastro é um retrato do instante do
  download; `valid`/`due_soon`/`expired` mudam só com o tempo, sem gravação, e o aparelho
  que já tem o item nunca recebe um `status` novo. Por isso o app recalcula a faixa na
  hora de exibir, a partir de `registered_at` (instante com o fuso da cidade; o dia é o
  da data desse instante): `vence_em` = esse dia + 24 meses de calendário (`Date#>>`;
  29/02 + 24 meses = 28/02 ou 29/02); `expired` se `vence_em <= hoje`; `due_soon` se
  `vence_em - hoje <= 60` dias; senão `valid`; `hoje` = o dia da cidade. É a regra do
  24a (`TerritoryRegistry::Validity`). Os status que não dependem do tempo (`missing`,
  `missing_identifier`, `refused`, `exited`) valem como enviados, sem recálculo.
  Família sem domicílio no download (Q66): a família cujo responsável é paciente
  provisório da UPA (Q47) não vai no domicílio, mas os outros membros chegam como
  cadastros e o `family_id` deles aponta para uma família que o aparelho nunca
  recebe. O app tolera: mostra o membro sem família, não falha e não cria família
  provisória.
- **UUID e texto.** Todo UUID vai em minúsculas (`client_uuid`, ids e
  citações): em maiúsculas o item volta `rejected` `invalid_request` com
  `path` `client_uuid` (ou o campo do id). O app envia `note` e `reason` já
  aparados: o api conta os caracteres depois de tirar os espaços das pontas, e
  o esquema conta o texto como veio.
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
- **Interruptor (v1.3.0).** `features.vector_control` na sessão (ausente =
  false). Desligado → itens `rejected` `feature_disabled`; o que já foi gravado
  fica.
- **Compatibilidade (v1.3.0, Q6).** O api só emite as entidades novas
  (`city_block`, `ovitrap`, `liraa_item`, `transmission_block`) e o
  `<household>.vector` para cidade com o gate `vector_control` utilizável;
  ligar ou desligar o interruptor chega a todo aparelho da cidade como
  `reset: true`; o app anterior ao do 35a não ignora tipo desconhecido no
  download e quebra com as entidades novas, por isso **nenhum aparelho com app
  anterior ao do 35a pode estar numa cidade com `vector_control` ligado** (gate
  de go-live); o app do 35a ignora tipo desconhecido e zera o cursor ao migrar
  o esquema local para a v2. O api aceita o envio da v1.2.0 sem mudança.
- **Boletim (`vector_inspection`, v1.3.0).** Só o agente de endemias (CBO
  515140) nas microáreas atribuídas (`cbo_not_allowed`, `path`
  `vector_inspection`); exige domicílio (`household_id` ou
  `household_client_uuid`; sem ele → `vector_inspection_invalid` com `path`
  `household_id`, CV-6). Listas ausentes = vazias. As relações estão em
  `vector_control.rules` e o api decide, com os códigos do §17; erro de esquema
  dentro do boletim → `rejected` `vector_inspection_invalid` com o mesmo `path`
  (CV-4). Os motivos 34 a 37 não vêm no `reasons` (`reason_derived`): o api os
  deriva. A etiqueta da amostra é `upcase(client_uuid[0,8]) + "-" + NN`,
  calculada igual no app e no api; colisão → `sample_label_taken` (código de
  item; 422 no dashboard, Q13(3)), `path` `vector_inspection.samples[i]` (Q7(1);
  o app só troca as etiquetas por ação explícita do agente). Os `path` das
  recusas são os `path` que o dashboard exibe (Q9). `charges` com até 2
  casas (o Ajv precisa de `multipleOfPrecision`, como na Q49).
- **Domicílio pelo agente de endemias (v1.3.0, Q13(1)).** Com `vector_control`
  utilizável, o item `household` deixa de ser só do ACS: o agente de endemias
  (515140) cadastra e edita, nas microáreas atribuídas a ele, domicílio **só**
  de tipo não residencial (`2 3 4 5 6 12 13`), sem família nem morador. Tipo
  residencial, troca para residencial, `family` e `individual_registration` →
  `rejected` `cbo_not_allowed`, como hoje. O esquema não muda (autoria não é
  forma), por isso não há exemplo novo.
- **Ovitrampa (v1.3.0).** `ovitrap_installation` (domicílio por id ou
  `client_uuid`; `consent` false → `consent_required`) e `ovitrap_collection`
  (por `ovitrap_id` ou `ovitrap_client_uuid`, que resolve pelo livro de
  idempotência; falta → `not_found`, `path` `ovitrap_client_uuid`). `reinstall`
  é true por padrão e ignorado com `remove: true` (o app manda
  `reinstall: !remove`), sem acoplamento no esquema; `reinstall: false` sem
  `remove: true` é recusado (`rejected` `invalid_request`, `path` `reinstall`;
  Q33); `condition: lost` + `remove: true` = perdida (CV-9). O `id` do
  resultado das duas é o da
  **ovitrampa** (CV-3). A contagem de ovos nunca vem do app.
- **Resultado (v1.3.0).** `vector_inspection_id` só no `accepted`/`duplicate`
  de `home_visit` com boletim.
- **Download (v1.3.0).** `<household>.vector` (ausente = gate não utilizável;
  `null` = sem perfil; **só leitura**, nunca vai no item `household`, CV-10);
  mudança de perfil reemite o `<household>` com a mesma `version` do 24a (o app
  sobrescreve). `city_block`, `ovitrap`, `liraa_item` (`closed` = levantamento
  fechado) e `transmission_block` (só `active` e `closed`; nunca caso nem
  notificação), cada um com `version`; o fim vem pelo `status`, sem `removal`
  novo. O app **sobrescreve** `city_block`, `ovitrap`, `liraa_item` e
  `transmission_block` a cada recebimento, qualquer que seja a `version`: o api
  reemite com a mesma `version` quando a mudança é de outra linha (contagem de
  ovos da leitura, fechamento do levantamento, ciclo de UBV novo) ou quando a
  entidade entra no escopo do aparelho por um domicílio ou perfil (Q29).
- **Referência (v1.3.0).** `vector_control_domains` só com o gate utilizável (`products[].charge_size` é texto
  `"^[0-9]{1,8}\.[0-9]{2}$"`, numeric(10,2); "> 0" é do api; Q15);
  `collective_activity_domains.rules` na forma de
  `CollectiveActivities::Json.domains` (Q3), com as sete chaves do api.
- **`street_type` (v1.3.0).** É o código DNE de `string_domains.tipo_logradouro`
  (`"081"`), nunca o rótulo; o esquema aceita texto, e quem recusa é o api
  (`invalid_household`, `path` `address.street_type`; CV-11).
- **Interruptor (v1.4.0).** `features.zoonoses` na sessão = `Zoonoses::Gate.field_usable?`
  (ausente = false). Desligado: os itens voltam `rejected` `feature_disabled`, o
  app esconde as telas e a fila espera (Q6 do 35a). O que foi gravado fica.
- **Compatibilidade (v1.4.0, §11).** O api emite `animal`, `leish_survey` e
  `zoonoses_domains` só com `field_usable?`; ligar ou desligar o interruptor
  chega a todo aparelho da cidade como `reset: true`. O app do 35a ignora tipo e
  `removal` desconhecidos no download e não valida a sessão nem a referência em
  execução: ele convive com a cidade e só não mostra os animais. O app anterior
  ao do 35a quebra, por isso **nenhum aparelho com app anterior ao do 35a pode
  estar numa cidade com `zoonoses` ligado** (gate de go-live). O api aceita o
  envio da v1.3.0 sem mudança.
- **Animal (`animal`, v1.4.0, D4, D5).** Corpo inteiro na criação e na edição; a
  edição leva `animal_id` + `version` (vencida → `stale_version` com o
  `<animal>` atual, D3). `microchip` e `registry_number` só na criação: o app não
  recebe o número (Q9) e não o reenvia. `status`/`status_on` só na edição, e quem
  deixa `active` sai do download. Animal comunitário não tem tutor. O tutor é
  opcional também com domicílio (tutor não identificado); é `tutor_patient_id`
  (o 515140 escolhe entre os moradores que o tablet tem) ou `tutor_client_uuid`,
  que cita um item `patient` ou um `individual_registration` com `new_patient` do
  mesmo lote (24c; Q22, Q29); `community: true` = ninguém responde pelo animal.
  o app nunca envia `neutered` (castração é do veterinário, §7; o download traz o valor). `birth_estimate_month`
  `"YYYY-MM"`: o api grava o dia 1, e o download traz `birth_estimate_on`.
  Recusas: `microchip_taken`, `registry_number_taken`, `animal_not_active`,
  `out_of_scope` e `tutor_not_found` (`tutor_client_uuid`).
- **Vacinação (`rabies_vaccination`, v1.4.0).** A modalidade é sempre `house`, e
  a campanha é o `open_campaign` da referência (`campaign_not_open`). Uma dose
  por animal e campanha (`already_vaccinated_in_campaign`): só o api barra,
  porque o tablet não sabe a campanha da última dose (Q19). `adverse_note` só
  com `adverse_event: true` (Q20). Data fora da janela → `date_out_of_range`;
  produto sem `rabies_vaccine` → `product_not_allowed`. O `adverse_event` mostra
  no app o lembrete do EATAV (§3). **A falta de estoque não é recusa**: o item
  volta `accepted`.
- **Coleta de LV (`leish_collection`, v1.4.0).** Só o CBO 515140
  (`cbo_not_allowed`) e só cão (`animal_not_dog`). O inquérito precisa estar
  `open` (`survey_not_open`) e cobrir o quarteirão do domicílio
  (`household_not_in_survey`); sem `leish_survey_id`, a coleta é avulsa.
  `dpp_result` e `dpp_on` vão juntos. A etiqueta é do api e volta em `label`,
  obrigatória no `accepted` e no `duplicate` (Q21, formato em
  `zoonoses.rules.leish_label`); até lá, o app mostra "Etiqueta depois de enviar".
- **Coleira (`collar`, v1.4.0).** Só cão; o `due_on` é do api; a coleira ativa
  anterior sai `replaced` na mesma transação (§6); a falta de estoque não é
  recusa. As coleiras a trocar (`collar_due_on` em até 15 dias) têm lista própria
  no app, fora de "Imóveis a visitar" (Q23).
- **Referência do item (v1.4.0).** `animal_client_uuid` resolve pelo livro de
  idempotência (falta → `not_found`). O `id` do resultado é o do animal, da
  vacinação, do teste e da coleira. Os códigos de item novos são dez, em
  `errors.item`: `microchip_taken`, `registry_number_taken`,
  `already_vaccinated_in_campaign`, `campaign_not_open`, `survey_not_open`,
  `animal_not_dog`, `animal_not_active`, `date_out_of_range`,
  `household_not_in_survey` e `tutor_not_found`.
- **Download (v1.4.0).** `animal` vem só pelo domicílio do escopo (sem
  domicílio, não vai) e só `active`. `leish_survey` vem só `open`, com
  `household_ids` = os domicílios do escopo nos quarteirões dele (Q21); a coleta
  só aparece nesses domicílios. A saída das duas vem por `removal`
  `out_of_scope` (Q21). O app **sobrescreve** `animal` e `leish_survey` a cada
  recebimento, qualquer que seja a `version`, como na Q29: `last_rabies_vaccination_on`
  e `collar_due_on` mudam sem `version` nova (D10). A fila local nunca é apagada.
  Nunca o número do microchip, e o tutor só com id e nome.
- **Referência (v1.4.0).** `zoonoses_domains` só com `field_usable?`.
  `open_campaign` é `null` sem campanha aberta; abrir ou fechar a campanha muda
  o `reference_version`, e o app baixa de novo (cache de 5 min do api).
  `vector_control_domains.products` traz só produtos de controle vetorial: a
  vacina e a coleira vêm só em `zoonoses_domains.products` (D1).

## Exemplos e verificação

`examples/` tem 265 exemplos (77 válidos, 188 inválidos, um defeito por arquivo),
gerados por `tools/make_examples.py` e listados em `examples/manifest.json`
(`{ suites: [ { schema, cases: [ { file, expect } ] } ] }`; `expect` é
`valid` ou o erro `<data_pointer> <type>` do `json_schemer`). A partir da raiz
do monorepo, com o compose de pé:

```bash
contracts/field-sync/tools/check.sh                           # todas as suítes (265/265)
contracts/field-sync/tools/check.sh upload-request-v1.json    # uma suíte
python3 contracts/field-sync/tools/check_domains.py           # $defs iguais, enum = domains, erros conhecidos,
                                                              # regras-da-atividade e logradouro-em-codigo (v1.3.0)
python3 contracts/field-sync/tools/check_domains.py --release # idem, e falha sem a prova técnica (proof)
```

## Consumo

O `api` copia os seis arquivos (os cinco esquemas e `domains-v1.json`) para
`config/field_sync/` e prende o SHA-256 de cada um num spec (como `config/lab/lab-report-v1.json`); as respostas reais de
`/field/v1/*` são validadas contra essas cópias. Mudou um esquema? Atualize os
dois lugares no mesmo ciclo, com entrada no CHANGELOG. O app de campo (24c)
consome os esquemas e `domains-v1.json` pela tag `field-sync-v1.4.0` e gera
deles os tipos TypeScript.
