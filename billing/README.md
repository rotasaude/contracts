# billing — arquivo de interface do BPA Magnético

Perfil do arquivo texto que o Rota Saúde gera no fechamento da competência (ADR 0039, módulo 22) e que
o faturista importa no BPA Magnético do DATASUS. Fonte de verdade do layout: [`bpa-interface.md`](bpa-interface.md).

| Arquivo | O que é |
|---|---|
| `bpa-interface.md` | perfil: formato, folhas, campo de controle, origem de cada campo, layout campo a campo |
| `tools/bpa_oracle.py` | segunda implementação do layout, só para gerar os exemplos (Python 3, stdlib) |
| `examples/*.txt` + `SHA256SUMS` | exemplos golden que o teste do api compara byte a byte |

Versão: `billing-v1.0.0`. Mudança de layout do DATASUS (acompanhar o `BPA_LEIAME.txt` a cada competência)
é MAJOR quando muda posição ou tamanho de campo; MINOR quando só acrescenta campo no fim da linha.
