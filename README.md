# contracts — contratos compartilhados do Rota Saúde

Contrato neutro consumido por `api` e pelos frontends (`admin-console`, `dashboard`,
`wpda`). Princípio (ADR 0002): **as aplicações compartilham contrato, não código.**
Quatro domínios, **versionados independentemente** (ADR 0015):

| Domínio | O que é | Estado |
|---|---|---|
| [`events/`](events/EVENTS.md) | Formato dos domain events (nome, escopo, payload) | **materializado** (do código real) |
| [`protocols/`](protocols/schema.json) | JSON Schema da definição de protocolo (ADR 0009) | **materializado** |
| `types/` | Contrato de tipos da API (Ruby ↔ TS) | **scaffold** — extração da API pendente |
| `design-tokens/` | Cores, espaçamento, tipografia como dado | **scaffold** — precisa de input de design |

## Versionamento (ADR 0015)

- **SemVer 2.0.0 por domínio**, com tag prefixada (`events-vX.Y.Z`, `protocols-vX.Y.Z`,
  `types-vX.Y.Z`, `tokens-vX.Y.Z`). Cada app fixa a versão **do domínio que consome**.
- **Classificação de mudança:**
  - **MAJOR** — quebra consumidores (remove/renomeia campo, muda tipo, renomeia evento,
    torna obrigatório um opcional). Nunca entra sozinho — usa **expand/contract**
    (suportar a forma antiga E a nova num MINOR; migrar cada app; remover a antiga num
    MAJOR só quando todos migraram).
  - **MINOR** — adiciona sem quebrar (campo opcional, evento novo, valor de enum novo).
  - **PATCH** — corrige sem mudar forma.
- **Invariante de tolerância do consumidor** (pré-condição de MINOR seguro): todo
  consumidor **tolera** campo desconhecido (ignora), valor de enum desconhecido
  (fallback) e evento desconhecido (ignora). Verificável em teste.
- **CHANGELOG obrigatório** por domínio (`<dominio>/CHANGELOG.md`): sem entrada, não há
  tag. MAJOR linka a issue de migração coordenada.

## Nota de proveniência

Materializado na Etapa 10 da refundação. Substitui o `packages/` do monorepo
(`packages/protocols` → `contracts/protocols`; `packages/types` → `contracts/types`;
`packages/ui` **dissolvido** → `contracts/design-tokens`). O `packages/` antigo
permanece até a migração de topologia (multi-repo) removê-lo.
