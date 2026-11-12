#!/usr/bin/env python3
"""Conferência entre os arquivos de field-sync/ (sem docker).

1. Todo $defs repetido em dois esquemas é igual.
2. Cada enum do pedido de envio é exatamente o domínio de domains-v1.json,
   e as faixas das medidas são as de domains-v1.json.
3. Todo error dos exemplos válidos de resposta está em errors.item.
--release: falha também com "proof": null (a tag só sai depois da prova técnica do api).
Uso: python3 field-sync/tools/check_domains.py [--release]
"""
import itertools
import json
import os
import sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS = ["session-response-v1.json", "upload-request-v1.json", "upload-response-v1.json", "changes-response-v1.json"]


def load(name):
    with open(os.path.join(D, name), encoding="utf-8") as f:
        return json.load(f)


def main():
    bad = []
    s = {n: load(n) for n in SCHEMAS}
    for a, b in itertools.combinations(SCHEMAS, 2):
        for key in sorted(set(s[a].get("$defs", {})) & set(s[b].get("$defs", {}))):
            if s[a]["$defs"][key] != s[b]["$defs"][key]:
                bad.append(f"$defs/{key}: {a} != {b}")
    print("defs-iguais" if not bad else "DEFS DIFERENTES: " + "; ".join(bad))

    dom = load("domains-v1.json")
    req = s["upload-request-v1.json"]["$defs"]
    hv, ca = dom["home_visit"], dom["collective_activity"]
    ca_props = req["collective_activity_body"]["properties"]
    meas = req["visit_measurements"]["properties"]

    def codes(entries):
        return sorted(e["code"] for e in entries)

    pairs = {
        "motivo_visita": (sorted(i["code"] for g in hv["motivo_visita"] for i in g["items"]), sorted(req["visit_reason"]["enum"])),
        "desfecho": (codes(hv["desfecho"]), sorted(req["home_visit_body"]["properties"]["outcome"]["enum"])),
        "tipo_de_imovel": (codes(hv["tipo_de_imovel"]), sorted(req["property_type"]["enum"])),
        "tipo_glicemia": (codes(hv["tipo_glicemia"]), sorted(meas["glucose_type"]["enum"])),
        "turno": (codes(hv["turno"]), sorted(ca_props["shift"]["enum"])),
        "justificativa_nao_possui_cpf": (sorted(dom["patient"]["justificativa_nao_possui_cpf"]["codes"]), sorted(req["no_cpf_reason"]["enum"])),
        "sexo": (codes(dom["patient"]["sexo"]), sorted(req["new_patient"]["properties"]["sex"]["enum"])),
        "tipo_atividade_coletiva": (codes(ca["tipo_atividade_coletiva"]), sorted(ca_props["activity_type"]["enum"])),
        "temas_para_reuniao": (codes(ca["temas_para_reuniao"]), sorted(ca_props["meeting_topics"]["items"]["enum"])),
        "publico_alvo": (codes(ca["publico_alvo"]), sorted(ca_props["target_audience"]["items"]["enum"])),
        "temas_para_saude": (codes(ca["temas_para_saude"]), sorted(ca_props["health_topics"]["items"]["enum"])),
        "praticas_em_saude": (codes(ca["praticas_em_saude"]), sorted(ca_props["health_practices"]["items"]["enum"])),
    }
    for key, rule in hv["rules"]["measurements"].items():
        if "min" in rule:
            pairs[f"measurements.{key}"] = ([rule["min"], rule["max"]], [meas[key]["minimum"], meas[key]["maximum"]])
    diff = [k for k, (x, y) in pairs.items() if x != y]
    print("dominios-iguais" if not diff else "DOMINIOS DIFERENTES: " + ", ".join(diff))
    bad += diff

    known = set(dom["errors"]["item"])
    manifest = load(os.path.join("examples", "manifest.json"))
    unknown = []
    for suite in manifest["suites"]:
        if suite["schema"] != "upload-response-v1.json":
            continue
        for case in suite["cases"]:
            if case["expect"] != "valid":
                continue
            for r in load(os.path.join("examples", case["file"]))["results"]:
                if "error" in r and r["error"] not in known:
                    unknown.append(f'{case["file"]}: {r["error"]}')
    print("erros-conhecidos" if not unknown else "ERROS FORA DA LISTA: " + "; ".join(unknown))
    bad += unknown

    proof = dom["proof"]
    print("prova: " + ("pendente" if proof is None else f'{proof["api_commit"]} ({proof["date"]})'))
    if "--release" in sys.argv and proof is None:
        bad.append("proof")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
