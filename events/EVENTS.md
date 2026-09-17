# events — contrato dos domain events

Formato dos eventos publicados pelo `api` (ADR 0004). Extraído do código real.

Cada evento tem **nome**, **escopo** e **payload**. O escopo não é rótulo: ele diz
em **qual banco** o evento é gravado, e os dois bancos têm regras diferentes.

- **Tenant-scoped** — `DomainEvents.publish`, grava em `domain_events` **no banco da
  cidade**, dentro da conexão dela. Exige `Current.city` setado (sem cidade,
  levanta `DomainEvents::CityMissing`). Publique **dentro da transação da cidade**:
  o evento comita junto com a escrita de domínio e os consumidores só entram na
  fila após o COMMIT; num ROLLBACK, nenhum é enfileirado.
- **Platform-scope** — `Platform.audit`, grava em `platform_events` **no banco de
  plataforma**. Só para objetos de plataforma: cidades, canais e operadores.
  **Nunca carrega dado pessoal** — ver a garantia abaixo, que é validada em runtime.

> O payload viaja como dado literal; o id do agregado vai **no payload** (não há
> colunas `aggregate_*`). Eventos sem consumidor são **só auditoria**.

## Tenant-scoped (`DomainEvents.publish`, no banco da cidade)

| Evento | Payload | Consumidores |
|---|---|---|
| `triage.completed` | `triage_id`, + `Outcome#to_h` | `GenerateReportJob`, `UpdateDashboardJob`, `NotifyCitizenJob` |
| `triage.urgent` | `triage_id`, + `Outcome#to_h` | `AlertMunicipalityJob` |
| `consent.given` | `conversation_id`, `consent_id`, `version` | — (auditoria) |
| `consent.revoked` | `conversation_id`, `consent_id`, `reason` | `AnonymizeRevokedTriageJob`, `RecordConsentRevocationJob` |
| `protocol.published` | `protocol_definition_id`, `protocol_key`, `version`, `actor` | — (auditoria) |
| `protocol.activated` | `protocol_key`, `protocol_definition_id`, `version`, `activated_by` | — (auditoria) |
| `protocol.retired` | `protocol_definition_id`, `protocol_key`, `version`, `actor` | — (auditoria) |
| `membership.granted` | `user_id`, `role` | — (auditoria) |
| `membership.revoked` | `user_id`, `role`, `by` | — (auditoria) |
| `user.invited` | `email`, `role`, `invitation_id` | — (auditoria) |
| `user.deactivated` | `user_id`, `by` | — (auditoria) |
| `identity.govbr_login` | `user_id`, `provider_uid`, `assurance` | — (auditoria) |
| `operator.city_access` | `operator_id`, `session_id` | — (auditoria) |

**`Outcome#to_h`** contribui `status`, `tier`, `priority`, `score`, `awaiting` e
`trail` — mas passa por `.compact`: **chave nula não viaja**. O consumidor precisa
tolerar a ausência de qualquer uma delas, o que é um caso particular da invariante
de tolerância exigida no README deste repositório.

**`user.*`, `membership.*` e `identity.*` são tenant-scoped**, não platform-scope:
pessoa pertence à cidade, e os dados dela vivem no banco dela. Um `user.invited`
com `email` no payload seria **recusado** pela validação de `platform_events`.

## Platform-scope (`Platform.audit`, no banco de plataforma)

| Evento | Payload |
|---|---|
| `municipality.provisioned` | `city_id`, `ibge_code`, `by` |
| `city.suspended` | `city_id` |
| `city.resumed` | `city_id` |
| `city.backed_up` | `city_id`, `file` |
| `city.restored` | `city_id`, `file` |
| `city.archived` | `city_id`, `backup` |
| `city.key_rotated` | `city_id` |
| `city.admin_reinvited` | `city_id`, `invitation_id` |
| `channel.registered` | `city_id`, `phone_number_id` |
| `channel.token_rotated` | `city_id`, `phone_number_id`, `by` |
| `channel.unknown_seen` | `phone_number_id`, `hits` |
| `operator.login` | `operator_id`, `operator_session_id` |
| `operator.city_access` | `city_id`, `operator_id` |

**`operator.city_access` é emitido nos DOIS escopos**, e é de propósito: a
plataforma registra que um operador entrou numa cidade (`city_id`, `operator_id`) e
a própria cidade registra que foi acessada (`operator_id`, `session_id`). Um
consumidor que só olhe um dos lados vê metade da trilha.

### Garantia de ausência de dado pessoal (platform-scope)

`platform_events` **recusa a gravação** de payload que carregue chave de dado
pessoal, em qualquer profundidade, com validação de runtime. A regra é por
**substring**, sem diferenciar maiúsculas — `email`, `cpf`, `phone`, `wa_id`,
`provider_uid`, `body`, `name` — mais a chave exata `from`. Isso significa que
`user_email`, `display_phone_number` e `full_name` são recusadas sem precisarem
estar listadas uma a uma.

Duas chaves vencem a regra por allow-list explícita: **`phone_number_id`** (é o id
do número do canal na Meta — identificador de canal de plataforma, não de pessoa) e
**`city_name`** (nome da cidade, objeto de plataforma). Qualquer chave nova que case
um fragmento proibido só entra por essa allow-list, com justificativa.

Para o consumidor, isto é uma garantia forte: um evento de plataforma **nunca**
contém dado de cidadão, e a promessa é sustentada por validação, não por convenção.

## Convenções (ADR 0004)

- Nome: minúsculo, `<agregado>.<ação_passado>` (`triage.completed`), nunca o nome do
  consumidor.
- Payload só com dados (nunca objetos AR), incluindo o id do agregado quando o
  consumidor precisar (ex.: `triage_id`).
- Adicionar evento ou campo opcional = **MINOR**; renomear/remover = **MAJOR**
  (ADR 0015).

## Fora do contrato canônico

- **`protocol.created`** é **lido** por `admin/protocols_query` (para preencher
  `created_by`), mas **nenhum código de produção o emite** — só a semente de
  demonstração (`lib/dashboard_demo.rb`). Na prática, `created_by` vem vazio fora de
  dev. Decisão pendente: passar a emitir no comando de criação (entra aqui como
  evento de 1ª classe) ou remover a leitura. Até lá, fica registrado como
  dependência sem produtor.
