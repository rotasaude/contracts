#!/usr/bin/env python3
"""Gera field-sync/examples/*.json e examples/manifest.json (determinístico).

Uso: python3 field-sync/tools/make_examples.py (de qualquer pasta).
Um defeito por arquivo inválido; o expect é o erro exato do json_schemer
("<data_pointer> <type>", "(root)" na raiz). Dados fictícios; os CPFs têm
dígito verificador válido e são inventados; o CNS 702000000000001 é
provisório (início 7) e inventado.
"""
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "examples")
DELETE = object()


def cu(n):
    return f"c0ffee{n:02d}-0000-4000-8000-{n:012d}"


TEAM = "3f1c2a4b-5d6e-4f70-8a9b-0c1d2e3f4a5b"
MA1 = "6a7b8c9d-0e1f-4a2b-8c3d-4e5f6a7b8c9d"
MA2 = "7b8c9d0e-1f2a-4b3c-9d4e-5f6a7b8c9d0e"
HH = "8c9d0e1f-2a3b-4c4d-8e5f-6a7b8c9d0e1f"
HH2 = "9e0f1a2b-3c4d-4e5f-8a6b-7c8d9e0f1a2b"
FAM = "9d0e1f2a-3b4c-4d5e-9f6a-7b8c9d0e1f2a"
PAT = "0e1f2a3b-4c5d-4e6f-8a7b-8c9d0e1f2a3b"
PAT2 = "1f2a3b4c-5d6e-4f7a-9b8c-9d0e1f2a3b4c"
PAT3 = "2b3c4d5e-6f7a-4b8c-9d0e-1f2a3b4c5d6e"
REG = "2a3b4c5d-6e7f-4a8b-8c9d-0e1f2a3b4c5d"
REG2 = "3c4d5e6f-7a8b-4c9d-8e0f-1a2b3c4d5e6f"
REG3 = "4d5e6f7a-8b9c-4d0e-9f1a-2b3c4d5e6f7a"
USER = "3b4c5d6e-7f8a-4b9c-9d0e-1f2a3b4c5d6e"
PROF = "4c5d6e7f-8a9b-4c0d-8e1f-2a3b4c5d6e7f"
PROF2 = "5d6e7f8a-9b0c-4d1e-9f2a-3b4c5d6e7f8a"
UNIT = "6e7f8a9b-0c1d-4e2f-8a3b-4c5d6e7f8a9b"
VISIT = "7f8a9b0c-1d2e-4f3a-9b4c-5d6e7f8a9b0c"
ACT = "8a9b0c1d-2e3f-4a4b-8c5d-6e7f8a9b0c1d"
FAM2 = "5e6f7a8b-9c0d-4e1f-8a2b-3c4d5e6f7a8b"
BLOCK = "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
BLOCK2 = "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e"
OVI = "c3d4e5f6-a7b8-4c9d-8e0f-2a3b4c5d6e7f"
OVI2 = "d5e6f7a8-b9c0-4d1e-8f2a-3b4c5d6e7f80"
LIRAA_ITEM = "d4e5f6a7-b8c9-4d0e-9f1a-3b4c5d6e7f8a"
SURVEY = "e5f6a7b8-c9d0-4e1f-8a2b-4c5d6e7f8a9b"
TBLOCK = "f6a7b8c9-d0e1-4f2a-9b3c-5d6e7f8a9b0c"
PRODUCT = "0a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"
PRODUCT2 = "1b2c3d4e-5f6a-4b7c-9d8e-0f1a2b3c4d5e"
VINSP = "2c3d4e5f-6a7b-4c8d-8e9f-1a2b3c4d5e6f"
MAP_SHA = "ab" * 32
REF_SHA = "cd" * 32
CURSOR = "eyJ2IjoxLCJzaW5jZSI6IjIwMjYtMTEtMTJUMTI6MDA6MDBaIn0"

TEAM_REF = {"id": TEAM, "ine": "0001234567", "name": "ESF Vila Nova"}
MA1_REF = {"id": MA1, "code": "03"}
ADDRESS = {"zip": "80010000", "street_type": "RUA", "street": "das Flores", "number": "120", "no_number": False,
           "complement": None, "neighborhood_id": None, "district": "Centro", "reference": "Perto da praça"}
NEW_PATIENT = {"full_name": "Benedita Aparecida Rocha", "birth_date": "1948-05-02", "sex": "female",
               "mother_name": "Maria José Rocha", "no_cpf_reason": "2", "cns": "702000000000001"}
WITHDRAWAL_REASON = "Visita registrada no domicílio errado."
LOC_GPS = {"latitude": -25.42847123, "longitude": -49.27325411, "accuracy_m": 8.5, "source": "gps"}
LOC_MAP = {"latitude": -25.42851, "longitude": -49.2733, "source": "map"}


def set_path(doc, path, value):
    cur = doc
    for key in path[:-1]:
        cur = cur[key]
    if value is DELETE:
        del cur[path[-1]]
    else:
        cur[path[-1]] = value
    return doc


def variant(base, path, value):
    return set_path(base(), path, value)


# ---------- GET /field/v1/session ----------

def session_acs():
    return {"contract": "field-sync-v1", "server_time": "2026-11-12T12:00:00Z",
            "user": {"id": USER, "name": "Rosângela Alves"},
            "professional": {"id": PROF, "cbo": "515105", "has_cns": True},
            "teams": [{"id": TEAM, "ine": "0001234567", "name": "ESF Vila Nova",
                       "micro_areas": [{"id": MA1, "code": "03", "name": "Vila Nova — rua das Flores", "scope": "responsible"}],
                       "out_of_area_allowed": True}],
            "features": {"home_visits": True, "collective_activities": True, "territory_registry": True},
            "min_date": "2026-10-01",
            "map": {"version": "2026-11-01", "size_bytes": 41234567, "sha256": MAP_SHA}, "reference_version": REF_SHA}


def session_agent():
    d = session_acs()
    d["user"]["name"] = "Carlos Menezes"
    d["professional"] = {"id": PROF2, "cbo": "515140", "has_cns": False}
    d["teams"][0]["micro_areas"] = [{"id": MA2, "code": "07", "name": "Jardim Esperança", "scope": "assigned"}]
    d["teams"][0]["out_of_area_allowed"] = False
    d["features"]["collective_activities"] = False
    return d


# ---------- POST /field/v1/uploads (pedido) ----------

def hv_resident():
    return {"team_id": TEAM, "occurred_at": "2026-11-12T09:40:00-03:00", "household_id": HH, "subject": "resident",
            "patient_id": PAT, "outcome": 1, "reasons": [11, 12], "shared": False,
            "measurements": {"systolic": 138, "diastolic": 88, "weight_kg": 81.5, "height_cm": 162.0,
                             "glucose_mg_dl": 142, "glucose_type": 2},
            "note": "Pediu para a equipe voltar à tarde."}


def hv_non_residential():
    return {"team_id": TEAM, "occurred_at": "2026-11-12T14:05:00-03:00", "micro_area_id": MA1, "property_type": "4",
            "subject": "none", "outcome": 1, "reasons": [34, 37], "shared": False}


def collective():
    return {"team_id": TEAM, "held_on": "2026-11-11", "shift": 2, "activity_type": 5,
            "place_text": "Salão da Associação de Moradores da Vila Nova",  # Q15
            "participants_count": 12, "target_audience": [12], "health_topics": [4],
            "health_practices": [20], "professionals": [{"professional_id": PROF2}],
            "participants": [{"patient_id": PAT, "altered_evaluation": True, "measurements": {"weight_kg": 81.5, "height_cm": 162.0}},
                             {"patient_client_uuid": cu(10), "altered_evaluation": False}]}


def collective_procedure():
    body = collective()
    body.update({"activity_type": 6, "health_practices": [30], "procedure_code": "0101050046"})  # Q37
    del body["health_topics"]
    return body


def household_update():
    return {"household_id": HH, "version": 3, "micro_area_id": MA1, "property_type": "1", "refused": False,
            "contact_phone": "41999990000", "address": copy.deepcopy(ADDRESS), "living_conditions": {}}


def registration_create():
    return {"patient_id": PAT2, "household_id": HH, "family_id": FAM, "is_responsible": False, "identification": {},
            "patient_demographics": {"race_color": "01", "ethnicity": None}, "sociodemographic": {},
            "health_conditions": {}, "refused": False}


def hv_new_household():
    visit = hv_resident()
    del visit["household_id"], visit["patient_id"], visit["measurements"], visit["note"]
    visit["household_client_uuid"] = cu(20)
    visit["patient_client_uuid"] = cu(10)
    return visit


def registration_same_batch():
    body = registration_create()
    del body["patient_id"], body["household_id"], body["family_id"]
    body["patient_client_uuid"] = cu(10)
    body["household_client_uuid"] = cu(20)
    return body


def item(n, kind, body):
    return {"client_uuid": cu(n), "type": kind, "body": body}


def up(*items):
    return {"items": list(items)}


def upload_hv():
    return up(item(1, "home_visit", hv_resident()))


def upload_hv_nr():
    return up(item(2, "home_visit", hv_non_residential()))


def upload_withdrawal():
    return up(item(3, "home_visit_withdrawal", {"visit_client_uuid": cu(1), "reason": WITHDRAWAL_REASON}))


def upload_ca():
    return up(item(4, "collective_activity", collective()))


def upload_ca_procedure():
    return up(item(8, "collective_activity", collective_procedure()))


def upload_patient():
    return up(item(5, "patient", {"new_patient": copy.deepcopy(NEW_PATIENT), "duplicates_reviewed": False}))


def upload_household():
    return up(item(6, "household", household_update()))


def upload_registration():
    return up(item(7, "individual_registration", registration_create()))


def upload_mixed():
    visit = hv_resident()
    del visit["patient_id"], visit["measurements"], visit["note"]
    visit["patient_client_uuid"] = cu(10)
    return up(item(10, "patient", {"new_patient": copy.deepcopy(NEW_PATIENT)}), item(11, "home_visit", visit),
              item(12, "collective_activity", collective()))


def upload_hv_new_household():
    household = household_update()
    del household["household_id"], household["version"]
    return up(item(10, "patient", {"new_patient": copy.deepcopy(NEW_PATIENT)}), item(20, "household", household),
              item(21, "home_visit", hv_new_household()))


def upload_registration_same_batch():
    household = household_update()
    del household["household_id"], household["version"]
    return up(item(10, "patient", {"new_patient": copy.deepcopy(NEW_PATIENT)}), item(20, "household", household),
              item(22, "individual_registration", registration_same_batch()))


def new_household():
    household = household_update()
    del household["household_id"], household["version"]
    return household


def family_new(responsible, members_count):
    return {"household_client_uuid": cu(30), "version": 1, "responsible": {"patient_client_uuid": responsible},
            "income_band": "3", "members_count": members_count, "living_since": "2026-11"}


def upload_family_new():
    registration = registration_create()
    del registration["patient_id"], registration["household_id"], registration["family_id"]
    registration.update({"patient_client_uuid": cu(31), "household_client_uuid": cu(30), "is_responsible": True})
    return up(item(30, "household", new_household()), item(31, "patient", {"new_patient": copy.deepcopy(NEW_PATIENT)}),
              item(32, "individual_registration", registration), item(33, "family", family_new(cu(31), 2)))


def upload_family_new_from_registration():  # Q26: o responsável cita o cadastro individual com new_patient
    registration = registration_create()
    del registration["patient_id"], registration["household_id"], registration["family_id"]
    registration.update({"new_patient": dict(NEW_PATIENT, social_name="Dita"), "household_client_uuid": cu(30),
                         "is_responsible": True})
    return up(item(30, "household", new_household()), item(35, "individual_registration", registration),
              item(36, "family", family_new(cu(35), 1)))


def upload_family_update():
    return up(item(34, "family", {"household_id": HH, "family_id": FAM, "version": 4, "income_band": "4",
                                  "members_count": 3, "living_since": "2019-03", "moved_out": False}))


def upload_household_location(location):
    return up(item(6, "household", dict(household_update(), location=location)))


def upload_hv_location(location=LOC_GPS):
    visit = hv_resident()
    visit["location"] = copy.deepcopy(location) if isinstance(location, dict) else location
    return up(item(1, "home_visit", visit))


def upload_hv_family_client_uuid():
    visit = hv_resident()
    del visit["patient_id"], visit["measurements"], visit["note"]
    visit.update({"subject": "family_responsible", "family_client_uuid": cu(33)})
    return up(upload_family_new()["items"][3], item(37, "home_visit", visit))


B = ["items", 0, "body"]
VI = B + ["vector_inspection"]

# ---------- 35a: vigilância ambiental (boletim e ovitrampas) ----------

def vi_worked():
    return {"activity": "li_t", "work_type": "routine", "situation": "worked", "educational_action": True,
            "entered_at": "2026-11-12T09:30:00-03:00", "left_at": "2026-11-12T09:52:00-03:00", "risk_class": "yellow",
            "deposits": [{"group": "A1", "existing": 3, "with_water": 2, "with_larvae": 1, "eliminated": 1, "treated": 1},
                         {"group": "D2", "existing": 4, "with_water": 2, "with_larvae": 1, "eliminated": 4, "treated": 0}],
            "measures": [{"method": "mechanical"}, {"method": "focal", "vector_product_id": PRODUCT, "charges": 2.25}],
            "samples": [{"number": 1, "deposit_group": "A1", "larvae_collected": 8},
                        {"number": 2, "deposit_group": "D2", "larvae_collected": 5}]}


def hv_ace():
    return {"team_id": TEAM, "occurred_at": "2026-11-12T09:40:00-03:00", "household_id": HH, "subject": "family_responsible",
            "family_id": FAM, "outcome": 1, "reasons": [], "shared": False, "vector_inspection": vi_worked()}


def hv_ace_pe():
    return {"team_id": TEAM, "occurred_at": "2026-11-12T14:05:00-03:00", "household_id": HH2, "subject": "none",
            "outcome": 1, "reasons": [], "shared": False,
            "vector_inspection": {"activity": "pe", "work_type": "routine", "situation": "worked", "educational_action": False,
                                  "entered_at": "2026-11-12T13:50:00-03:00", "left_at": "2026-11-12T14:20:00-03:00",
                                  "city_block_id": BLOCK,
                                  "deposits": [{"group": "D1", "existing": 12, "with_water": 5, "with_larvae": 0, "eliminated": 0, "treated": 5}],
                                  "measures": [{"method": "perifocal", "vector_product_id": PRODUCT2, "charges": 0.5}]}}


def hv_ace_closed():
    return {"team_id": TEAM, "occurred_at": "2026-11-12T10:15:00-03:00", "household_id": HH, "subject": "none",
            "outcome": 3, "reasons": [], "shared": False,
            "vector_inspection": {"activity": "liraa", "work_type": "routine", "situation": "closed", "educational_action": False,
                                  "entered_at": "2026-11-12T10:14:00-03:00", "left_at": "2026-11-12T10:16:00-03:00",
                                  "liraa_draw_item_id": LIRAA_ITEM}}


def upload_vi():
    return up(item(60, "home_visit", hv_ace()))


def upload_vi_pe():
    return up(item(61, "home_visit", hv_ace_pe()))


def upload_vi_closed():
    return up(item(62, "home_visit", hv_ace_closed()))


def ovi_installation():
    return {"household_id": HH, "number": "OVT-014", "consent": True, "installed_on": "2026-11-12"}


def upload_ovitrap_installation():
    return up(item(63, "ovitrap_installation", ovi_installation()))


def upload_ovitrap_collection():
    return up(item(66, "ovitrap_collection", {"ovitrap_id": OVI, "collected_on": "2026-11-12", "condition": "ok", "reinstall": True, "remove": False}),
              item(67, "ovitrap_collection", {"ovitrap_id": OVI2, "collected_on": "2026-11-12", "condition": "lost", "remove": True}))


def upload_ovitrap_same_batch():
    return up(item(64, "ovitrap_installation", {"household_id": HH, "number": "OVT-015", "consent": True, "installed_on": "2026-11-12"}),
              item(65, "ovitrap_collection", {"ovitrap_client_uuid": cu(64), "collected_on": "2026-11-17", "condition": "ok"}))


def upload_vi_8_deposits():
    d = vi_worked()
    d["deposits"] = [{"group": g, "existing": 0, "with_water": 0, "with_larvae": 0, "eliminated": 0, "treated": 0}
                     for g in ["A1", "A2", "B", "C", "D1", "D2", "E", "A1"]]
    d["samples"] = []
    return up(item(60, "home_visit", dict(hv_ace(), vector_inspection=d)))


def vr(n, kind, error, path=None):
    r = {"client_uuid": cu(n), "status": "rejected", "type": kind, "error": error}
    if path:
        r["path"] = path
    return r


def resp_vector_rejected():
    hv, oi, oc = "home_visit", "ovitrap_installation", "ovitrap_collection"
    rows = [(hv, "cbo_not_allowed", "vector_inspection"), (hv, "vector_inspection_invalid", "vector_inspection.liraa_draw_item_id"),
            (hv, "situation_outcome_mismatch", "vector_inspection.situation"), (hv, "inspection_not_worked", "vector_inspection.deposits"),
            (hv, "activity_property_mismatch", "vector_inspection.activity"), (hv, "liraa_item_not_found", "vector_inspection.liraa_draw_item_id"),
            (hv, "transmission_block_not_active", "vector_inspection.transmission_block_id"),
            (hv, "deposit_counts_inconsistent", "vector_inspection.deposits[0].with_larvae"),
            (hv, "product_not_allowed", "vector_inspection.measures[1].vector_product_id"),
            (hv, "samples_exceed_larvae", "vector_inspection.samples[1]"), (hv, "sample_label_taken", "vector_inspection.samples[0]"),
            (hv, "inspection_times_invalid", "vector_inspection.entered_at"), (hv, "reason_derived", "reasons"),
            (hv, "block_already_set", "vector_inspection.city_block_id"), (hv, "household_without_neighborhood", "vector_inspection.city_block_id"),
            (hv, "block_not_in_household_neighborhood", "vector_inspection.city_block_id"),
            (oi, "cbo_not_allowed", None), (oi, "household_without_block", "household_id"), (oi, "consent_required", "consent"),
            (oi, "ovitrap_number_taken", "number"), (oc, "not_found", "ovitrap_client_uuid"),
            (oc, "collection_out_of_range", "collected_on"), (oc, "reading_not_open", "ovitrap_id"), (oc, "ovitrap_not_active", "ovitrap_id")]
    return results(*[vr(70 + i, k, e, p) for i, (k, e, p) in enumerate(rows)])


def resp_vector_accepted():
    return results(dict(done(60, "home_visit", VISIT), vector_inspection_id=VINSP),
                   done(63, "ovitrap_installation", OVI), done(66, "ovitrap_collection", OVI),
                   done(60, "home_visit", VISIT, "duplicate"))


# ---------- formas do download (24a §2, json.rb) ----------

def household():
    return {"id": HH, "micro_area": dict(MA1_REF), "address": copy.deepcopy(ADDRESS), "property_type": "1",
            "contact_phone": "41999990000", "refused": False, "status": "active", "version": 3,
            "registered_at": "2026-10-28T10:15:00-03:00", "registered_by": {"name": "Rosângela Alves"},
            "location": dict(LOC_GPS),
            "families": [{"id": FAM, "responsible": {"patient_id": PAT, "display_name": "Joana Conceição"},
                          "income_band": "3", "members_count": 3, "living_since": "2019-03-01", "moved_out": False,
                          "responsible_exited": False}],
            "living_conditions": {}}


def registration():
    return {"id": REG,
            "patient": {"id": PAT, "display_name": "Joana Conceição", "full_name": "Joana D'Arc Conceição",
                        "mother_name": "Maria Conceição", "birth_date": "1961-03-14", "sex": "female", "has_cpf": True,
                        "no_cpf_reason": None, "cns_masked": None, "identity_locked": False},
            "patient_demographics": {"race_color": "03", "ethnicity": None},
            "household_id": HH, "family_id": FAM, "is_responsible": True, "team": dict(TEAM_REF), "micro_area": dict(MA1_REF),
            "identification": {}, "sociodemographic": {}, "health_conditions": {}, "street_situation": None,
            "refused": False, "exit": None, "status": "valid", "version": 2,
            "registered_at": "2026-10-28T10:20:00-03:00", "registered_by": {"name": "Rosângela Alves"},
            "identity_changed_at": None, "identity_review_pending": False}


def micro_area(ident=MA1, code="03", name="Vila Nova — rua das Flores"):
    return {"id": ident, "team": dict(TEAM_REF), "code": code, "name": name,
            "acs": {"professional_id": PROF, "name": "Rosângela Alves"}, "active": True}


def who_to_visit():
    return {"generated_at": "2026-11-12T12:00:00Z", "micro_areas": [{"micro_area_id": MA1, "people": [
        {"patient_id": PAT, "display_name": "Joana Conceição", "age": 65,
         "household": {"id": HH, "address_short": "Rua das Flores, 120"}, "family_id": FAM, "micro_area": dict(MA1_REF),
         "last_visit_on": "2026-08-20",
         "reasons": [{"code": "care_line", "care_line": "Pessoa com hipertensão",
                      "practice": "2 visitas do ACS nos últimos 12 meses", "status": "overdue", "due_on": "2026-11-01"}]},
        {"patient_id": PAT2, "display_name": "Benedita Rocha", "age": 78,
         "household": {"id": HH, "address_short": "Rua das Flores, 120"}, "family_id": FAM, "micro_area": dict(MA1_REF),
         "last_visit_on": None,
         "reasons": [{"code": "registration_due", "status": "due_soon", "due_on": "2026-12-20"}, {"code": "never_visited"}]}]}]}


# ---------- POST /field/v1/uploads (resposta) ----------

def results(*rs):
    return {"results": list(rs)}


def done(n, kind, ident, status="accepted"):
    return {"client_uuid": cu(n), "status": status, "type": kind, "id": ident}


def resp_accepted():
    return results(done(10, "patient", PAT2), done(11, "home_visit", VISIT), done(12, "collective_activity", ACT))


def resp_duplicate():
    return results(done(11, "home_visit", VISIT, "duplicate"))


def resp_rejected():
    return results(
        {"client_uuid": cu(1), "status": "rejected", "type": "home_visit", "error": "visit_date_out_of_range", "path": "occurred_at"},
        {"client_uuid": cu(4), "status": "rejected", "type": "collective_activity", "error": "feature_disabled"},
        {"client_uuid": cu(5), "status": "rejected", "type": "patient", "error": "client_uuid_conflict"},
        {"client_uuid": cu(9), "status": "rejected", "type": "home_visit", "error": "patient_unidentified", "path": "patient_id"})  # Q41


def resp_invalid_patient():  # Q49: identidade inválida no registro rápido; path por Q32/Q46
    return results({"client_uuid": cu(5), "status": "rejected", "type": "patient", "error": "invalid_patient", "path": "new_patient.full_name"})


def resp_withdrawal_rejected():  # Q45: sem path, o código vale para o item inteiro
    return results(
        {"client_uuid": cu(3), "status": "rejected", "type": "home_visit_withdrawal", "error": "day_closed"},
        {"client_uuid": cu(13), "status": "rejected", "type": "home_visit_withdrawal", "error": "visit_changed"})


def resp_invalid_request():
    return results(
        {"client_uuid": cu(1), "status": "rejected", "type": "home_visit", "error": "invalid_request", "path": "reasons[0]"},
        {"status": "rejected", "type": "home_visit", "error": "invalid_request", "path": "client_uuid"},
        {"status": "rejected", "error": "invalid_request", "path": "type"})


def resp_duplicate_suspected():
    return results({"client_uuid": cu(10), "status": "rejected", "type": "patient", "error": "duplicate_suspected",
                    "candidates": [{"patient_id": PAT2, "display_name": "Benedita Rocha", "birth_date": "1948-05-02", "sex": "female", "has_cpf": False,
                                    "has_cns": True},
                                   {"patient_id": PAT3, "display_name": "Benedita A. Rocha", "birth_date": "1948-05-02",
                                    "sex": None, "has_cpf": True, "has_cns": False}]})


def resp_duplicate_participant():  # Q54: semelhança (confirmable) e impossível de liberar
    return results(
        {"client_uuid": cu(11), "status": "rejected", "type": "collective_activity", "error": "duplicate_participant",
         "path": "participants[1]", "confirmable": True},
        {"client_uuid": cu(12), "status": "rejected", "type": "collective_activity", "error": "duplicate_participant",
         "path": "participants[2]", "confirmable": False})


def resp_internal_error():  # Q63: exceção inesperada; sem path, fora do livro de idempotência
    return results({"client_uuid": cu(14), "status": "rejected", "type": "home_visit", "error": "internal_error"})


def resp_household_changed():  # Q63: cadastro individual NOVO cujo domicílio citado mudou de versão
    return results({"client_uuid": cu(15), "status": "rejected", "type": "individual_registration", "error": "household_changed", "path": "household_id"})


def resp_too_many_requests():  # Q67: orçamento de busca de pessoa estourado; sem path, fora do livro de idempotência
    return results({"client_uuid": cu(18), "status": "rejected", "type": "patient", "error": "too_many_requests"})


def resp_already_registered_with_id():  # Q63/6A: cadastro existente dentro do escopo do aparelho
    return results({"client_uuid": cu(16), "status": "rejected", "type": "individual_registration", "error": "already_registered", "id": REG})


def resp_already_registered_without_id():  # Q63/6A: fora do escopo, sem id
    return results({"client_uuid": cu(17), "status": "rejected", "type": "individual_registration", "error": "already_registered"})


def resp_stale_household():
    current = household()
    current["version"] = 4
    return results({"client_uuid": cu(6), "status": "stale_version", "type": "household", "id": HH,
                    "current_version": 4, "current": current})


def resp_stale_registration():
    current = registration()
    current["version"] = 3
    return results({"client_uuid": cu(7), "status": "stale_version", "type": "individual_registration", "id": REG,
                    "current_version": 3, "current": current})


def resp_accepted_with_version():  # Q5: version obrigatório no accepted dos cadastros; opcional no duplicate
    return results(dict(done(6, "household", HH), version=4), dict(done(34, "family", FAM, "duplicate"), version=5),
                   dict(done(7, "individual_registration", REG), version=2), done(1, "home_visit", VISIT))


def resp_duplicate_without_version():  # Q5: recibo anterior à coluna result_version
    return results(done(6, "household", HH, "duplicate"))


def resp_stale_family():  # Q4: em stale_version de family, id = o domicílio
    current = household()
    current["version"] = 5
    return results({"client_uuid": cu(34), "status": "stale_version", "type": "family", "id": HH,
                    "current_version": 5, "current": current})


def resp_invalid_location():  # Q2
    return results({"client_uuid": cu(6), "status": "rejected", "type": "household", "error": "invalid_location",
                    "path": "location.latitude"})


def resp_family_not_found():
    return results({"client_uuid": cu(34), "status": "rejected", "type": "family", "error": "family_not_found",
                    "path": "family_id"})


# ---------- GET /field/v1/changes ----------

def household_vector():
    return {"city_block_id": BLOCK, "risk_class": "yellow", "risk_assessed_on": "2026-11-03",
            "last_worked_on": "2026-11-03", "last_situation": "worked"}


def city_block():
    return {"id": BLOCK, "neighborhood_id": cu(40), "number": "12A", "active": True, "neighbor_ids": [BLOCK2], "version": 2}


def ovitrap():
    return {"id": OVI, "number": "OVT-014", "household_id": HH, "status": "active",
            "open_reading": {"installed_on": "2026-11-12"},
            "last_reading": {"collected_on": "2026-11-12", "condition": "ok", "egg_count": 37}, "version": 5}


def liraa_item():
    return {"id": LIRAA_ITEM, "survey_id": SURVEY, "survey_name": "LIRAa novembro 2026", "household_id": HH,
            "city_block_id": BLOCK, "status": "pending", "version": 1}


def transmission_block():
    return {"id": TBLOCK, "status": "active", "block_ids": [BLOCK, BLOCK2],
            "cycles": [{"number": 1, "starts_on": "2026-11-10", "ends_on": "2026-11-14"}], "version": 3}


def page_vector():
    hh = dict(household(), vector=household_vector())
    return {"reset": False,
            "items": [{"type": "household", "id": HH, "version": 3, "body": hh},
                      {"type": "city_block", "id": BLOCK, "version": 2, "body": city_block()},
                      {"type": "ovitrap", "id": OVI, "version": 5, "body": ovitrap()},
                      {"type": "liraa_item", "id": LIRAA_ITEM, "version": 1, "body": liraa_item()},
                      {"type": "transmission_block", "id": TBLOCK, "version": 3, "body": transmission_block()}],
            "removals": [], "who_to_visit": None, "next_cursor": CURSOR, "has_more": True}


def page_vector_closed():
    page = page_vector()
    page["items"][0]["body"]["vector"] = None
    page["items"][2]["body"].update(status="removed", open_reading=None)
    page["items"][2]["body"]["last_reading"]["egg_count"] = None
    page["items"][3]["body"]["status"] = "closed"
    page["items"][4]["body"].update(status="closed", cycles=[
        {"number": 1, "starts_on": "2026-11-10", "ends_on": "2026-11-14"},
        {"number": 2, "starts_on": "2026-11-17", "ends_on": "2026-11-21"},
        {"number": 3, "starts_on": "2026-11-24", "ends_on": "2026-11-28"}])
    page.update(who_to_visit=who_to_visit(), has_more=False)
    return page


def page_first():
    return {"reset": False,
            "items": [{"type": "micro_area", "id": MA1, "body": micro_area()},
                      {"type": "household", "id": HH, "version": 3, "body": household()},
                      {"type": "registration", "id": REG, "version": 2, "body": registration()}],
            "removals": [], "who_to_visit": None, "next_cursor": CURSOR, "has_more": True}


def page_last():
    return {"reset": False, "items": [], "removals": [], "who_to_visit": who_to_visit(), "next_cursor": CURSOR, "has_more": False}


def page_last_age_null():
    page = page_last()
    page["who_to_visit"]["micro_areas"][0]["people"][1]["age"] = None  # Q33: paciente sem nascimento
    return page


def page_last_never_done():
    page = page_last()
    page["who_to_visit"]["micro_areas"][0]["people"][0]["reasons"][0]["due_on"] = None  # Q60: prática atrasada nunca feita
    return page


def page_last_due_soon_null():
    page = page_last_never_done()
    page["who_to_visit"]["micro_areas"][0]["people"][0]["reasons"][0]["status"] = "due_soon"
    return page


def page_removals():
    return {"reset": False, "items": [],
            "removals": [{"type": "household", "id": HH2, "reason": "moved"},
                         {"type": "registration", "id": REG2, "reason": "erased"},
                         {"type": "registration", "id": REG3, "reason": "out_of_scope"}],
            "who_to_visit": {"generated_at": "2026-11-12T12:00:00Z", "micro_areas": [{"micro_area_id": MA1, "people": []}]},
            "next_cursor": CURSOR, "has_more": False}


def page_reset():
    return {"reset": True, "items": [{"type": "micro_area", "id": MA2, "body": micro_area(MA2, "07", "Jardim Esperança")}],
            "removals": [], "who_to_visit": None, "next_cursor": CURSOR, "has_more": True}


# ---------- GET /field/v1/reference ----------

def reference():
    return {"reference_version": REF_SHA,
            "registration_dictionaries": {
                "version": "8.7.0",
                # A ordem 117, 214, 118 é a do YAML: prova que a lista não é reordenada (Q27).
                "domains": {"renda_familiar": [{"code": 3, "label": "1/2 a 1 salário mínimo"}],
                            "abastecimento_de_agua": [{"code": 117, "label": "Rede encanada até o domicílio"},
                                                      {"code": 214, "label": "Poço/nascente no domicílio"},
                                                      {"code": 118, "label": "Cisterna"}]},
                "sections": {"living_conditions": []}},
            "string_domains": {"uf": [{"code": "41", "label": "PARANÁ"}], "tipo_logradouro": [{"code": "081", "label": "RUA"}]},
            "neighborhoods": [{"id": cu(40), "name": "Vila Nova"}],
            "health_units": [{"id": UNIT, "cnes": "2384299", "name": "UBS Vila Nova"},
                             {"id": cu(41), "cnes": None, "name": "Ponto de apoio Jardim Esperança"}],  # Q6
            "team_professionals": [{"team_id": TEAM, "professional_id": PROF2, "name": "Carla Mendes", "cbo": "515105",
                                    "has_cns": True}],
            "home_visit_domains": {"motivo_visita": [], "desfecho": [], "turno": [], "tipo_glicemia": [],
                                   "tipo_de_imovel": [], "non_residential_property_types": [],
                                   "non_residential_reasons": [], "male_forbidden_reasons": [],
                                   "without_person_allowed_reasons": [], "responsible_document_reasons": [],
                                   "reasons_max": 36, "measurement_ranges": {}},
            "collective_activity_domains": {"activity_types": [], "meeting_topics": [], "target_audience": [],
                                            "health_topics": [], "health_practices": [], "procedures": [], "rules": {}}}


SUITES = [
    ("session-response-v1.json", {
        "session-acs.json": (session_acs(), "valid"),
        "session-assigned-agent.json": (session_agent(), "valid"),
        "invalid-session-contract-v2.json": (variant(session_acs, ["contract"], "field-sync-v2"), "/contract const"),
        "invalid-session-scope-team.json": (variant(session_acs, ["teams", 0, "micro_areas", 0, "scope"], "team"), "/teams/0/micro_areas/0/scope enum"),
        "invalid-session-token-key.json": (variant(session_acs, ["token"], "rsf_x"), "/token schema"),
        "session-without-map.json": (variant(session_acs, ["map"], None), "valid"),
        "invalid-session-without-reference-version.json": (variant(session_acs, ["reference_version"], DELETE), "(root) required"),
        "invalid-session-map-short-sha.json": (variant(session_acs, ["map", "sha256"], "ab"), "/map/sha256 pattern"),
        "session-endemic-agent.json": (variant(session_agent, ["features", "vector_control"], True), "valid"),
        "invalid-session-vector-control-string.json": (variant(session_agent, ["features", "vector_control"], "true"), "/features/vector_control boolean"),
    }),
    ("upload-request-v1.json", {
        "upload-home-visit-resident.json": (upload_hv(), "valid"),
        "upload-home-visit-non-residential.json": (upload_hv_nr(), "valid"),
        "upload-home-visit-withdrawal.json": (upload_withdrawal(), "valid"),
        "upload-collective-activity.json": (upload_ca(), "valid"),
        "upload-collective-activity-other-procedure.json": (upload_ca_procedure(), "valid"),
        "upload-patient.json": (upload_patient(), "valid"),
        "upload-household-update.json": (upload_household(), "valid"),
        "upload-individual-registration.json": (upload_registration(), "valid"),
        "upload-mixed-batch.json": (upload_mixed(), "valid"),
        "upload-home-visit-new-household.json": (upload_hv_new_household(), "valid"),
        "upload-registration-same-batch.json": (upload_registration_same_batch(), "valid"),
        "invalid-upload-empty.json": (up(), "/items minItems"),
        "invalid-upload-51-items.json": (up(*[item(n, "home_visit_withdrawal", {"visit_client_uuid": cu(1), "reason": WITHDRAWAL_REASON}) for n in range(1, 52)]), "/items maxItems"),
        "invalid-upload-unknown-type.json": (up({"client_uuid": cu(1), "type": "visit_sheet", "body": {}}), "/items/0/type enum"),
        "invalid-upload-client-uuid-uppercase.json": (variant(upload_hv, ["items", 0, "client_uuid"], cu(1).upper()), "/items/0/client_uuid pattern"),
        "invalid-home-visit-shift-in-body.json": (variant(upload_hv, B + ["shift"], 1), "/items/0/body/shift schema"),
        "invalid-home-visit-occurred-at-without-offset.json": (variant(upload_hv, B + ["occurred_at"], "2026-11-12T09:40:00"), "/items/0/body/occurred_at pattern"),
        "invalid-home-visit-outcome-4.json": (variant(upload_hv, B + ["outcome"], 4), "/items/0/body/outcome enum"),
        "invalid-home-visit-reason-26.json": (variant(upload_hv, B + ["reasons"], [26]), "/items/0/body/reasons/0 enum"),
        "invalid-home-visit-systolic-alone.json": (variant(upload_hv, B + ["measurements"], {"systolic": 138}), "/items/0/body/measurements/systolic dependentRequired"),
        "invalid-home-visit-note-too-long.json": (variant(upload_hv, B + ["note"], "x" * 501), "/items/0/body/note maxLength"),
        "invalid-home-visit-latitude.json": (variant(upload_hv, B + ["latitude"], -25.43), "/items/0/body/latitude schema"),
        "invalid-home-visit-client-uuid-in-body.json": (variant(upload_hv, B + ["client_uuid"], cu(1)), "/items/0/body/client_uuid schema"),
        "invalid-home-visit-two-households.json": (variant(upload_hv_new_household, ["items", 2, "body", "household_id"], HH), "/items/2/body not"),
        "invalid-registration-two-patients.json": (variant(upload_registration_same_batch, ["items", 2, "body", "patient_id"], PAT2), "/items/2/body not"),
        "invalid-home-visit-two-patients.json": (variant(upload_hv, B + ["patient_client_uuid"], cu(10)), "/items/0/body not"),
        "invalid-registration-two-households.json": (variant(upload_registration, B + ["household_client_uuid"], cu(20)), "/items/0/body not"),
        "invalid-withdrawal-reason-short.json": (variant(upload_withdrawal, B + ["reason"], "errado"), "/items/0/body/reason minLength"),
        "invalid-home-visit-37-reasons.json": (variant(upload_hv, B + ["reasons"], [c for c in range(1, 39) if c != 26]), "/items/0/body/reasons maxItems"),  # Q36
        "invalid-collective-activity-altered-count-in-body.json": (variant(upload_ca, B + ["altered_count"], 1), "/items/0/body/altered_count schema"),  # Q38
        "invalid-collective-activity-8-meeting-topics.json": (variant(upload_ca, B + ["meeting_topics"], [1, 2, 3, 4, 5, 6, 7, 8]), "/items/0/body/meeting_topics maxItems"),  # Q36
        "invalid-collective-activity-19-target-audience.json": (variant(upload_ca, B + ["target_audience"], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20]), "/items/0/body/target_audience maxItems"),
        "invalid-collective-activity-17-health-topics.json": (variant(upload_ca, B + ["health_topics"], [1, 4, 5, 6, 7, 8, 10, 13, 14, 15, 16, 17, 19, 21, 29, 31, 32]), "/items/0/body/health_topics maxItems"),
        "invalid-collective-activity-16-health-practices.json": (variant(upload_ca, B + ["health_practices"], [2, 3, 9, 11, 12, 20, 22, 23, 24, 25, 26, 27, 28, 30, 33, 34]), "/items/0/body/health_practices maxItems"),
        "invalid-collective-activity-procedure-not-sigtap-list.json": (variant(upload_ca_procedure, B + ["procedure_code"], "0101050001"), "/items/0/body/procedure_code enum"),  # Q37
        "invalid-collective-activity-pse-topic-18.json": (variant(upload_ca, B + ["health_topics"], [18]), "/items/0/body/health_topics/0 enum"),
        "invalid-collective-activity-two-places.json": (variant(upload_ca, B + ["place_health_unit_id"], UNIT), "/items/0/body oneOf"),  # Q15
        "invalid-collective-activity-inep.json": (variant(upload_ca, B + ["inep"], "41000000"), "/items/0/body/inep schema"),  # Q15
        "invalid-patient-cpf-masked.json": (variant(upload_patient, B + ["new_patient", "cpf"], "390.533.447-05"), "/items/0/body/new_patient/cpf pattern"),
        "invalid-household-version-without-id.json": (variant(upload_household, B + ["household_id"], DELETE), "/items/0/body/version dependentRequired"),
        "invalid-household-property-type-integer.json": (variant(upload_household, B + ["property_type"], 1), "/items/0/body/property_type enum"),
        "upload-family-new.json": (upload_family_new(), "valid"),
        "upload-family-new-from-registration.json": (upload_family_new_from_registration(), "valid"),
        "upload-family-update.json": (upload_family_update(), "valid"),
        "upload-household-location.json": (upload_household_location(dict(LOC_MAP)), "valid"),
        "upload-household-location-cleared.json": (upload_household_location(None), "valid"),
        "upload-home-visit-location.json": (upload_hv_location(), "valid"),
        "upload-home-visit-family-client-uuid.json": (upload_hv_family_client_uuid(), "valid"),
        "invalid-location-latitude-only.json": (upload_hv_location({"latitude": -25.42847123, "source": "gps"}), "/items/0/body/location required"),
        "invalid-location-latitude-out-of-range.json": (variant(upload_hv_location, B + ["location", "latitude"], -91), "/items/0/body/location/latitude minimum"),
        "invalid-location-nine-decimals.json": (variant(upload_hv_location, B + ["location", "latitude"], -25.428471234), "/items/0/body/location/latitude multipleOf"),
        "invalid-location-gps-without-accuracy.json": (variant(upload_hv_location, B + ["location", "accuracy_m"], DELETE), "/items/0/body/location required"),  # Q3
        "invalid-home-visit-location-null.json": (upload_hv_location(None), "/items/0/body/location object"),
        "invalid-family-two-households.json": (variant(upload_family_update, B + ["household_client_uuid"], cu(30)), "/items/0/body oneOf"),
        "invalid-family-responsible-two-patients.json": (variant(upload_family_update, B + ["responsible"], {"patient_id": PAT, "patient_client_uuid": cu(31)}), "/items/0/body/responsible maxProperties"),
        "invalid-registration-two-families.json": (variant(upload_registration, B + ["family_client_uuid"], cu(33)), "/items/0/body not"),
        "upload-home-visit-vector-inspection.json": (upload_vi(), "valid"),
        "upload-home-visit-vector-inspection-pe.json": (upload_vi_pe(), "valid"),
        "upload-home-visit-vector-inspection-closed.json": (upload_vi_closed(), "valid"),
        "upload-ovitrap-installation.json": (upload_ovitrap_installation(), "valid"),
        "upload-ovitrap-same-batch.json": (upload_ovitrap_same_batch(), "valid"),
        "upload-ovitrap-collection.json": (upload_ovitrap_collection(), "valid"),
        "invalid-vector-inspection-null.json": (variant(upload_vi, VI, None), "/items/0/body/vector_inspection object"),
        "invalid-vector-inspection-activity-unknown.json": (variant(upload_vi, VI + ["activity"], "lit"), "/items/0/body/vector_inspection/activity enum"),
        "invalid-vector-inspection-recovered-in-body.json": (variant(upload_vi, VI + ["recovered"], True), "/items/0/body/vector_inspection/recovered schema"),
        "invalid-vector-inspection-entered-at-without-offset.json": (variant(upload_vi, VI + ["entered_at"], "2026-11-12T09:30:00"), "/items/0/body/vector_inspection/entered_at pattern"),
        "invalid-vector-inspection-risk-class-blue.json": (variant(upload_vi, VI + ["risk_class"], "blue"), "/items/0/body/vector_inspection/risk_class enum"),
        "invalid-vector-inspection-deposit-group-f.json": (variant(upload_vi, VI + ["deposits", 0, "group"], "F"), "/items/0/body/vector_inspection/deposits/0/group enum"),
        "invalid-vector-inspection-deposit-1000.json": (variant(upload_vi, VI + ["deposits", 0, "existing"], 1000), "/items/0/body/vector_inspection/deposits/0/existing maximum"),
        "invalid-vector-inspection-8-deposits.json": (upload_vi_8_deposits(), "/items/0/body/vector_inspection/deposits maxItems"),
        "invalid-vector-inspection-charges-three-decimals.json": (variant(upload_vi, VI + ["measures", 1, "charges"], 1.234), "/items/0/body/vector_inspection/measures/1/charges multipleOf"),
        "invalid-vector-inspection-charges-zero.json": (variant(upload_vi, VI + ["measures", 1, "charges"], 0), "/items/0/body/vector_inspection/measures/1/charges exclusiveMinimum"),
        "invalid-vector-inspection-larvae-11.json": (variant(upload_vi, VI + ["samples", 0, "larvae_collected"], 11), "/items/0/body/vector_inspection/samples/0/larvae_collected maximum"),
        "invalid-ovitrap-installation-two-households.json": (variant(upload_ovitrap_installation, B + ["household_client_uuid"], cu(30)), "/items/0/body oneOf"),
        "invalid-ovitrap-installation-number-13-chars.json": (variant(upload_ovitrap_installation, B + ["number"], "OVT-012345678"), "/items/0/body/number pattern"),
        "invalid-ovitrap-installation-without-consent.json": (variant(upload_ovitrap_installation, B + ["consent"], DELETE), "/items/0/body required"),
        "invalid-ovitrap-collection-two-ovitraps.json": (variant(upload_ovitrap_collection, B + ["ovitrap_client_uuid"], cu(64)), "/items/0/body oneOf"),
        "invalid-ovitrap-collection-condition-wet.json": (variant(upload_ovitrap_collection, B + ["condition"], "wet"), "/items/0/body/condition enum"),
        "invalid-ovitrap-collection-egg-count.json": (variant(upload_ovitrap_collection, B + ["egg_count"], 12), "/items/0/body/egg_count schema"),
    }),
    ("upload-response-v1.json", {
        "upload-response-accepted.json": (resp_accepted(), "valid"),
        "upload-response-duplicate.json": (resp_duplicate(), "valid"),
        "upload-response-rejected.json": (resp_rejected(), "valid"),
        "upload-response-duplicate-suspected.json": (resp_duplicate_suspected(), "valid"),
        "upload-response-duplicate-participant.json": (resp_duplicate_participant(), "valid"),
        "upload-response-invalid-patient.json": (resp_invalid_patient(), "valid"),
        "upload-response-withdrawal-rejected.json": (resp_withdrawal_rejected(), "valid"),
        "upload-response-invalid-request.json": (resp_invalid_request(), "valid"),
        "upload-response-internal-error.json": (resp_internal_error(), "valid"),
        "upload-response-household-changed.json": (resp_household_changed(), "valid"),
        "upload-response-too-many-requests.json": (resp_too_many_requests(), "valid"),
        "upload-response-already-registered-with-id.json": (resp_already_registered_with_id(), "valid"),
        "upload-response-already-registered-without-id.json": (resp_already_registered_without_id(), "valid"),
        "upload-response-stale-household.json": (resp_stale_household(), "valid"),
        "upload-response-stale-registration.json": (resp_stale_registration(), "valid"),
        "upload-response-accepted-with-version.json": (resp_accepted_with_version(), "valid"),
        "upload-response-duplicate-without-version.json": (resp_duplicate_without_version(), "valid"),
        "upload-response-stale-family.json": (resp_stale_family(), "valid"),
        "upload-response-invalid-location.json": (resp_invalid_location(), "valid"),
        "upload-response-family-not-found.json": (resp_family_not_found(), "valid"),
        "invalid-response-household-accepted-without-version.json": (results(done(6, "household", HH)), "/results/0 required"),
        "invalid-response-home-visit-with-version.json": (results(dict(done(1, "home_visit", VISIT), version=1)), "/results/0/version schema"),
        "invalid-response-duplicate-suspected-without-candidates.json": (variant(resp_duplicate_suspected, ["results", 0, "candidates"], DELETE), "/results/0 required"),
        "invalid-response-empty-results.json": (results(), "/results minItems"),
        "invalid-response-rejected-without-client-uuid.json": (variant(resp_invalid_request, ["results", 1, "error"], "visit_date_out_of_range"), "/results/1 required"),
        "invalid-response-accepted-without-id.json": (variant(resp_accepted, ["results", 0, "id"], DELETE), "/results/0 required"),
        "invalid-response-status-queued.json": (variant(resp_accepted, ["results", 0, "status"], "queued"), "/results/0/status enum"),
        "invalid-response-candidate-with-cpf.json": (variant(resp_duplicate_suspected, ["results", 0, "candidates", 0, "cpf"], "11144477735"), "/results/0/candidates/0/cpf schema"),
        "invalid-response-stale-without-current.json": (variant(resp_stale_household, ["results", 0, "current"], DELETE), "/results/0 required"),
        "invalid-response-rejected-with-id.json": (variant(resp_rejected, ["results", 0, "id"], VISIT), "/results/0/id schema"),
        "invalid-response-id-on-rejected-other-error.json": (variant(resp_household_changed, ["results", 0, "id"], REG), "/results/0/id schema"),
        "invalid-response-unknown-error-code.json": (variant(resp_internal_error, ["results", 0, "error"], "Internal Error"), "/results/0/error pattern"),
        "invalid-response-candidates-without-duplicate-suspected.json": (variant(resp_duplicate_suspected, ["results", 0, "error"], "cpf_taken"), "/results/0/error const"),
        "invalid-response-duplicate-participant-without-confirmable.json": (variant(resp_duplicate_participant, ["results", 0, "confirmable"], DELETE), "/results/0 required"),
        "invalid-response-confirmable-on-other-error.json": (variant(resp_rejected, ["results", 0, "confirmable"], True), "/results/0/confirmable schema"),
        "invalid-response-stale-household-with-cpf.json": (variant(resp_stale_household, ["results", 0, "current", "families", 0, "responsible", "cpf"], "39053344705"), "/results/0/current/families/0/responsible/cpf schema"),
        "upload-response-vector-accepted.json": (resp_vector_accepted(), "valid"),
        "upload-response-vector-rejected.json": (resp_vector_rejected(), "valid"),
        "invalid-response-vector-inspection-id-on-patient.json": (results(dict(done(10, "patient", PAT2), vector_inspection_id=VINSP)), "/results/0/vector_inspection_id schema"),
        "invalid-response-vector-inspection-id-on-rejected.json": (variant(resp_vector_rejected, ["results", 0, "vector_inspection_id"], VINSP), "/results/0/vector_inspection_id schema"),
        "invalid-response-ovitrap-id.json": (results(dict(done(63, "ovitrap_installation", OVI), ovitrap_id=OVI)), "/results/0/ovitrap_id schema"),
    }),
    ("changes-response-v1.json", {
        "changes-first-page.json": (page_first(), "valid"),
        "changes-last-page.json": (page_last(), "valid"),
        "changes-last-page-age-null.json": (page_last_age_null(), "valid"),
        "changes-last-page-care-line-never-done.json": (page_last_never_done(), "valid"),
        "changes-removals.json": (page_removals(), "valid"),
        "changes-reset.json": (page_reset(), "valid"),
        "changes-household-location-null.json": (variant(page_first, ["items", 1, "body", "location"], None), "valid"),
        "invalid-changes-household-without-location.json": (variant(page_first, ["items", 1, "body", "location"], DELETE), "/items/1/body required"),
        "invalid-changes-who-null-on-last-page.json": (variant(page_last, ["who_to_visit"], None), "/who_to_visit object"),
        "invalid-changes-who-on-middle-page.json": (variant(page_first, ["who_to_visit"], who_to_visit()), "/who_to_visit null"),
        "invalid-changes-removal-reason-death.json": (variant(page_removals, ["removals", 0, "reason"], "death"), "/removals/0/reason enum"),
        "invalid-changes-household-without-version.json": (variant(page_first, ["items", 1, "version"], DELETE), "/items/1 required"),
        "invalid-changes-micro-area-with-version.json": (variant(page_first, ["items", 0, "version"], 1), "/items/0/version schema"),
        "invalid-changes-registration-with-cpf.json": (variant(page_first, ["items", 2, "body", "patient", "cpf"], "39053344705"), "/items/2/body/patient/cpf schema"),
        "invalid-changes-care-line-reason-with-cid.json": (variant(page_last, ["who_to_visit", "micro_areas", 0, "people", 0, "reasons", 0, "cid10"], "I10"), "/who_to_visit/micro_areas/0/people/0/reasons/0/cid10 schema"),
        "invalid-changes-care-line-due-soon-null-due-on.json": (page_last_due_soon_null(), "/who_to_visit/micro_areas/0/people/0/reasons/0/due_on string"),
        "invalid-changes-registration-due-null-due-on.json": (variant(page_last, ["who_to_visit", "micro_areas", 0, "people", 1, "reasons", 0, "due_on"], None), "/who_to_visit/micro_areas/0/people/1/reasons/0/due_on string"),
        "invalid-changes-cursor-null.json": (variant(page_first, ["next_cursor"], None), "/next_cursor string"),
        "changes-vector-page.json": (page_vector(), "valid"),
        "changes-vector-closed.json": (page_vector_closed(), "valid"),
        "invalid-changes-transmission-block-with-case.json": (variant(page_vector, ["items", 4, "body", "cases"], [{"disease": "dengue", "case_on": "2026-11-08"}]), "/items/4/body/cases schema"),
        "invalid-changes-transmission-block-proposed.json": (variant(page_vector, ["items", 4, "body", "status"], "proposed"), "/items/4/body/status enum"),
        "invalid-changes-ovitrap-without-version.json": (variant(page_vector, ["items", 2, "version"], DELETE), "/items/2 required"),
        "invalid-changes-city-block-number-with-space.json": (variant(page_vector, ["items", 1, "body", "number"], "12 A"), "/items/1/body/number pattern"),
        "invalid-changes-household-vector-risk-blue.json": (variant(page_vector, ["items", 0, "body", "vector", "risk_class"], "blue"), "/items/0/body/vector/risk_class enum"),
    }),
    ("reference-response-v1.json", {
        "reference.json": (reference(), "valid"),
        "invalid-reference-version-short.json": (variant(reference, ["reference_version"], "cd"), "/reference_version pattern"),
        "invalid-reference-professional-with-cpf.json": (variant(reference, ["team_professionals", 0, "cpf"], "39053344705"), "/team_professionals/0/cpf schema"),
        "invalid-reference-professional-without-has-cns.json": (variant(reference, ["team_professionals", 0, "has_cns"], DELETE), "/team_professionals/0 required"),  # Q6
        "invalid-reference-domain-as-object.json": (variant(reference, ["registration_dictionaries", "domains", "renda_familiar"], {"3": "1/2 a 1 salário mínimo"}), "/registration_dictionaries/domains/renda_familiar array"),  # Q27
        "invalid-reference-without-health-units.json": (variant(reference, ["health_units"], DELETE), "(root) required"),
    }),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = {"suites": []}
    for schema, cases in SUITES:
        entries = []
        for name, (doc, expect) in cases.items():
            with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
                f.write(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
            entries.append({"file": name, "expect": expect})
        manifest["suites"].append({"schema": schema, "cases": entries})
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    total = sum(len(c) for _, c in SUITES)
    print(" · ".join(f"{s} {len(c)}" for s, c in SUITES) + f" · total {total}")


if __name__ == "__main__":
    main()
