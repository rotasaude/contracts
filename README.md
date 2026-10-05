# contracts — contratos compartilhados do Rota Saúde

Contrato neutro entre o `api` e os frontends (`admin`, `dashboard`, `wpda`,
`maintenance`). Princípio do ADR 0002: **as aplicações compartilham contrato,
não código.** Não deploya e não tem código executável; é dado e documentação
versionados.

## Papel no ecossistema

| Repo | Papel |
|---|---|
| `api` | Backend único (Rails 8). Emite os eventos e valida protocolos |
| `wpda`, `dashboard`, `admin`, `maintenance` | Frontends: cidadão, prefeitura, plataforma e manutenção |
| **`contracts`** (este) | O que mais de um repo precisa concordar: eventos, schema de protocolo, tipos, tokens |
| `docs` | ADRs, specs e planos. O ADR 0015 governa este repo |

## Domínios

Cinco domínios, **versionados de forma independente** (ADR 0015):

| Domínio | O que é | Versão | Estado |
|---|---|---|---|
| [`events/`](events/EVENTS.md) | Catálogo dos eventos: nome, escopo, payload | `events-v2.1.0` | Materializado, reconciliado com o código |
| [`protocols/`](protocols/README.md) | JSON Schema da definição de protocolo (ADR 0009) | `protocols-v1.4.0` | Materializado |
| [`session/`](session/CHANGELOG.md) | Corpo da sessão (`GET /session`) e escopo do envelope de `/admin/api` | `session-v1.1.0` | Materializado |
| [`types/`](types/README.md) | Contrato de tipos da API (Ruby ↔ TS) | — | Scaffold: extração pendente |
| [`design-tokens/`](design-tokens/README.md) | Cores, espaçamento e tipografia como dado | — | Scaffold: precisa de input de design |

### events

Os eventos têm dois escopos, que seguem o banco por cidade
([ADR 0020](https://github.com/rotasaude/docs/blob/main/adr/0020.md)):

- **Tenant-scoped:** `DomainEvents.publish`, gravado no `domain_events` do
  **banco da cidade**. O evento não carrega `municipality_id`: a cidade é o
  banco.
- **Platform-scope:** `Platform.audit`, gravado em `platform_events` no
  **banco de plataforma**. Referencia a cidade por `city_id` e tem garantia de
  ausência de dado pessoal.

`events-v2.0.0` (2026-09-16, MAJOR) removeu `municipality_id` e reconciliou o
catálogo com o código. A migração coordenada foi a issue
[rotasaude/contracts#1](https://github.com/rotasaude/contracts/issues/1).
`events-v2.1.0` (MINOR) acrescentou `operator.impersonated`, que só ocorre em
development.

No `api`, um evento de plataforma com nome novo quebra a suíte até ser
declarado na lista de nomes permitidos (`R18_PLATFORM_EVENT_NAMES`, em
`spec/events/platform_event_payload_guard_spec.rb`). Declare o
evento lá **e** aqui, no mesmo ciclo.

### protocols

`schema.json` é o contrato único da definição de protocolo, consumido pelo
validador do motor Ruby. O editor do `dashboard` não importa o arquivo: salva
pelo `api`, que valida contra ele. `v1.1.0`
acrescentou `recommendations`, `priority_when` e a gramática de condições
(`$defs/condition`), sem remover nada. `v1.2.0` acrescentou `analytic` na
pergunta (Analytics, ADR 0025), válido só em `boolean` e `enum`. `v1.3.0` faz o schema exigir `options`
(não vazio) em pergunta `enum`, regra que já constava na descrição. `v1.4.0`
acrescentou `offer` (título, resumo, elegibilidade e intervalo de repetição do
catálogo), `suggestions` e os operadores `gte`/`lte` (ADR 0027). Exemplos
válidos e inválidos ficam em `protocols/examples/`.

O `api` usa uma **cópia** em `config/protocols/schema.json`, não uma
dependência. Hoje as duas estão idênticas. Mudou o schema? Atualize os dois
lugares no mesmo ciclo, com entrada no CHANGELOG daqui.

### session

`schema.json` descreve o corpo de `GET /session` (e de `POST /session` e
`POST /session/grant`) e o `data.scope` do envelope de `/admin/api`. `v1.1.0`
acrescentou `features` (chaves de interruptor ligadas na cidade do host, ADR
0028). O `api` não tem cópia deste schema. Exemplos válidos e inválidos ficam
em `session/examples/`, com o mesmo formato de manifesto de
`protocols/examples/`; verifique, a partir da raiz do monorepo e com o compose
de pé:

```bash
python3 -c '
import json, os, sys
schema_path, manifest_path, extras = sys.argv[1], sys.argv[2], sys.argv[3:]
base = os.path.dirname(manifest_path)
cases = [dict(c, doc=json.load(open(os.path.join(base, c["file"])))) for c in json.load(open(manifest_path))["cases"]]
cases += [{"file": p, "expect": "valid", "doc": json.load(open(p))} for p in extras]
print(json.dumps({"schema": json.load(open(schema_path)), "cases": cases}))
' contracts/session/schema.json contracts/session/examples/manifest.json \
| docker compose exec -T -w /rails api bundle exec ruby -rjson -rjson_schemer -e '
input = JSON.parse(STDIN.read)
schemer = JSONSchemer.schema(input["schema"])
passed = input["cases"].count do |c|
  errors = schemer.validate(c["doc"]).map { |e| p = e["data_pointer"]; "#{p.empty? ? "(root)" : p} #{e["type"]}" }.uniq
  ok = c["expect"] == "valid" ? errors.empty? : errors.include?(c["expect"])
  puts "#{ok ? "ok  " : "FAIL"} #{c["file"]} — esperado: #{c["expect"]}; obtido: #{errors.empty? ? "valid" : errors.join(" | ")}"
  ok
end
puts "#{passed}/#{input["cases"].size} casos"
exit(passed == input["cases"].size ? 0 : 1)'
```

### Fora deste repo, por enquanto

- **SDL GraphQL da API de manutenção:** vive em `maintenance/schema.graphql`,
  extraído do `api` por `npm run schema:pull`. A spec prevê publicá-lo aqui
  quando houver um domínio para ele.
- **Tokens de tema:** cada frontend tem o próprio `src/theme/tokens.ts`, até
  `design-tokens/` ser materializado.

## Versionamento (ADR 0015)

- **SemVer 2.0.0 por domínio**, com tag prefixada (`events-vX.Y.Z`,
  `protocols-vX.Y.Z`, `session-vX.Y.Z`, `types-vX.Y.Z`, `tokens-vX.Y.Z`). Cada app fixa a versão
  **do domínio que consome**.
- **Classificação de mudança:**
  - **MAJOR:** quebra consumidores (remove ou renomeia campo, muda tipo,
    renomeia evento, torna obrigatório um campo opcional). Nunca entra sozinho;
    usa **expand/contract**: suporta a forma antiga e a nova num MINOR, migra
    cada app e remove a antiga num MAJOR só quando todos migraram.
  - **MINOR:** adiciona sem quebrar (campo opcional, evento novo, valor de enum
    novo).
  - **PATCH:** corrige sem mudar a forma.
- **Invariante de tolerância do consumidor** (pré-condição de um MINOR seguro):
  todo consumidor **tolera** campo desconhecido (ignora), valor de enum
  desconhecido (usa fallback) e evento desconhecido (ignora). Verificável em
  teste.
- **CHANGELOG obrigatório** por domínio (`<dominio>/CHANGELOG.md`): sem
  entrada, não há tag. Um MAJOR aponta a issue de migração coordenada.
- **Commits** seguem Conventional Commits em inglês, como nos outros repos.
  Os commits de release de domínio podem começar pela tag (`events-v2.1.0: …`).

## Em aberto (ADR 0015)

- **Mecanismo de distribuição:** hoje é cópia manual (o `schema.json` no
  `api`). Pacote, submódulo ou download por tag ainda não foi decidido.
- **Validação automática** da categoria da mudança e compatibilidade de eventos
  já persistidos.

## Proveniência

Materializado na Etapa 10 da refundação. Substituiu o `packages/` do monorepo:
`packages/protocols` virou `contracts/protocols`, `packages/types` virou
`contracts/types` e `packages/ui` foi **dissolvido** em
`contracts/design-tokens`. O `packages/` antigo ainda existe na raiz do
monorepo, fora do git.
