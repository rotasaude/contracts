# protocols — JSON Schema da definição

`schema.json` é o contrato único da definição de protocolo (ADR 0009), consumido pelo
motor Ruby (`Protocols::Validator`) e pelo preview TS. Versionado por `protocols-vX.Y.Z`.

## Exemplos

`examples/` guarda definições válidas e inválidas. `examples/manifest.json` diz, por
arquivo, `valid` ou o erro esperado no formato `<data_pointer> <type>` do
`json_schemer` (o mesmo validador do `api`). Exemplo novo entra no manifesto no mesmo
commit da mudança de schema que ele prova.

Para verificar, a partir da raiz do monorepo, com o compose de pé (o container do
`api` só monta `apps/api`, por isso tudo entra pela entrada padrão; caminhos depois do
manifesto são casos extras esperados `valid`):

```bash
python3 -c '
import json, os, sys
schema_path, manifest_path, extras = sys.argv[1], sys.argv[2], sys.argv[3:]
base = os.path.dirname(manifest_path)
cases = [dict(c, doc=json.load(open(os.path.join(base, c["file"])))) for c in json.load(open(manifest_path))["cases"]]
cases += [{"file": p, "expect": "valid", "doc": json.load(open(p))} for p in extras]
print(json.dumps({"schema": json.load(open(schema_path)), "cases": cases}))
' contracts/protocols/schema.json contracts/protocols/examples/manifest.json apps/api/config/city_templates/triage_respiratoria.json \
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
