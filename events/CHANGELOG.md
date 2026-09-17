# Changelog — events

Formato: cada entrada tem versão, data, categoria (MAJOR/MINOR/PATCH) e o quê mudou.
Sem entrada, não há tag (ADR 0015).

## events-v2.0.0 — 2026-09-16 — MAJOR

Issue de migração coordenada: rotasaude/contracts#1

Reconciliação do contrato com o código real. O `v1.0.0` foi extraído antes da
migração para banco por cidade e descrevia um sistema que deixou de existir: a
seção platform-scope falava em `municipality_id` nulo "sob bypass", que é
vocabulário da RLS desmontada, e o catálogo de eventos estava defasado em treze
entradas.

**MAJOR — removido (nenhum consumidor possível):**
- `inbound_message.received` **não é emitido por código nenhum**. O v1 o listava
  como primeira linha da tabela e ainda lhe atribuía um consumidor
  (`ProcessInboundMessageJob`): quem integrasse por este contrato esperaria para
  sempre por um evento que não chega.
- Campo `municipality_id` em `inbound_message.received`, `protocol.activated` e
  `municipality.provisioned`. Não existe em evento nenhum desde a migração para
  banco por cidade — cada cidade É o escopo, e o que identifica a cidade em
  evento de plataforma passou a ser `city_id`.

Não houve expand/contract porque não há o que expandir: nenhuma das duas formas
removidas é emitida, então não existe consumidor em produção lendo a forma antiga.
Levantamento em rotasaude/contracts#1: nenhum dos três frontends cita nome de
evento literal, e o único acoplamento — o filtro do `dashboard` em
`/admin/api/events` — monta as opções a partir da própria resposta da API, não de
uma lista em tempo de compilação.

**MAJOR — corrigido escopo (o v1 mandava ler no banco errado):**
- `user.invited` e `user.deactivated` estavam documentados como platform-scope;
  são **tenant-scoped**, gravados em `domain_events` no banco da cidade. Além de
  errado, era impossível: `platform_events` recusa payload com chave `email`, que
  é justamente o payload de `user.invited`.

**MINOR — treze eventos acrescentados**, todos já emitidos e nenhum documentado:
`protocol.retired`, `identity.govbr_login`, `operator.city_access` (nos dois
escopos), `operator.login`, `city.suspended`, `city.resumed`, `city.backed_up`,
`city.restored`, `city.archived`, `city.key_rotated`, `city.admin_reinvited`,
`channel.registered`, `channel.token_rotated`, `channel.unknown_seen`.

**PATCH — descrições corrigidas:**
- `consent.revoked` estava marcado "— (auditoria)"; tem **dois consumidores**
  (`AnonymizeRevokedTriageJob`, `RecordConsentRevocationJob`), sendo que o primeiro
  anonimiza dado de triagem. Descrever como só-auditoria sugeria que reemitir não
  tem consequência.
- `membership.revoked` e `user.deactivated` carregam também `by`.
- `Outcome#to_h` contribui `awaiting` além das cinco chaves listadas, e passa por
  `.compact` — chave nula não viaja, e o consumidor precisa tolerar a ausência.
- Definição de escopo reescrita: o que distingue os dois não é rótulo, é em qual
  banco o evento é gravado e sob quais garantias.

**Documentado pela primeira vez:** a garantia de ausência de dado pessoal em
`platform_events` — validação de runtime que recusa chaves proibidas por substring
em qualquer profundidade, com allow-list explícita para `phone_number_id` e
`city_name`. É garantia forte para o consumidor e não constava do contrato.

**Registrado como dependência sem produtor:** `protocol.created` é lido por
`admin/protocols_query` e emitido apenas pela semente de demonstração.

## events-v1.0.0 — 2026-06-23 — MAJOR (inicial)
- Contrato inicial extraído do `api` após o rename PT→EN (C1): eventos `triage.*`,
  `consent.*`, `protocol.*`, `membership.*`, `user.*`, `municipality.provisioned`,
  `inbound_message.received`. Ver `EVENTS.md`.
