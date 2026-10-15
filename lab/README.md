# lab — laboratório municipal

Contratos do módulo 21b (laboratório municipal, ADR 0037).

| Arquivo | O que é |
|---|---|
| `lab-report-v1.json` | `rotasaude.lab_report.v1`: JSON canônico do laudo, congelado na liberação. É o que a assinatura ICP (CAdES) cobre e de onde o PDF sai. JSON Schema 2020-12, **fechado** (`additionalProperties: false`). |
| `hl7-v2-profile.md` | `rotasaude.lab.hl7.v1`: perfil HL7 v2.5.1 da entrada do middleware do fornecedor (`POST /hl7/v2`): `QBP^Q11` → `RSP^K11` (lista de trabalho) e `OUL^R22` → `ACK^R22` (resultado). |
| `examples/` | Laudo válido e inválido, e uma mensagem ER7 por caso do perfil, listados em `examples/manifest.json`. |

## Regras

- **Laudo fechado e sem CPF.** O paciente vai por nome, nascimento, sexo biológico e
  número de registro (= número da requisição, 8 dígitos). Endereço e telefone do
  laboratório são obrigatórios (RDC 978/2025, art. 167, II). `key` no componente e
  `support_laboratory` (sempre `null` no 21b; arts. 129/169) são a Divergência D16.
  Liberador e responsável técnico saem como `council`, `council_uf`,
  `council_number` (no banco, `council_state` e `registration_number` do módulo 10).
- **HL7: nosso código vai em `ERR-5`** (Divergência D1): `ERR-3` é o código da tabela
  0357. `ERR` repete, um por recusa.
- **HL7: o componente vai em `OBX-3`** (`analyte_key^nome^99RSL`) e o exame em
  `OBR-4` (`instrument_test_code`) — Divergência D2.
- **`SPM-4`** (obrigatório na v2.5.1) = `material` da versão do exame, como código e
  texto.
- **Tudo ou nada.** Uma `OUL^R22` com vários `SPM`/`OBR`/`OBX` entra inteira ou é
  recusada inteira (`AE`, um `ERR` por problema). Nenhum resultado é liberado sozinho.
- **Idempotência.** `MSH-10` já aceito (`AA`) do mesmo token → `AA` sem efeito;
  mensagem recusada não é guardada e pode ser reenviada com o mesmo `MSH-10`.
- **Sem dado de paciente** no `RSP^K11` (sem `PID`), no `ACK` e no `ERR`.
- Os `.hl7` têm `\r` (CR) real entre os segmentos e nenhum `\n`; gere com `printf`,
  nunca com editor que troque o fim de linha (`od -c` confere).

## Consumo

O `api` copia `lab-report-v1.json` para `config/lab/` e prende o SHA-256 do arquivo
commitado; os `.hl7` viram fixtures dos testes (`spec/fixtures/lab/`). Mudou um dos
dois? Atualize os lugares no mesmo ciclo, com entrada no CHANGELOG.

## Verificação

A partir da raiz do monorepo (usa o `json_schemer` do `api`):

```bash
docker compose run --rm --no-deps -v "$PWD/contracts:/contracts" -w /rails api bundle exec ruby -rjson -rjson_schemer -e '
m = JSON.parse(File.read("/contracts/lab/examples/manifest.json"))
m["suites"].each do |s|
  s["cases"].each do |c|
    path = "/contracts/lab/examples/#{c["file"]}"
    if s["schema"]
      errs = JSONSchemer.schema(JSON.parse(File.read("/contracts/lab/#{s["schema"]}"))).validate(JSON.parse(File.read(path)))
                        .map { |e| "#{e["data_pointer"]} #{e["type"]} #{e.dig("details", "missing_keys")}" }
      puts "#{c["file"]}: #{errs.empty? ? "valid" : errs.uniq.join(" | ")}"
    else
      raw = File.binread(path); segs = raw.split("\r")
      puts "#{c["file"]}: #{segs.first.split("|")[8]} #{segs.find { |x| x.start_with?("MSA") }&.split("|")&.at(1)} lf=#{raw.include?("\n")}"
    end
  end
end'
```

Esperado: `lab-report-advanced.json: valid`; `invalid-lab-report-without-lead.json`
com `required ["technical_lead"]` na raiz; uma linha por `.hl7` com o `MSH-9` e o
`MSA-1` do manifesto, e `lf=false`.
