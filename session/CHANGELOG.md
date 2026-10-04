# Changelog — session

## session-v1.0.0 — 2026-10-04 — MAJOR

Issue de migração coordenada: rotasaude/api#35

Primeira versão do contrato de sessão. Documenta o corpo de `GET /session` e de
`POST /session` (mesmo formato; `POST /session/grant` também), e o `data.scope`
do envelope de `/admin/api`.

**Substitui chaves que nunca foram documentadas** e vinham do tempo do
município como inquilino (RLS): `municipality_id`,
`municipality_name` e `municipality_uf` em cada membership da sessão, e
`scope.municipality` (`{ id, slug, name: "Nome · UF", uf }`) no envelope. Valem
agora, no lugar delas:

- `memberships[]`: `city_slug`, `city_name`, `city_uf`, `role`;
- `data.scope.city`: `{ slug, name, uf }`.

Migração em expand/contract, na ordem de deploy: api emite as duas formas →
`dashboard` e `admin` leem as novas (o `admin` deixa de mandar o parâmetro
`municipality_id`, que o api já ignorava) → api remove as antigas. Esta versão é
a forma final, depois do passo de remoção.

Fora deste contrato: `GET /admin/api/municipalities` (catálogo do seletor, que
devolve só a cidade do host com a forma própria `{ id, slug, name, uf }`) e a
sessão de operador no console de plataforma (`Operators::SessionsController`),
que usa o mesmo formato de `session_user` sem `time_zone`.
