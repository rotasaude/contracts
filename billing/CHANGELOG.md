# Changelog — billing

## billing-v1.1.0 — 2026-10-27

Paciente sem CPF no BPA-I (módulo 24a, ADR 0042; api `10c2ab9`): CNS em `Prd-cnspac` (60–74),
`prd_cpf_pcnte` (339–349) em brancos e `prd_sem_cpf` (351) = `S`; com CPF nada muda (`N`, CNS em brancos).
Paciente sem CPF e sem CNS não entra no arquivo (pendência `missing_patient_id`). `prd_situacao_rua` (350)
continua em branco. Exemplos golden inalterados (só pacientes com CPF; mesmos bytes).

## billing-v1.0.0 — 2026-10-21 (não publicada até a tag)

Primeira versão (ADR 0039, módulo 22): perfil do arquivo de interface do BPA Magnético (layout do
DATASUS de 09/07/2026, BPA 05.00) — cabeçalho `01`, BPA-C `02`, BPA-I `03` com CPF do paciente e
"pessoa sem CPF"; folhas de 20 numa série só; campo de controle; exemplos golden gerados pelo oráculo
`tools/bpa_oracle.py`.
