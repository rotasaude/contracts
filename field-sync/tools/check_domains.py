#!/usr/bin/env python3
"""Conferência entre os arquivos de field-sync/ (sem docker).

1. Todo $defs repetido em dois esquemas é igual.
2. Cada enum do pedido de envio é exatamente o domínio de domains-v1.json,
   e as faixas das medidas, os tamanhos máximos das listas e os limites da
   coordenada (location) são os de domains-v1.json; o mesmo vale para vector_control
   (listas, limites e regras do controle vetorial, 35a).
3. Todo error dos exemplos válidos de resposta está em errors.item.
4. regras-da-atividade: collective_activity.rules tem as sete chaves da referência (REFERENCE_RULE_KEYS, as do api),
   by_type cobre os tipos de atividade com valores válidos, e o esquema da referência as exige.
5. logradouro-em-codigo: todo street_type dos exemplos é código DNE de três dígitos (Q3), nunca o rótulo.
--release: falha também com "proof": null (a tag só sai depois da prova técnica do api).
Uso: python3 field-sync/tools/check_domains.py [--release]
"""
import ast
import itertools
import json
import os
import re
import sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS = ["session-response-v1.json", "upload-request-v1.json", "upload-response-v1.json", "changes-response-v1.json",
           "reference-response-v1.json"]

# As sete chaves de collective_activity.rules que o api serve na referência, na ordem do api
# (CollectiveActivities::Json.domains[:rules]). make_examples.py tem a mesma constante; a guarda confere.
REFERENCE_RULE_KEYS = ["list_max", "by_type", "health_topics_with_meeting_topic", "practices_only_in_type",
                       "procedure_practices", "smoking_practices", "participant_measurements"]


def find_key(node, key):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key:
                yield v
            yield from find_key(v, key)
    elif isinstance(node, list):
        for v in node:
            yield from find_key(v, key)


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
        "outro_procedimento_coletivo": (codes(ca["outro_procedimento_coletivo"]), sorted(ca_props["procedure_code"]["enum"])),
        "reasons_max": ([hv["rules"]["reasons_max"]], [req["home_visit_body"]["properties"]["reasons"]["maxItems"]]),
    }
    for key, limit in ca["rules"]["list_max"].items():
        pairs[f"list_max.{key}"] = ([limit], [ca_props[key]["maxItems"]])
    for key, rule in hv["rules"]["measurements"].items():
        if "min" in rule:
            pairs[f"measurements.{key}"] = ([rule["min"], rule["max"]], [meas[key]["minimum"], meas[key]["maximum"]])
    loc, loc_dom = req["location"], dom["location"]
    lp, acc = loc["properties"], dom["location"]["accuracy_m"]
    pairs["location"] = (
        [loc_dom["latitude"]["min"], loc_dom["latitude"]["max"], loc_dom["longitude"]["min"], loc_dom["longitude"]["max"],
         10 ** -loc_dom["decimals"], 10 ** -loc_dom["decimals"], acc["min"], acc["max"], 10 ** -acc["decimals"],
         sorted(loc_dom["sources"]), acc["required_for"], ["accuracy_m"]],
        [lp["latitude"]["minimum"], lp["latitude"]["maximum"], lp["longitude"]["minimum"], lp["longitude"]["maximum"],
         lp["latitude"]["multipleOf"], lp["longitude"]["multipleOf"], lp["accuracy_m"]["minimum"], lp["accuracy_m"]["maximum"],
         lp["accuracy_m"]["multipleOf"], sorted(lp["source"]["enum"]), [loc["if"]["properties"]["source"]["const"]],
         loc["then"]["required"]])
    vc = dom["vector_control"]
    vi = req["vector_inspection"]["properties"]
    chg = s["changes-response-v1.json"]["$defs"]

    def nn(enum):
        return sorted(x for x in enum if x is not None)

    hv_vec = chg["household_vector"]["properties"]
    ovi = chg["ovitrap"]["properties"]
    last_reading = next(o for o in ovi["last_reading"]["anyOf"] if o.get("type") == "object")
    charges = req["vector_measure"]["properties"]["charges"]
    sample = req["vector_sample"]["properties"]
    vc_rules = vc["rules"]
    pairs.update({
        "vector_control.activities": (codes(vc["activities"]), sorted(vi["activity"]["enum"])),
        "vector_control.work_types": (codes(vc["work_types"]), sorted(vi["work_type"]["enum"])),
        "vector_control.situations": (codes(vc["situations"]), sorted(vi["situation"]["enum"])),
        "vector_control.situations(changes)": (codes(vc["situations"]), nn(hv_vec["last_situation"]["enum"])),
        "vector_control.risk_classes": (codes(vc["risk_classes"]), sorted(vi["risk_class"]["enum"])),
        "vector_control.risk_classes(changes)": (codes(vc["risk_classes"]), nn(hv_vec["risk_class"]["enum"])),
        "vector_control.deposit_groups": (codes(vc["deposit_groups"]), sorted(req["deposit_group"]["enum"])),
        "vector_control.measure_methods": (codes(vc["measure_methods"]), sorted(req["vector_measure"]["properties"]["method"]["enum"])),
        "vector_control.ovitrap_conditions": (codes(vc["ovitrap_conditions"]), sorted(req["ovitrap_collection_body"]["properties"]["condition"]["enum"])),
        "vector_control.ovitrap_conditions(changes)": (codes(vc["ovitrap_conditions"]), sorted(last_reading["properties"]["condition"]["enum"])),
        "vector_control.ovitrap_statuses": (codes(vc["ovitrap_statuses"]), sorted(ovi["status"]["enum"])),
        "vector_control.liraa_item_statuses": (codes(vc["liraa_item_statuses"]), sorted(chg["liraa_item"]["properties"]["status"]["enum"])),
        "vector_control.transmission_block_statuses": (codes(vc["transmission_block_statuses"]), sorted(chg["transmission_block"]["properties"]["status"]["enum"])),
        "vector_control.limits": (
            [vc["limits"]["deposit_count_max"], vc["limits"]["charges_max"], vc["limits"]["samples_max"], vc["limits"]["samples_max"],
             vc["limits"]["larvae_collected_max"], vc["limits"]["measures_max"], len(vc["deposit_groups"]), 10 ** -vc_rules["charges_decimals"]],
            [req["deposit_count"]["maximum"], charges["maximum"], sample["number"]["maximum"], vi["samples"]["maxItems"],
             sample["larvae_collected"]["maximum"], vi["measures"]["maxItems"], vi["deposits"]["maxItems"], charges["multipleOf"]]),
        "vector_control.rules": (
            [[c for c in vc_rules["registrar_cbos"] if c not in hv["rules"]["registrar_cbos"]],
             sorted(k for k in vc_rules["derived_reasons"] if int(k) not in req["visit_reason"]["enum"]),
             sorted(t for v in vc_rules["activity_property_types"].values() for t in v if t not in req["property_type"]["enum"])],
            [[], [], []]),
    })
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

    rules = ca["rules"]
    why = []
    # Lê a constante do gerador pela AST: importar o make_examples monta as suítes, e isso depende destas mesmas regras.
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_examples.py"), encoding="utf-8") as f:
        gen_keys = next((ast.literal_eval(n.value) for n in ast.parse(f.read()).body if isinstance(n, ast.Assign)
                         and any(getattr(t, "id", None) == "REFERENCE_RULE_KEYS" for t in n.targets)), None)
    if gen_keys != REFERENCE_RULE_KEYS:
        why.append("REFERENCE_RULE_KEYS do gerador difere do desta guarda")
    missing = [k for k in REFERENCE_RULE_KEYS if k not in rules]
    if missing:
        why.append("faltam " + ", ".join(missing))
    by_type = rules.get("by_type")
    if isinstance(by_type, dict):
        want = sorted(str(c) for c in ca_props["activity_type"]["enum"])
        if sorted(by_type) != want:
            why.append(f"by_type tem os tipos {sorted(by_type)} e o pedido {want}")
        out = sorted({v for r in by_type.values() for v in r.values() if v not in ("required", "forbidden", "optional")})
        if out:
            why.append("by_type com valor fora de required/forbidden/optional: " + ", ".join(map(str, out)))
    ref_rules = s["reference-response-v1.json"].get("$defs", {}).get("collective_activity_rules")
    if ref_rules is not None and ref_rules.get("required") != REFERENCE_RULE_KEYS:
        why.append("$defs/collective_activity_rules.required difere de REFERENCE_RULE_KEYS")
    print("regras-da-atividade" if not why else "REGRAS DA ATIVIDADE: " + "; ".join(why))
    bad += why

    wrong = []
    for suite in manifest["suites"]:
        for case in suite["cases"]:
            for v in find_key(load(os.path.join("examples", case["file"])), "street_type"):
                if v is not None and not (isinstance(v, str) and re.fullmatch("[0-9]{3}", v)):
                    wrong.append(case["file"])
                    break
    print("logradouro-em-codigo" if not wrong else "LOGRADOURO FORA DO CODIGO: " + ", ".join(wrong))
    bad += wrong

    proof = dom["proof"]
    print("prova: " + ("pendente" if proof is None else f'{proof["api_commit"]} ({proof["date"]})'))
    if "--release" in sys.argv and proof is None:
        bad.append("proof")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
