# clinical — JSON canônico assinado (ADR 0032)

O documento que o profissional assina no prontuário. O `api` monta o JSON a partir
da consulta finalizada (ou do adendo), serializa em **RFC 8785 (JCS)** e o `signer`
monta o CAdES destacado AD-RB sobre esses bytes. O `.p7s` e o `.json` exportados
juntos são validáveis no validar.iti.gov.br.

| Arquivo | `schema` | O que é |
|---|---|---|
| `consultation-v1.json` | `rotasaude.consultation.v1` | Consulta finalizada |
| `consultation-addendum-v1.json` | `rotasaude.consultation_addendum.v1` | Adendo (assinado pelo autor do adendo) |

## Regras

- **Fechado em todo nível** (`additionalProperties: false`): o que não está no
  esquema não entra no que se assina. Campo novo = esquema novo (`v2`).
- **Uma representação por valor**, para o JCS dar um só hash:
  - instantes em UTC, com segundos, sem fração: `2026-10-08T13:41:37Z`;
  - datas `AAAA-MM-DD`; CPF, CNES, IBGE e CBO só com dígitos;
  - texto vazio é `null`, nunca `""`; medida não aferida é chave ausente em `vitals`.
- **Cabeçalho comum**: `city`, `unit`, `professional` (quem assina: o autor da
  consulta ou do adendo, com o CPF que tem de ser o do certificado), `patient`.
  O `$defs` é idêntico nos dois arquivos.
- **Adendo só da autora** (19a): o `professional` do adendo é sempre a autora
  da consulta. Os exemplos são fixtures do esquema, que não confere autoria;
  por isso `addendum-structured.json` traz outra profissional.
- **Cadeia**: `addendum.previous_sha256` é o SHA-256 (hex minúsculo) do JCS do
  documento assinado anterior da mesma consulta; sem nenhum assinado ainda, o
  do JCS da consulta como montado no momento em que o adendo é assinado, que
  não precisa coincidir com uma assinatura posterior da consulta.
- **`changes` do adendo**: chave ausente = sem mudança; `evaluated_problems`
  traz só os eventos novos; `conducts` é sempre a lista final, não vazia;
  `exam_requests: []` = todos os exames cancelados (lista final vazia).
- O esquema não confere plausibilidade de sinais vitais, CID-10 por CBO nem
  relações entre campos, texto só de espaços em branco, normalização Unicode
  nem datas impossíveis (ex.: `2026-13-45`): isso é do `api`. As listas
  mantêm a ordem de registro (não são ordenadas).

## Exemplos e verificação

`examples/consultation/` e `examples/consultation-addendum/` seguem o manifesto
de `protocols/examples/` (`valid` ou o erro `<data_pointer> <type>` do
`json_schemer`). A partir da raiz do monorepo, com o compose de pé, o comando de
`protocols/README.md` com o esquema e o manifesto de cada um:

```bash
# consulta: troque os dois caminhos do comando de protocols/README.md por
#   contracts/clinical/consultation-v1.json contracts/clinical/examples/consultation/manifest.json
# adendo:
#   contracts/clinical/consultation-addendum-v1.json contracts/clinical/examples/consultation-addendum/manifest.json
```

## Vetor de canonicalização

`examples/canonical/` tem o JCS de `consultation-full.json` e de
`addendum-structured.json` e o `SHA256SUMS`. Todo gerador do JSON canônico tem
de produzir exatamente esses bytes a partir desses documentos
(`shasum -a 256 -c SHA256SUMS` dentro da pasta). O vetor cobre acento e emoji
em UTF-8 cru e decimais (`36.7`, `81.5`, `31.1`).
