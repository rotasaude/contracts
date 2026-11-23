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
# As sete chaves de collective_activity.rules que o api serve na referência, na ordem do api.
# check_domains.py tem a mesma constante e confere a igualdade.
REFERENCE_RULE_KEYS = ["list_max", "by_type", "health_topics_with_meeting_topic", "practices_only_in_type",
                       "procedure_practices", "smoking_practices", "participant_measurements"]


def cu(n):
    return f"c0ffee{n:02d}-0000-4000-8000-{n:012d}"


def cz(n):  # client_uuid do 35b (o cu(n) já usa 1–93)
    return f"c0ffee{n:02d}-0000-4000-9000-{n:012d}"


ANIMAL = "a7b8c9d0-e1f2-4a3b-8c4d-6e7f8a9b0c1d"
ANIMAL2 = "b8c9d0e1-f2a3-4b4c-9d5e-7f8a9b0c1d2e"
ANIMAL3 = "c9d0e1f2-a3b4-4c5d-8e6f-8a9b0c1d2e3f"
CAMPAIGN = "d0e1f2a3-b4c5-4d6e-9f7a-9b0c1d2e3f4a"
LV_SURVEY = "f1a2b3c4-d5e6-4f7a-8b8c-0d1e2f3a4b5c"
VACCINE = "e1f2a3b4-c5d6-4e7f-8a9b-1c2d3e4f5a6b"
COLLAR_PRODUCT = "f2a3b4c5-d6e7-4f8a-9b0c-2d3e4f5a6b7c"
VACC = "0b1c2d3e-4f5a-4b6c-8d7e-3f4a5b6c7d8e"
LTEST = "1c2d3e4f-5a6b-4c7d-9e8f-4a5b6c7d8e9f"
COLLAR = "2d3e4f5a-6b7c-4d8e-8f9a-5b6c7d8e9f0a"


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
ADDRESS = {"zip": "80010000", "street_type": "081", "street": "das Flores", "number": "120", "no_number": False,
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


def session_zoonoses():
    d = session_agent()
    d["features"]["vector_control"] = True
    d["features"]["zoonoses"] = True
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


# ---------- 35b: zoonoses (animal, vacinação antirrábica, coleta de leishmaniose, coleira) ----------

def zitem(n, kind, body):
    return {"client_uuid": cz(n), "type": kind, "body": body}


def zdone(n, kind, ident, status="accepted"):
    return {"client_uuid": cz(n), "status": status, "type": kind, "id": ident}


def zr(n, kind, error, path=None):
    r = {"client_uuid": cz(n), "status": "rejected", "type": kind, "error": error}
    if path:
        r["path"] = path
    return r


def animal_new():
    return {"household_id": HH, "species": "dog", "sex": "female", "size": "medium", "name": "Pipoca", "coat": "Caramelo",
            "breed": "SRD", "birth_estimate_month": "2022-03", "tutor_patient_id": PAT, "community": False,
            "microchip": "985112003456789"}


def animal_update():
    return {"animal_id": ANIMAL2, "version": 2, "household_id": HH, "species": "cat", "sex": "male", "name": "Frajola",
            "community": False, "status": "missing", "status_on": "2026-11-20"}


def animal_community():
    return {"household_id": HH2, "species": "dog", "sex": "unknown", "community": True}


def vacc():
    return {"animal_id": ANIMAL, "campaign_id": CAMPAIGN, "vaccinated_on": "2026-11-21", "vector_product_id": VACCINE,
            "adverse_event": True, "adverse_note": "Inchaço no local da aplicação."}


def leish():
    return {"leish_survey_id": LV_SURVEY, "animal_id": ANIMAL, "collected_on": "2026-11-21", "dpp_result": "reactive",
            "dpp_on": "2026-11-21"}


def collar():
    return {"animal_id": ANIMAL, "vector_product_id": COLLAR_PRODUCT, "placed_on": "2026-11-21"}


def _swap(d, drop, **add):
    d = dict(d)
    for k in drop:
        d.pop(k, None)
    d.update(add)
    return d


def up_animal_new():
    return up(zitem(10, "animal", animal_new()))


def up_animal_update():
    return up(zitem(11, "animal", animal_update()))


def up_vacc():
    return up(zitem(13, "rabies_vaccination", vacc()))


def up_leish():
    return up(zitem(14, "leish_collection", leish()))


def up_collar():
    return up(zitem(15, "collar", collar()))


def upload_zoonoses_same_batch():  # §17, roteiro 9; tutor por Q29 (patient ou individual_registration com new_patient)
    return up(zitem(1, "patient", {"new_patient": NEW_PATIENT}),
              zitem(2, "animal", _swap(animal_new(), ["microchip", "tutor_patient_id"], tutor_client_uuid=cz(1))),
              zitem(3, "rabies_vaccination", _swap(vacc(), ["animal_id", "adverse_note"], animal_client_uuid=cz(2), adverse_event=False)),
              zitem(4, "leish_collection", _swap(leish(), ["animal_id"], animal_client_uuid=cz(2))),
              zitem(5, "collar", _swap(collar(), ["animal_id"], animal_client_uuid=cz(2))))


def resp_zoonoses_rejected():
    an, rv, lc, co = "animal", "rabies_vaccination", "leish_collection", "collar"
    rows = [(an, "microchip_taken", "microchip"), (an, "registry_number_taken", "registry_number"),
            (an, "animal_not_active", "animal_id"), (an, "cbo_not_allowed", None), (an, "out_of_scope", "household_id"),
            (an, "tutor_not_found", "tutor_client_uuid"),
            (rv, "already_vaccinated_in_campaign", "animal_id"), (rv, "campaign_not_open", "campaign_id"),
            (rv, "product_not_allowed", "vector_product_id"), (rv, "date_out_of_range", "vaccinated_on"),
            (lc, "survey_not_open", "leish_survey_id"), (lc, "household_not_in_survey", "leish_survey_id"),
            (lc, "animal_not_dog", "animal_id"), (lc, "cbo_not_allowed", None), (lc, "not_found", "animal_client_uuid"),
            (co, "animal_not_dog", "animal_client_uuid"), (co, "feature_disabled", None)]
    return results(*[zr(40 + i, k, e, p) for i, (k, e, p) in enumerate(rows)])


def resp_zoonoses_accepted():
    return results(dict(zdone(2, "animal", ANIMAL), version=1),
                   zdone(3, "rabies_vaccination", VACC),
                   dict(zdone(4, "leish_collection", LTEST), label="LV-2026-F1A2B3-0001"),
                   zdone(5, "collar", COLLAR),
                   dict(zdone(4, "leish_collection", LTEST, "duplicate"), label="LV-2026-F1A2B3-0001"),
                   zdone(2, "animal", ANIMAL, "duplicate"),
                   dict(zdone(6, "leish_collection", cz(60)), label="LV-2026-AVUL-0007"))


# ---------- 35b: download (animal, leish_survey) ----------

ANIMAL_REQUIRED = ["id", "version", "household_id", "species", "name", "sex", "size", "coat", "breed", "birth_estimate_on",
                   "status", "neutered", "tutor", "community", "last_rabies_vaccination_on", "collar_due_on", "has_microchip"]
LEISH_REQUIRED = ["id", "version", "name", "kind", "household_ids", "starts_on", "ends_on"]


def animal():
    return {"id": ANIMAL, "version": 2, "household_id": HH, "species": "dog", "name": "Pipoca", "sex": "female",
            "size": "medium", "coat": "Caramelo", "breed": "SRD", "birth_estimate_on": "2022-03-01", "status": "active",
            "neutered": False, "tutor": {"patient_id": PAT, "display_name": "Joana Conceição"}, "community": False,
            "last_rabies_vaccination_on": "2026-11-21", "collar_due_on": "2026-12-01", "has_microchip": True}


def animal_community_body():
    return dict(animal(), id=ANIMAL2, version=1, name=None, size=None, coat=None, breed=None, birth_estimate_on=None,
                last_rabies_vaccination_on=None, collar_due_on=None, tutor=None, community=True, has_microchip=False)


def leish_survey():
    return {"id": LV_SURVEY, "version": 1, "name": "Inquérito LV Vila Nova 2026", "kind": "sample",
            "household_ids": [HH, HH2], "starts_on": "2026-11-03", "ends_on": "2026-12-12"}


def page_zoonoses():
    return {"reset": False,
            "items": [{"type": "household", "id": HH, "version": 3, "body": household()},
                      {"type": "animal", "id": ANIMAL, "version": 2, "body": animal()},
                      {"type": "animal", "id": ANIMAL2, "version": 1, "body": animal_community_body()},
                      {"type": "leish_survey", "id": LV_SURVEY, "version": 1, "body": leish_survey()}],
            "removals": [], "who_to_visit": None, "next_cursor": CURSOR, "has_more": True}


def page_zoonoses_removals():
    return {"reset": False, "items": [],
            "removals": [{"type": "animal", "id": ANIMAL3, "reason": "out_of_scope"},
                         {"type": "leish_survey", "id": LV_SURVEY, "reason": "out_of_scope"}],
            "who_to_visit": who_to_visit(), "next_cursor": CURSOR, "has_more": False}


def resp_stale_animal():
    return results({"client_uuid": cz(11), "status": "stale_version", "type": "animal", "id": ANIMAL,
                    "current_version": 3, "current": dict(animal(), version=3)})


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
    with open(os.path.join(os.path.dirname(HERE), "domains-v1.json"), encoding="utf-8") as f:
        ca_rules = json.load(f)["collective_activity"]["rules"]
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
                                            "health_topics": [], "health_practices": [], "procedures": [],
                                            "rules": {k: copy.deepcopy(ca_rules[k]) for k in REFERENCE_RULE_KEYS}}}


def reference_vector():
    """reference() + vector_control_domains; as seis listas vêm de domains-v1.json (uma fonte só)."""
    with open(os.path.join(os.path.dirname(HERE), "domains-v1.json"), encoding="utf-8") as f:
        vc = json.load(f)["vector_control"]
    doc = reference()
    doc["vector_control_domains"] = {
        **{k: [{"code": e["code"], "label": e["label"]} for e in vc[k]]
           for k in ("activities", "work_types", "situations", "deposit_groups", "measure_methods", "risk_classes")},
        "products": [{"id": PRODUCT, "code": "SPN", "name": "Espinosade 7,48% DT (larvicida)", "unit": "un", "charge_size": "1.00", "uses": ["focal"]},
                     {"id": PRODUCT2, "code": "CDM", "name": "Clotianidina + deltametrina PM (adulticida residual)", "unit": "g", "charge_size": "12.50", "uses": ["perifocal"]}],
        "cadences": [{"neighborhood_id": None, "risk_class": None, "strategic_point": True, "days": 15},
                     {"neighborhood_id": cu(40), "risk_class": "red", "strategic_point": False, "days": 30}],
        "parameters": {"default_days": 60, "strategic_point_days": 15, "ovitrap_collection_days_min": 3, "ovitrap_collection_days_max": 10},
        "limits": dict(vc["limits"])}
    return doc


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
        "session-zoonoses-agent.json": (session_zoonoses(), "valid"),
        "invalid-session-zoonoses-string.json": (variant(session_zoonoses, ["features", "zoonoses"], "true"), "/features/zoonoses boolean"),
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
        "invalid-vector-inspection-sample-label-in-body.json": (variant(upload_vi, VI + ["samples", 0, "label"], "ABCDEF12-01"), "/items/0/body/vector_inspection/samples/0/label schema"),
        "invalid-vector-inspection-larvae-11.json": (variant(upload_vi, VI + ["samples", 0, "larvae_collected"], 11), "/items/0/body/vector_inspection/samples/0/larvae_collected maximum"),
        "invalid-ovitrap-installation-two-households.json": (variant(upload_ovitrap_installation, B + ["household_client_uuid"], cu(30)), "/items/0/body oneOf"),
        "invalid-ovitrap-installation-number-13-chars.json": (variant(upload_ovitrap_installation, B + ["number"], "OVT-012345678"), "/items/0/body/number pattern"),
        "invalid-ovitrap-installation-without-consent.json": (variant(upload_ovitrap_installation, B + ["consent"], DELETE), "/items/0/body required"),
        "invalid-ovitrap-collection-two-ovitraps.json": (variant(upload_ovitrap_collection, B + ["ovitrap_client_uuid"], cu(64)), "/items/0/body oneOf"),
        "invalid-ovitrap-collection-condition-wet.json": (variant(upload_ovitrap_collection, B + ["condition"], "wet"), "/items/0/body/condition enum"),
        "invalid-ovitrap-collection-egg-count.json": (variant(upload_ovitrap_collection, B + ["egg_count"], 12), "/items/0/body/egg_count schema"),
        "upload-animal-new.json": (up_animal_new(), "valid"),
        "upload-animal-update.json": (up_animal_update(), "valid"),
        "upload-animal-community.json": (up(zitem(12, "animal", animal_community())), "valid"),
        "upload-zoonoses-same-batch.json": (upload_zoonoses_same_batch(), "valid"),
        "upload-rabies-vaccination.json": (up_vacc(), "valid"),
        "upload-leish-collection.json": (up_leish(), "valid"),
        "upload-leish-collection-off-survey.json": (up(zitem(14, "leish_collection", _swap(leish(), ["leish_survey_id", "dpp_result", "dpp_on"]))), "valid"),
        "upload-collar.json": (up_collar(), "valid"),
        "invalid-animal-without-species.json": (variant(up_animal_new, B + ["species"], DELETE), "/items/0/body required"),
        "invalid-animal-without-sex.json": (variant(up_animal_new, B + ["sex"], DELETE), "/items/0/body required"),
        "invalid-animal-without-community.json": (variant(up_animal_new, B + ["community"], DELETE), "/items/0/body required"),
        "invalid-rabies-vaccination-without-campaign-id.json": (variant(up_vacc, B + ["campaign_id"], DELETE), "/items/0/body required"),
        "invalid-rabies-vaccination-without-vaccinated-on.json": (variant(up_vacc, B + ["vaccinated_on"], DELETE), "/items/0/body required"),
        "invalid-rabies-vaccination-without-vector-product-id.json": (variant(up_vacc, B + ["vector_product_id"], DELETE), "/items/0/body required"),
        "invalid-rabies-vaccination-without-adverse-event.json": (variant(up_vacc, B + ["adverse_event"], DELETE), "/items/0/body required"),
        "invalid-leish-collection-without-collected-on.json": (variant(up_leish, B + ["collected_on"], DELETE), "/items/0/body required"),
        "invalid-collar-without-vector-product-id.json": (variant(up_collar, B + ["vector_product_id"], DELETE), "/items/0/body required"),
        "invalid-collar-without-placed-on.json": (variant(up_collar, B + ["placed_on"], DELETE), "/items/0/body required"),
        "invalid-animal-neutered-in-body.json": (variant(up_animal_new, B + ["neutered"], True), "/items/0/body/neutered schema"),
        "invalid-rabies-vaccination-modality-in-body.json": (variant(up_vacc, B + ["modality"], "house"), "/items/0/body/modality schema"),
        "invalid-leish-collection-label-in-body.json": (variant(up_leish, B + ["label"], "LV-2026-F1A2B3-0001"), "/items/0/body/label schema"),
        "invalid-collar-due-on-in-body.json": (variant(up_collar, B + ["due_on"], "2027-05-21"), "/items/0/body/due_on schema"),
        "invalid-animal-two-households.json": (variant(up_animal_new, B + ["household_client_uuid"], cz(30)), "/items/0/body oneOf"),
        "invalid-animal-without-household.json": (variant(up_animal_new, B + ["household_id"], DELETE), "/items/0/body required"),
        "invalid-animal-two-tutors.json": (variant(up_animal_new, B + ["tutor_client_uuid"], cz(1)), "/items/0/body not"),
        "invalid-animal-community-with-tutor.json": (variant(up_animal_new, B + ["community"], True), "/items/0/body/tutor_patient_id schema"),
        "invalid-animal-microchip-on-update.json": (variant(up_animal_update, B + ["microchip"], "985112003456789"), "/items/0/body/microchip schema"),
        "invalid-animal-microchip-14-digits.json": (variant(up_animal_new, B + ["microchip"], "98511200345678"), "/items/0/body/microchip pattern"),
        "invalid-animal-status-on-create.json": (up(zitem(10, "animal", dict(animal_new(), status="deceased", status_on="2026-11-20"))), "/items/0/body/status schema"),
        "invalid-animal-version-without-id.json": (variant(up_animal_update, B + ["animal_id"], DELETE), "/items/0/body/version dependentRequired"),
        "invalid-animal-birth-month-13.json": (variant(up_animal_new, B + ["birth_estimate_month"], "2022-13"), "/items/0/body/birth_estimate_month pattern"),
        "invalid-animal-name-61-chars.json": (variant(up_animal_new, B + ["name"], "P" * 61), "/items/0/body/name maxLength"),
        "invalid-rabies-vaccination-two-animals.json": (variant(up_vacc, B + ["animal_client_uuid"], cz(2)), "/items/0/body oneOf"),
        "invalid-rabies-vaccination-without-animal.json": (variant(up_vacc, B + ["animal_id"], DELETE), "/items/0/body required"),
        "invalid-rabies-vaccination-note-short.json": (variant(up_vacc, B + ["adverse_note"], "Inchaço."), "/items/0/body/adverse_note minLength"),
        "invalid-rabies-vaccination-note-without-event.json": (variant(up_vacc, B + ["adverse_event"], False), "/items/0/body/adverse_note schema"),
        "invalid-leish-collection-without-animal.json": (variant(up_leish, B + ["animal_id"], DELETE), "/items/0/body required"),
        "invalid-leish-collection-dpp-without-date.json": (variant(up_leish, B + ["dpp_on"], DELETE), "/items/0/body/dpp_result dependentRequired"),
        "invalid-leish-collection-dpp-inconclusive.json": (variant(up_leish, B + ["dpp_result"], "inconclusive"), "/items/0/body/dpp_result enum"),
        "invalid-collar-two-animals.json": (variant(up_collar, B + ["animal_client_uuid"], cz(2)), "/items/0/body oneOf"),
        "invalid-collar-without-animal.json": (variant(up_collar, B + ["animal_id"], DELETE), "/items/0/body required"),
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
        "upload-response-zoonoses-accepted.json": (resp_zoonoses_accepted(), "valid"),
        "upload-response-zoonoses-rejected.json": (resp_zoonoses_rejected(), "valid"),
        "invalid-response-leish-collection-without-label.json": (results(zdone(4, "leish_collection", LTEST)), "/results/0 required"),
        "invalid-response-label-on-collar.json": (results(dict(zdone(5, "collar", COLLAR), label="LV-2026-F1A2B3-0001")), "/results/0/label schema"),
        "invalid-response-label-lowercase-hex.json": (results(dict(zdone(4, "leish_collection", LTEST), label="LV-2026-f1a2b3-0001")), "/results/0/label pattern"),
        "invalid-response-animal-accepted-without-version.json": (results(zdone(2, "animal", ANIMAL)), "/results/0 required"),
        "invalid-response-version-on-vaccination.json": (results(dict(zdone(3, "rabies_vaccination", VACC), version=1)), "/results/0/version schema"),
        "upload-response-stale-animal.json": (resp_stale_animal(), "valid"),
        "invalid-response-stale-animal-with-microchip.json": (variant(resp_stale_animal, ["results", 0, "current", "microchip"], "985112003456789"), "/results/0/current/microchip schema"),
        "invalid-response-stale-vaccination.json": (variant(resp_stale_animal, ["results", 0, "type"], "rabies_vaccination"), "/results/0/type enum"),
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
        "invalid-changes-ovitrap-with-resident.json": (variant(page_vector, ["items", 2, "body", "resident_name"], "Maria Teste"), "/items/2/body/resident_name schema"),
        "invalid-changes-household-vector-risk-blue.json": (variant(page_vector, ["items", 0, "body", "vector", "risk_class"], "blue"), "/items/0/body/vector/risk_class enum"),
        "changes-zoonoses-page.json": (page_zoonoses(), "valid"),
        "changes-zoonoses-removals.json": (page_zoonoses_removals(), "valid"),
        "invalid-changes-animal-with-microchip.json": (variant(page_zoonoses, ["items", 1, "body", "microchip"], "985112003456789"), "/items/1/body/microchip schema"),
        "invalid-changes-animal-tutor-with-cpf.json": (variant(page_zoonoses, ["items", 1, "body", "tutor", "cpf"], "52998224725"), "/items/1/body/tutor/cpf schema"),
        "invalid-changes-leish-survey-with-target-dogs.json": (variant(page_zoonoses, ["items", 3, "body", "target_dogs"], 180), "/items/3/body/target_dogs schema"),
        "invalid-changes-animal-species-bird.json": (variant(page_zoonoses, ["items", 1, "body", "species"], "bird"), "/items/1/body/species enum"),
        "invalid-changes-animal-without-item-version.json": (variant(page_zoonoses, ["items", 1, "version"], DELETE), "/items/1 required"),
        "invalid-changes-leish-survey-without-item-version.json": (variant(page_zoonoses, ["items", 3, "version"], DELETE), "/items/3 required"),
        "invalid-changes-leish-survey-no-households.json": (variant(page_zoonoses, ["items", 3, "body", "household_ids"], []), "/items/3/body/household_ids minItems"),
        "invalid-changes-removal-animal-deceased.json": (variant(page_zoonoses_removals, ["removals", 0, "reason"], "deceased"), "/removals/0/reason enum"),
        **{f"invalid-changes-animal-without-{k.replace('_', '-')}.json": (variant(page_zoonoses, ["items", 1, "body", k], DELETE), "/items/1/body required") for k in ANIMAL_REQUIRED},
        **{f"invalid-changes-animal-tutor-without-{k.replace('_', '-')}.json": (variant(page_zoonoses, ["items", 1, "body", "tutor", k], DELETE), "/items/1/body/tutor required") for k in ["patient_id", "display_name"]},
        **{f"invalid-changes-leish-survey-without-{k.replace('_', '-')}.json": (variant(page_zoonoses, ["items", 3, "body", k], DELETE), "/items/3/body required") for k in LEISH_REQUIRED},
    }),
    ("reference-response-v1.json", {
        "reference.json": (reference(), "valid"),
        "invalid-reference-version-short.json": (variant(reference, ["reference_version"], "cd"), "/reference_version pattern"),
        "invalid-reference-professional-with-cpf.json": (variant(reference, ["team_professionals", 0, "cpf"], "39053344705"), "/team_professionals/0/cpf schema"),
        "invalid-reference-professional-without-has-cns.json": (variant(reference, ["team_professionals", 0, "has_cns"], DELETE), "/team_professionals/0 required"),  # Q6
        "invalid-reference-domain-as-object.json": (variant(reference, ["registration_dictionaries", "domains", "renda_familiar"], {"3": "1/2 a 1 salário mínimo"}), "/registration_dictionaries/domains/renda_familiar array"),  # Q27
        "invalid-reference-without-health-units.json": (variant(reference, ["health_units"], DELETE), "(root) required"),
        "invalid-reference-activity-rules-old-vocabulary.json": (variant(reference, ["collective_activity_domains", "rules"], {"by_activity_type": {}}), "/collective_activity_domains/rules required"),
        "invalid-reference-activity-by-type-old-value.json": (variant(reference, ["collective_activity_domains", "rules", "by_type", "1", "health_topics"], "with_meeting_topic_6"), "/collective_activity_domains/rules/by_type/1/health_topics enum"),
        "reference-vector-control.json": (reference_vector(), "valid"),
        "invalid-reference-product-charge-size-number.json": (variant(reference_vector, ["vector_control_domains", "products", 0, "charge_size"], 1), "/vector_control_domains/products/0/charge_size string"),
        "invalid-reference-product-without-uses.json": (variant(reference_vector, ["vector_control_domains", "products", 0, "uses"], []), "/vector_control_domains/products/0/uses minItems"),
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
