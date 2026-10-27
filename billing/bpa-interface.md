# Perfil do arquivo de interface do BPA Magnético (billing-v1.1.0)

Arquivo que o Rota Saúde gera no fechamento da competência de um
estabelecimento faturante e que o faturista importa no BPA Magnético
(menu de importação de "sistemas próprios"). ADR 0039; módulo 22.
Layout: `Layout_Exportacao_BPA.pdf` do DATASUS de **09/07/2026** (BPA
05.00), SHA-256 `f318bc0359b378e8455280f87dec0ad8c016bcf853d640f2f83353e5648f9f1f`,
conferido em `docs/pesquisa/2026-10-21-faturamento-bpa-prova-tecnica.md`.

## Formato
- Texto ASCII (bytes 0x20–0x7E), largura fixa, todo registro termina em CR+LF (inclusive o último).
- `NUM`: só dígitos, zeros à esquerda. `ALFA`: espaços à direita. Campo opcional sem dado: brancos.
- Um cabeçalho `01` seguido das linhas `02` (BPA-C) e depois `03` (BPA-I).
- Texto livre (órgãos, nome, bairro): maiúsculas sem acento, só letras e espaço, espaços colapsados,
  no máximo o tamanho do campo (o nome do paciente é cortado em 30, como no BPA Magnético).
- Nome do download: `bpa-<CNES>-<AAAAMM>-v<versão>.txt`; `Content-Type: text/plain; charset=us-ascii`.

## Folhas
- Uma série só, 001..999, 20 linhas por folha (`prd-seq` 01..20) nos dois instrumentos.
- BPA-C primeiro, ordenado por CBO, procedimento, idade e competência de realização.
- BPA-I depois, agrupado por profissional (CNS + CBO, nessa ordem): **folha nova a cada profissional**;
  dentro do grupo, por data, procedimento e id do procedimento.
- `cbc-lin` = número de linhas `02` + `03`; `cbc-flh` = número de folhas. Mais de 999 folhas: o
  fechamento é recusado (`too_many_sheets`), nunca cortado.

## Campo de controle
`(Σ (código do procedimento como inteiro + quantidade), sobre todas as linhas 02 e 03) mod 1111 + 1111`.

## Competências
- Cabeçalho (`cbc-mvm`): competência de processamento = a do fechamento.
- Linhas (`prd-cmp`): competência de realização = mês da data do procedimento. Procedimento gravado
  depois do fechamento da competência dele entra no arquivo da próxima competência aberta (até 3
  competências anteriores, regra do BPA 04.13).

## Origem dos dados
- BPA-C agrega por CNES × competência de realização × CBO × procedimento × idade (anos completos na data).
- BPA-I item a item. Paciente identificado por **um** documento: com CPF, `prd_cpf_pcnte` preenchido,
  `Prd-cnspac` em brancos e `prd_sem_cpf` = `N`; **sem CPF** (paciente do cadastro territorial, módulo 24a,
  ADR 0042), CNS em `Prd-cnspac`, `prd_cpf_pcnte` em brancos e `prd_sem_cpf` = `S`. Paciente sem CPF e sem CNS
  não entra no arquivo: é pendência (`missing_patient_id`).
- Sexo `F`/`M`; IBGE de residência = 6 primeiros dígitos do IBGE da cidade; caráter `01` eletivo, `02` urgência;
  raça/cor (`01`..`05`, sem `99`) e etnia (só quando `05`) do cadastro do paciente; CEP, endereço,
  complemento, número (`SN` sem número) e bairro do cadastro do paciente (endereço em maiúsculas ASCII com
  letras, dígitos e espaço); telefone do par do wpda quando houver; nacionalidade, serviço, classificação,
  equipe, CNPJ de OPM, código de logradouro, e-mail, INE e situação de rua em brancos; `prd-org` = `BPA`;
  `cbc_versao` = `ROTASAUDE`. Paciente sem raça/cor ou sem endereço não entra no arquivo: é pendência
  (`missing_race_color`, `missing_address`) — decisão D-U1 do contrato §12.
- Cabeçalho: órgão de origem (até 30), CNPJ de origem (14 dígitos, só numérico), órgão de destino (até 40) e
  indicador `M`/`E` e a sigla do órgão (até 6, opcional; brancos sem ela) vêm da configuração de faturamento da cidade.

## Layout

### Cabeçalho `01` (130 posições + CR+LF = 132)

| Seq | Nome | Obr | Tam | Ini | Fim | Tipo | Preenchimento | O que o Rota Saúde grava |
|---|---|---|---|---|---|---|---|---|
| 1 | cbc-hdr | | 2 | 1 | 2 | NUM | `01` | `01` |
| 2 | cbc-hdr | | 5 | 3 | 7 | ALFA | `#BPA#` | `#BPA#` |
| 3 | cbc-mvm | | 6 | 8 | 13 | NUM | ano e mês de **processamento**, AAAAMM | competência do fechamento (`billing_periods.competence`) |
| 4 | cbc-lin | | 6 | 14 | 19 | NUM | número de linhas do BPA gravadas, zeros à esquerda | quantidade de linhas `02` + `03` (sem o cabeçalho) |
| 5 | cbc-flh | | 6 | 20 | 25 | NUM | quantidade de folhas gravadas | total de folhas (BPA-C e BPA-I numa série só) |
| 6 | cbc-smt-vrf | | 4 | 26 | 29 | NUM | campo de controle, domínio 1111..2221 | ver "Campo de controle" |
| 7 | cbc-rsp | | 30 | 30 | 59 | ALFA | nome do órgão de origem responsável | `billing_settings.origin_name` em maiúsculas ASCII |
| 8 | cbc-sgl | | 6 | 60 | 65 | ALFA | sigla do órgão de origem (padrão brancos) | `billing_settings.origin_acronym` em maiúsculas ASCII; brancos sem ela (B10 do dashboard) |
| 9 | cbc-cgccpf | | 14 | 66 | 79 | NUM | CNPJ/CPF do prestador ou órgão público | `billing_settings.origin_cnpj` (só numérico; Review Focus 5) |
| 10 | cbc-dst | | 40 | 80 | 119 | ALFA | nome do órgão de saúde destino | `billing_settings.destination_body` em maiúsculas ASCII |
| 11 | cbc-dst-in | | 1 | 120 | 120 | ALFA | `M` municipal, `E` estadual | `billing_settings.management` |
| 12 | cbc_versao | | 10 | 121 | 130 | ALFA | versão do sistema, livre | `ROTASAUDE` + 1 branco |
| 13 | cbc-fim | | 2 | 131 | 132 | | CR+LF | CR+LF |

### Linha `02` — BPA-C (48 posições + CR+LF = 50)

| Seq | Nome | Obr | Tam | Ini | Fim | Tipo | Preenchimento | O que o Rota Saúde grava |
|---|---|---|---|---|---|---|---|---|
| 1 | prd-ident | | 2 | 1 | 2 | NUM | `02` | `02` |
| 2 | prd-cnes | X | 7 | 3 | 9 | NUM | CNES (último dígito é DV) | CNES do estabelecimento |
| 3 | prd-cmp | X | 6 | 10 | 15 | NUM | competência de **realização**, AAAAMM | mês de `performed_on` |
| 4 | Prd_cbo | | 6 | 16 | 21 | ALFA | CBO do profissional | `cbo_code` |
| 5 | prd-flh | X | 3 | 22 | 24 | NUM | folha, 001..999 | folha da série |
| 6 | prd-seq | | 2 | 25 | 26 | NUM | linha na folha, **01..20** | 01..20 |
| 7 | prd-pa | | 10 | 27 | 36 | NUM | procedimento (último dígito é DV) | `sigtap_code` |
| 8 | prd-ldade | | 3 | 37 | 39 | NUM | idade, 0 a 130 anos | idade em anos completos na data |
| 9 | prd-qt | | 6 | 40 | 45 | NUM | quantidade | soma das quantidades do grupo |
| 10 | prd-org | | 3 | 46 | 48 | ALFA | origem: `BPA` SIA/SUS, `PNI`, `SIE`, `SIB`, `MIN`, `PAC`, `SCL`, `EXT` outros sistemas | `BPA` (Divergência F6) |
| 11 | prd-fim | | 2 | 49 | 50 | | CR+LF | CR+LF |

### Linha `03` — BPA-I (351 posições + CR+LF = 353)

| Seq | Nome | Obr | Tam | Ini | Fim | Tipo | Preenchimento | O que o Rota Saúde grava |
|---|---|---|---|---|---|---|---|---|
| 1 | prd-ident | | 2 | 1 | 2 | NUM | `03` | `03` |
| 2 | prd-cnes | X | 7 | 3 | 9 | NUM | CNES | CNES do estabelecimento |
| 3 | prd-cmp | X | 6 | 10 | 15 | NUM | competência de realização | mês de `performed_on` |
| 4 | Prd_cnsmed | X | 15 | 16 | 30 | NUM | CNS do profissional com DV válido | `professionals.cns` do momento do fechamento |
| 5 | Prd_cbo | X | 6 | 31 | 36 | ALFA | CBO | `cbo_code` |
| 6 | Prd_dtaten | | 8 | 37 | 44 | NUM | data de atendimento AAAAMMDD | `performed_on` |
| 7 | prd-flh | X | 3 | 45 | 47 | NUM | folha 001..999 | folha da série |
| 8 | prd-seq | | 2 | 48 | 49 | NUM | linha na folha, **01..99** | 01..20 (folha de 20, como o BPA-C) |
| 9 | prd-pa | | 10 | 50 | 59 | NUM | procedimento | `sigtap_code` |
| 10 | Prd-cnspac | | 15 | 60 | 74 | NUM | CNS do paciente (obrigatório quando o procedimento exige) | CNS do paciente **só quando ele não tem CPF**; com CPF, **brancos** (nota 2 do PDF: um documento só) |
| 11 | Prd-sexo | | 1 | 75 | 75 | ALFA | `M` ou `F` (`I` aceito desde 01/2026, LEIAME 04.11) | `F`/`M` do paciente |
| 12 | Prd-ibge | | 6 | 76 | 81 | NUM | IBGE de residência (6 dígitos, sem o DV) | 6 primeiros dígitos de `city_profile.ibge_code` |
| 13 | Prd-cid | | 4 | 82 | 85 | ALFA | CID-10 | `cid10` sem ponto ou brancos |
| 14 | prd-ldade | | 3 | 86 | 88 | NUM | idade 0..130 | anos completos na data |
| 15 | prd-qt | | 6 | 89 | 94 | NUM | quantidade | `quantity` |
| 16 | Prd-caten | | 2 | 95 | 96 | NUM | caráter de atendimento | `01` eletivo, `02` urgência |
| 17 | Prd-naut | | 13 | 97 | 109 | NUM | número da autorização | brancos |
| 18 | prd-org | | 3 | 110 | 112 | ALFA | origem | `BPA` |
| 19 | prd-nmpac | | 30 | 113 | 142 | ALFA | nome completo do paciente | `patients.full_name`, maiúsculas ASCII, cortado em 30 (Desvio 6) |
| 20 | prd-dtnasc | | 8 | 143 | 150 | NUM | nascimento AAAAMMDD | `patients.birth_date` |
| 21 | prd-raca | x | 2 | 151 | 152 | NUM | `01`..`05`, `99` sem informação | `patients.race_color` (`01`..`05`; sem ele, pendência `missing_race_color` — D-U1) |
| 22 | prd-etnia | | 4 | 153 | 156 | NUM | só se raça = 05; senão brancos | `patients.ethnicity` quando `05`; senão brancos |
| 23 | prd-nac | | 3 | 157 | 159 | NUM | nacionalidade (quando preenchido) | brancos |
| 24 | prd_srv | | 3 | 160 | 162 | NUM | serviço (quando o procedimento exige) | brancos (spec §2: não criticado nesta entrega) |
| 25 | prd_clf | | 3 | 163 | 165 | NUM | classificação (idem) | brancos |
| 26 | prd_equipe_Seq | | 8 | 166 | 173 | NUM | sequência da equipe | brancos |
| 27 | prd_equipe_Area | | 4 | 174 | 177 | NUM | área da equipe | brancos |
| 28 | prd_cnpj | | 14 | 178 | 191 | NUM | CNPJ da empresa de manutenção/adaptação de OPM | brancos |
| 29 | prd_cep_pcnte | | 8 | 192 | 199 | NUM | CEP | `patients.address_zip` (sem endereço completo, pendência `missing_address` — D-U1) |
| 30 | prd_lograd_pcnte | | 3 | 200 | 202 | NUM | código do logradouro | brancos (o cadastro não tem a tabela DNE; risco no runbook) |
| 31 | prd_end_pcnte | | 30 | 203 | 232 | ALFA | endereço | `patients.address_street` (maiúsculas ASCII, letras e dígitos, até 30) |
| 32 | prd_compl_pcnte | | 10 | 233 | 242 | ALFA | complemento | `patients.address_complement` (até 10) |
| 33 | prd_num_pcnte | | 5 | 243 | 247 | ALFA | número (`SN`/`00` sem número) | `patients.address_number` (até 5; `SN` sem número) |
| 34 | prd_bairro_pcnte | | 30 | 248 | 277 | ALFA | bairro | `patients.address_district` (até 30); sem ele, o bairro do par do wpda |
| 35 | prd_ddtel_pcnte | | 11 | 278 | 288 | NUM | telefone; senão brancos | telefone do par sem o 55 (10–11 dígitos) quando houver |
| 36 | prd_email_pcnte | | 40 | 289 | 328 | ALFA | e-mail | brancos |
| 37 | prd_ine | X | 10 | 329 | 338 | NUM | INE da equipe (desde 08/2015) | brancos (unidade não-APS, sem equipe; risco no runbook) |
| 38 | prd_cpf_pcnte | | 11 | 339 | 349 | NUM | CPF (obrigatório quando o procedimento exige) | `patients.cpf`; **brancos** quando o paciente não tem CPF |
| 38 | prd_situacao_rua | | 1 | 350 | 350 | ALFA | `N`/`S`, branco sem informação (desde 12/2024) | branco |
| 39 | prd_sem_cpf | | 1 | 351 | 351 | ALFA | `N`/`S`, branco sem informação (desde **07/2026**) | `N` com CPF; `S` sem CPF (paciente pelo CNS) |
| 40 | prd-fim | | 2 | 352 | 353 | | CR+LF | CR+LF |

(O PDF repete o número 38 em duas linhas; as posições são as da tabela.)

### Campo de controle (observação do PDF)

1. Somar o código de todos os procedimentos + a quantidade (de toda linha `02` e `03`);
2. resto da divisão por 1111;
3. somar 1111. Resultado sempre em 1111..2221.

Implementação: `(Σ (sigtap_code.to_i + quantity)) % 1111 + 1111`.

### "Sem informação" e notas do PDF

Notas do PDF, descritivas. O que o Rota Saúde grava está em 'Origem dos dados' e na última coluna das tabelas: raça/cor nunca `99`; número sem número sempre `SN` (nunca `00`).

- Raça/cor `99` = sem informação; etnia em brancos quando raça ≠ 05; situação de rua e "sem CPF" em branco quando não há informação; número do endereço `SN`/`00` quando não há número.
- Nota 1 do PDF: o campo não pode ser editado pelo usuário. Nota 2: **o paciente é identificado por um documento só — CPF ou CNS, nunca os dois.**

### O que mudou desde o layout de 2020 (FEHOSP 09/2020, reproduzido na pesquisa §2.2)

| Versão do BPA | Mudança | Efeito aqui |
|---|---|---|
| 03.01 (31/03/2023) | Exclusão do `99 — Sem informação` em raça/cor a partir da competência 04/2023 (Portaria GM/MS 344/2017); o PDF de 2026 ainda lista o `99` | D-U1: raça/cor no cadastro do paciente, sem `99`; ausente = pendência `missing_race_color` |
| 04.00 (09/04/2024) | Campo **CPF do paciente** (`prd_cpf_pcnte`, 11) na exportação e na importação; a linha `03` passa de 338 para 349 posições | CPF em 339–349 |
| 04.06/04.07 (10–11/2024) | CPF e CNS do paciente nunca no mesmo atendimento | CNS do paciente em brancos |
| 04.08 (02/12/2024) | `prd_situacao_rua` (posição 350), competência 12/2024 | branco |
| 04.11 (23/01/2026) | Sexo `I` (indeterminado) aceito | só `F`/`M` saem (o cadastro só tem esses) |
| 04.13 (05/05/2026) | Data de realização: competência atual até **3 competências anteriores** | `invalid_date` fora dessa janela (Divergência F4) |
| 04.14 (22/05/2026) | Atributos SIGTAP "CPF obrigatório" (aceita só CPF) e "CNS obrigatório" (aceita CNS ou CPF) | CPF quando há; sem CPF, CNS (satisfaz "CNS obrigatório"; "CPF obrigatório" usa a exceção `prd_sem_cpf`) |
| **05.00 (07/07/2026)** | `prd_sem_cpf` "Pessoa sem CPF/Registro Civil" (posição 351), exceção ao atributo SIGTAP `058 — Obrigatório CPF`; "registros com crítica não são exportados para o SIA" | `N` com CPF, `S` sem CPF; linha `03` com 351 posições |
| 02.68 (2014, já antes de 2020) | 999 folhas × 99 linhas no BPA-I | folha de 20 no BPA-I também (spec §6) |
| 02.89 (2018) | Sexo diferente do sugerido na SIGTAP deixou de impedir o registro | Divergência F5 (`sex_not_allowed` continua, como o contrato manda) |
| 02.59/02.60 (2013) | CEP, logradouro, endereço, número e bairro passam a ser criticados | D-U1: endereço no cadastro do paciente; incompleto = pendência `missing_address` |

## Exemplos (`examples/`)
Gerados por `tools/bpa_oracle.py` (implementação independente do layout) — `SHA256SUMS` fixa o conteúdo:
- `bpa-c-21-lines.txt`: 21 linhas BPA-C, duas folhas (20 + 1), controle 1581.
- `bpa-i-25-lines.txt`: 25 linhas BPA-I de dois profissionais em três folhas (3; 20 + 2), acentos,
  apóstrofo, nome com mais de 30 letras, controle 2131.
- `bpa-mixed.txt`: 2 BPA-C e 2 BPA-I, folhas 001 e 002, controle 1617.
O api compara o seu gerador byte a byte com cópias destes arquivos (`apps/api/spec/fixtures/billing/`).
Os exemplos têm só pacientes com CPF; o caminho sem CPF (v1.1.0) é coberto pelos specs do api.
Regerar: `python3 -I billing/tools/bpa_oracle.py billing/examples > billing/examples/SHA256SUMS`.

## Fora deste perfil
APAC, RAAS, OCI, conciliação do retorno do SIA. Importação real no BPA Magnético: gate de go-live.
