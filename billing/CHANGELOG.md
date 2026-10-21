# Changelog — billing

## billing-v1.0.0 — 2026-10-21 (não publicada até a tag)

Primeira versão (ADR 0039, módulo 22): perfil do arquivo de interface do BPA Magnético (layout do
DATASUS de 09/07/2026, BPA 05.00) — cabeçalho `01`, BPA-C `02`, BPA-I `03` com CPF do paciente e
"pessoa sem CPF"; folhas de 20 numa série só; campo de controle; exemplos golden gerados pelo oráculo
`tools/bpa_oracle.py`.
