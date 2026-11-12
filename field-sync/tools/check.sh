#!/usr/bin/env bash
# Valida field-sync/examples/manifest.json contra os esquemas com o
# json_schemer do api. Rode da raiz do monorepo, com o compose de pé.
# Uso: field-sync/tools/check.sh [esquema.json ...]   (sem argumento: todas as suítes)
set -euo pipefail
dir="$(cd "$(dirname "$0")/.." && pwd)"
python3 -c '
import json, os, sys
d, only = sys.argv[1], set(sys.argv[2:])
ex = os.path.join(d, "examples")
m = json.load(open(os.path.join(ex, "manifest.json"), encoding="utf-8"))
suites = []
for s in m["suites"]:
    if only and s["schema"] not in only:
        continue
    cases = [dict(c, doc=json.load(open(os.path.join(ex, c["file"]), encoding="utf-8"))) for c in s["cases"]]
    suites.append({"schema": s["schema"], "schema_doc": json.load(open(os.path.join(d, s["schema"]), encoding="utf-8")), "cases": cases})
if not suites or any(not s["cases"] for s in suites):
    sys.exit("nenhuma suite ou suite sem casos")
print(json.dumps({"suites": suites}))
' "$dir" "$@" \
| docker compose exec -T -w /rails api bundle exec ruby -rjson -rjson_schemer -e '
input = JSON.parse(STDIN.read)
total = 0
passed = 0
input["suites"].each do |s|
  schemer = JSONSchemer.schema(s["schema_doc"])
  s["cases"].each do |c|
    total += 1
    errors = schemer.validate(c["doc"]).map { |e| p = e["data_pointer"]; "#{p.empty? ? "(root)" : p} #{e["type"]}" }.uniq
    ok = c["expect"] == "valid" ? errors.empty? : errors.include?(c["expect"])
    passed += 1 if ok
    puts "#{ok ? "ok  " : "FAIL"} #{s["schema"]} #{c["file"]} — esperado: #{c["expect"]}; obtido: #{errors.empty? ? "valid" : errors.join(" | ")}"
  end
end
puts "#{passed}/#{total} casos"
exit(passed == total ? 0 : 1)'
