# clinical — JSON canônico assinado (ADRs 0032 e 0033)

O documento que o profissional assina no prontuário. O `api` monta o JSON a partir
da consulta finalizada, do adendo ou do documento clínico emitido na consulta, serializa em **RFC 8785 (JCS)** e o `signer`
monta o CAdES destacado AD-RB sobre esses bytes. O `.p7s` e o `.json` exportados
juntos são validáveis no validar.iti.gov.br.

| Arquivo | `schema` | O que é |
|---|---|---|
| `consultation-v1.json` | `rotasaude.consultation.v1` | Consulta finalizada |
| `consultation-addendum-v1.json` | `rotasaude.consultation_addendum.v1` | Adendo (assinado pelo autor do adendo) |
| `clinical-document-v1.json` | `rotasaude.clinical_document.v1` | Documento clínico da consulta: atestado, declaração de comparecimento, receita comum, requisição de exames (ADR 0033) |

## Regras

- **Fechado em todo nível** (`additionalProperties: false`): o que não está no
  esquema não entra no que se assina. Campo novo = esquema novo (`v2`).
- **Uma representação por valor**, para o JCS dar um só hash:
  - instantes em UTC, com segundos, sem fração: `2026-10-08T13:41:37Z`;
  - datas `AAAA-MM-DD`; CPF, CNES, IBGE e CBO só com dígitos;
  - texto vazio é `null`, nunca `""`; medida não aferida é chave ausente em `vitals`.
- **Cabeçalho comum**: `city`, `unit`, `professional` (quem assina: o autor da
  consulta, do adendo ou do documento, com o CPF que tem de ser o do certificado),
  `patient`. O `$defs` é idêntico nos dois arquivos da consulta; o de
  `clinical-document-v1.json` repete, sem mudança, os que tem em comum com eles.
- **Adendo só da autora** (19a): o `professional` do adendo é sempre a autora
  da consulta. Os exemplos são fixtures do esquema, que não confere autoria;
  por isso `addendum-structured.json` traz outra profissional.
- **Versão da tabela no ato**: cada problema avaliado traz `release` e cada
  exame traz `competence` (competência SIGTAP `AAAAMM`) da tabela de onde saiu
  o rótulo, vigente quando o profissional assinou.
- **Cadeia**: `addendum.previous_sha256` é o SHA-256 (hex minúsculo) do JCS do
  documento assinado anterior da mesma consulta; sem nenhum assinado ainda, o
  do JCS da consulta como montado no momento em que o adendo é assinado, que
  não precisa coincidir com uma assinatura posterior da consulta.
- **`changes` do adendo**: chave ausente = sem mudança; `evaluated_problems`
  traz só os eventos novos; `conducts` é sempre a lista final, não vazia;
  `exam_requests: []` = todos os exames cancelados (lista final vazia).
- Os esquemas da consulta não conferem plausibilidade de sinais vitais, CID-10
  por CBO nem relações entre campos (o do documento clínico confere as da sua
  seção), texto só de espaços em branco, normalização Unicode
  nem datas impossíveis (ex.: `2026-13-45`): isso é do `api`. As listas
  mantêm a ordem de registro (não são ordenadas).

## Documento clínico (`clinical-document-v1.json`)

- **Conteúdo por tipo**: `document.kind` escolhe a forma de `content`
  (`sick_note`, `attendance_declaration`, `prescription`, `exam_requisition`); a
  forma de outro tipo é recusada.
- **Ausente × `null`**: campo que não se aplica ao caso (dias no atestado de
  acompanhante, `duration_days` não informada, `cid10` sem autorização) é chave
  **ausente**; texto que sempre se aplica (`note`) está sempre presente e é `null`
  quando vazio.
- **Atestado**: CID só com `cid_authorized: true`; acompanhante (`companion`)
  nunca com CID e sempre com nome, parentesco e motivo da CLT art. 473;
  afastamento (`leave`) com dias e início.
- **Declaração**: o dia mais o período **ou** a hora de chegada (e a de saída,
  se houver), em hora de parede da cidade `HH:MM`. Só a declaração emitida por
  profissional na consulta é assinada; a da recepção sai em papel e não tem JSON
  canônico.
- **Receita**: cada item é do catálogo (com o código CATMAT inteiro) **ou**
  texto livre; `catalog_release` é a versão do catálogo vigente na emissão
  (`null` se todos os itens são texto livre); `quantity` é número (pode ter
  casas decimais; o JCS escreve a forma mais curta). `catalog_item.dosage_form`
  está sempre presente e é `null` quando o CATMAT não traz a forma farmacêutica
  (o impresso usa a descrição original). Receita de enfermagem leva
  o protocolo (com a versão) e o CNPJ da cidade (alfanumérico da IN RFB
  2.229/2024, sem máscara), e só itens do catálogo. Antimicrobiano: 2 vias e
  `valid_until`; comum: 1 via.
- **Requisição de exames**: os exames da consulta, cada um com a competência
  SIGTAP gravada no ato (mesmo item de `consultation-v1`).
- O esquema não confere CBO por tipo de documento, protocolo vigente, dose
  máxima, item controlado nem o dígito verificador do CNPJ, nem a coerência
  entre `catalog_release` e os itens (`null` só se todos são texto livre),
  `city_cnpj` em receita que não é de enfermagem ou `antimicrobial` da receita
  frente ao dos itens: isso é do `api`.

## Exemplos e verificação

`examples/consultation/`, `examples/consultation-addendum/` e `examples/clinical-document/` seguem o manifesto
de `protocols/examples/` (`valid` ou o erro `<data_pointer> <type>` do
`json_schemer`). A partir da raiz do monorepo, com o compose de pé, o comando de
`protocols/README.md` com o esquema e o manifesto de cada um:

```bash
# consulta: troque os dois caminhos do comando de protocols/README.md por
#   contracts/clinical/consultation-v1.json contracts/clinical/examples/consultation/manifest.json
# adendo:
#   contracts/clinical/consultation-addendum-v1.json contracts/clinical/examples/consultation-addendum/manifest.json
# documento clínico:
#   contracts/clinical/clinical-document-v1.json contracts/clinical/examples/clinical-document/manifest.json
```

## Vetor de canonicalização

`examples/canonical/` tem o JCS de `consultation-full.json`,
`addendum-structured.json`, `prescription-doctor.json`, `sick-note-leave.json` e
`prescription-dosage-form-null.json` e o `SHA256SUMS`. Todo gerador do JSON
canônico tem de produzir exatamente esses bytes a partir desses documentos
(`shasum -a 256 -c SHA256SUMS` dentro da pasta). O vetor cobre acento, cedilha e
emoji em UTF-8 cru, decimais (`36.7`, `81.5`, `31.1`), `null` e chave ausente
(`note`, `duration_days`) e `dosage_form: null`.
