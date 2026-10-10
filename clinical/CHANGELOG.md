# Changelog — clinical

## clinical-v1.1.0 — 2026-10-09 — MINOR

Documento clínico emitido na consulta (ADR 0033, módulo 19c). Nada do
`v1.0.0` muda.

- `clinical-document-v1.json` (`rotasaude.clinical_document.v1`): o mesmo
  cabeçalho da consulta (cidade, unidade, profissional, paciente), o documento
  (`id`, `kind`, `issued_at`, `replaces_document_id`) e o conteúdo do tipo —
  atestado (afastamento ou acompanhante, CID só com autorização), declaração de
  comparecimento (período ou horário), receita comum (itens do CATMAT ou texto
  livre, versão do catálogo, protocolo de enfermagem e CNPJ, antimicrobiano em
  2 vias) e requisição de exames (SIGTAP com competência).
- Fechado em todo nível; conteúdo escolhido por `document.kind`; `$defs`
  comuns idênticos aos de `consultation-v1.json`.
- `catalog_item.dosage_form` aceita `null` (a chave continua obrigatória) quando
  o CATMAT não traz a forma farmacêutica (decisão de 2026-10-10).
- `examples/clinical-document/`: 47 exemplos (11 válidos, 36 inválidos).
- Vetor de canonicalização: `prescription-doctor.jcs`, `sick-note-leave.jcs` e
  `prescription-dosage-form-null.jcs` em `examples/canonical/`, com as linhas
  novas no `SHA256SUMS`.

## clinical-v1.0.0 — 2026-10-09 — MAJOR

Primeira versão do domínio (ADR 0032, módulo 19b): o JSON canônico que o
profissional assina no prontuário.

- `consultation-v1.json` (`rotasaude.consultation.v1`): cidade (IBGE), unidade
  (CNES), profissional (nome, CPF, CBO, conselho), paciente (nome de exibição,
  CPF, nascimento) e a consulta finalizada — horários, tipo de atendimento,
  S/O/A/P, sinais vitais, problemas avaliados (terminologia, código, rótulo,
  versão da tabela, ação), condutas, exames (SIGTAP grupo 02, com a
  competência AAAAMM da tabela) e desfecho.
- `consultation-addendum-v1.json` (`rotasaude.consultation_addendum.v1`): o
  mesmo cabeçalho, com o autor do adendo como profissional, e o adendo —
  motivo, texto, mudanças estruturadas e `previous_sha256` (cadeia).
- Fechados em todo nível; só formas com uma representação (UTC com `Z`, CPF só
  dígitos, `null` para texto vazio), porque o hash assinado é do JCS (RFC 8785).
- `examples/`: 42 exemplos (4 válidos, 38 inválidos) e o vetor de
  canonicalização (`examples/canonical/`, com `SHA256SUMS`).
- Valores tirados do 19a (ADR 0031): tipos de atendimento 1, 2, 5, 6;
  condutas 1, 2, 4–12, 14 (até 12); até 50 problemas e 100 exames; textos até
  20.000; motivo do adendo 10–500; conselhos de `Professional::COUNCILS`.
- Documento assinado nunca muda: mudança de forma será `consultation-v2.json`
  (novo `schema`), com `v1` mantido para verificar o que já foi assinado.
