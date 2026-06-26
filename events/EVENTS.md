# events — contrato dos domain events

Formato dos eventos publicados em `domain_events` (ADR 0004). Extraído do código real
do `api` (estado final, EN após o rename C1). Cada evento tem **nome**, **escopo**
(tenant-scoped via `DomainEvents.publish` ou platform-scope via `Platform.audit`,
ADR 0014) e **payload**.

> O payload viaja como dado literal; o id do agregado vai **no payload** (não há colunas
> `aggregate_*` — C2). Eventos sem consumidor são **só auditoria**.

## Tenant-scoped (`DomainEvents.publish`, sob o tenant da cidade)

| Evento | Payload | Consumidores |
|---|---|---|
| `inbound_message.received` | `inbound_message_id`, `municipality_id` | `ProcessInboundMessageJob` |
| `triage.completed` | `triage_id`, + `Outcome.to_h` (`tier`, `priority`, `trail`, `status`, `score`) | `GenerateReportJob`, `UpdateDashboardJob`, `NotifyCitizenJob` |
| `triage.urgent` | `triage_id`, + `Outcome.to_h` | `AlertMunicipalityJob` |
| `consent.given` | `conversation_id`, `consent_id`, `version` | — (auditoria) |
| `consent.revoked` | `conversation_id`, `consent_id`, `reason` | — (auditoria) |
| `protocol.published` | `protocol_definition_id`, `protocol_key`, `version`, `actor` | — (auditoria) |
| `protocol.activated` | `municipality_id`, `protocol_key`, `protocol_definition_id`, `version`, `activated_by` | — (auditoria) |
| `protocol.retired` | `protocol_definition_id`, `protocol_key`, `version`, `actor` | — (auditoria) |
| `membership.granted` | `user_id`, `role` | — (auditoria) |
| `membership.revoked` | `user_id`, `role` | — (auditoria) |

## Platform-scope (`Platform.audit`, `municipality_id` nulo, sob bypass)

| Evento | Payload |
|---|---|
| `user.invited` | `email`, `role`, `invitation_id` |
| `user.deactivated` | `user_id` |
| `municipality.provisioned` | `municipality_id`, `ibge_code`, `by` |

## Convenções (ADR 0004)

- Nome: minúsculo, `<agregado>.<ação_passado>` (`triage.completed`), nunca o nome do
  consumidor.
- Payload só com dados (nunca objetos AR), incluindo o id do agregado quando o consumidor
  precisar (ex.: `triage_id`).
- Adicionar evento ou campo opcional = **MINOR**; renomear/remover = **MAJOR** (ADR 0015).

## Pendência a registrar (decisão do autor)

- `protocol.created` é emitido e **lido** pelo `admin/protocols_query` (`created_by`), mas
  **não está modelado no v2**. Mesma situação da tabela `authors`. Decisão pendente:
  modelar (entra aqui como evento de 1ª classe) ou remover a feature. Até lá, fica
  documentado como evento existente fora do contrato canônico.
