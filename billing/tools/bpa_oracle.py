"""Oráculo independente do arquivo de interface do BPA Magnético.

Layout: Layout_Exportacao_BPA.pdf do DATASUS de 09/07/2026 (BPA 05.00).
Gera os exemplos golden de billing/examples a partir de dados fixos. Não
compartilha código com o api: é a segunda implementação que o teste golden
do api compara byte a byte. Uso: python3 -I billing/tools/bpa_oracle.py <dir>
"""
import datetime
import hashlib
import sys
import unicodedata

SHEET_LINES = 20


def text(value, size):
    """Maiúsculas ASCII, só letras e espaço, espaços colapsados, corte no tamanho do campo."""
    plain = unicodedata.normalize("NFKD", value or "")
    plain = "".join(c for c in plain if not unicodedata.combining(c)).upper()
    plain = "".join(c if ("A" <= c <= "Z") or c == " " else " " for c in plain)
    return " ".join(plain.split())[:size].ljust(size)


def addr(value, size):
    """Endereço: maiúsculas ASCII, letras, dígitos e espaço, espaços colapsados, corte no tamanho do campo."""
    plain = unicodedata.normalize("NFKD", value or "")
    plain = "".join(c for c in plain if not unicodedata.combining(c)).upper()
    plain = "".join(c if ("A" <= c <= "Z") or ("0" <= c <= "9") or c == " " else " " for c in plain)
    return " ".join(plain.split())[:size].ljust(size)


def opt_num(value, size):
    return num(value, size) if value else blank(size)


def num(value, size):
    digits = str(value)
    assert digits.isdigit() and len(digits) <= size, (value, size)
    return digits.rjust(size, "0")


def alfa(value, size):
    value = value or ""
    assert len(value) <= size, (value, size)
    return value.ljust(size)


def blank(size):
    return " " * size


def header_line(h, lines, sheets, control):
    line = ("01" + "#BPA#" + num(h["competence"], 6) + num(lines, 6) + num(sheets, 6) + num(control, 4)
            + text(h["origin_name"], 30) + text(h["origin_acronym"], 6) + num(h["origin_cnpj"], 14)
            + text(h["destination_body"], 40) + alfa(h["management"], 1) + alfa("ROTASAUDE", 10))
    assert len(line) == 130
    return line


def c_line(r, sheet, seq):
    line = ("02" + num(r["cnes"], 7) + num(r["competence"], 6) + alfa(r["cbo"], 6) + num(sheet, 3) + num(seq, 2)
            + num(r["procedure"], 10) + num(r["age"], 3) + num(r["quantity"], 6) + "BPA")
    assert len(line) == 48
    return line


def i_line(r, sheet, seq):
    line = ("03" + num(r["cnes"], 7) + num(r["competence"], 6) + num(r["professional_cns"], 15) + alfa(r["cbo"], 6)
            + r["performed_on"].strftime("%Y%m%d") + num(sheet, 3) + num(seq, 2) + num(r["procedure"], 10)
            + blank(15)                                                  # CNS do paciente: nunca junto do CPF
            + alfa(r["sex"], 1) + num(r["ibge"], 6) + alfa(r["cid10"], 4) + num(r["age"], 3) + num(r["quantity"], 6)
            + r["character"] + blank(13) + "BPA"                          # caráter, autorização, origem
            + text(r["name"], 30) + r["birth_date"].strftime("%Y%m%d") + num(r["race"], 2) + opt_num(r["ethnicity"], 4)
            + blank(3) + blank(3) + blank(3) + blank(8) + blank(4) + blank(14)        # nac., serviço, classif., equipe, CNPJ OPM
            + num(r["zip"], 8) + blank(3) + addr(r["street"], 30) + addr(r["complement"], 10) + addr(r["number"], 5)
            + addr(r["district"], 30) + alfa(r["phone"], 11) + blank(40)              # bairro, telefone, e-mail
            + blank(10) + num(r["cpf"], 11) + blank(1) + "N")                         # INE, CPF, situação de rua, sem CPF
    assert len(line) == 351
    return line


def build(h, c_rows, i_rows):
    out, sheet = [], 0
    c_sorted = sorted(c_rows, key=lambda r: (r["cbo"], r["procedure"], r["age"], r["competence"]))
    for k in range(0, len(c_sorted), SHEET_LINES):
        sheet += 1
        out += [c_line(r, sheet, seq) for seq, r in enumerate(c_sorted[k:k + SHEET_LINES], 1)]
    i_sorted = sorted(i_rows, key=lambda r: (r["professional_cns"], r["cbo"], r["performed_on"], r["procedure"], r["key"]))
    groups = []
    for r in i_sorted:
        if groups and groups[-1][0] == (r["professional_cns"], r["cbo"]):
            groups[-1][1].append(r)
        else:
            groups.append(((r["professional_cns"], r["cbo"]), [r]))
    for _, rows in groups:
        for k in range(0, len(rows), SHEET_LINES):
            sheet += 1
            out += [i_line(r, sheet, seq) for seq, r in enumerate(rows[k:k + SHEET_LINES], 1)]
    control = sum(int(r["procedure"]) + r["quantity"] for r in c_rows + i_rows) % 1111 + 1111
    return (header_line(h, len(out), sheet, control) + "\r\n" + "".join(line + "\r\n" for line in out)).encode("ascii")


def age(born, on):
    return on.year - born.year - ((on.month, on.day) < (born.month, born.day))


HEADER = {"competence": "202609", "origin_name": "SMS Curitiba", "origin_acronym": "", "origin_cnpj": "11222333000181",
          "destination_body": "Secretaria Municipal de Saúde", "management": "M"}
C_CODES = ["0202010473", "0202020380", "0202010317"]
PROFESSIONALS = [("798312812760829", "225125"), ("765218542269265", "223505")]
NAMES = ["Maria Aparecida da Silva", "José Antônio Pereira", "Ana Lúcia D'Ávila Gonçalves", "João Batista Conceição",
         "Luíza Helena de Araújo Fontes Bittencourt"]
RACES = ["01", "02", "03", "04", "05"]
CPFS = ["29136237191", "66012407106", "99378987656", "93842327501", "96273885648", "87159190726", "06446750714",
        "28441315817", "74747239723", "93161173481", "18425542049", "10271688769", "28258981714", "38263611130",
        "23441850114", "22458158749", "37499727378", "18615318263", "05596308676", "42719726737", "02622189095",
        "19833011594", "74018474776", "33531950410", "79387458989"]


def c_rows():
    return [{"cnes": "1234567", "competence": "202609", "cbo": "221205", "procedure": C_CODES[i % 3], "age": 20 + i,
             "quantity": i + 1} for i in range(21)]


def i_rows():
    rows = []
    for j in range(25):
        on = datetime.date(2026, 9, 1 + j % 28)
        born = datetime.date(1950 + j, 1 + j % 12, 1 + j % 27)
        cns, cbo = PROFESSIONALS[0] if j < 22 else PROFESSIONALS[1]
        rows.append({"key": "i%02d" % j, "cnes": "7654321", "competence": "202609", "professional_cns": cns, "cbo": cbo,
                     "performed_on": on, "procedure": "0301010072" if j < 22 else "0301010048",
                     "sex": "F" if j % 2 == 0 else "M", "ibge": "410690", "cid10": "I10" if j % 3 == 0 else "",
                     "age": age(born, on), "quantity": 1, "character": "02" if j % 4 == 0 else "01",
                     "name": NAMES[j % 5], "birth_date": born, "race": RACES[j % 5], "ethnicity": "0001" if j % 5 == 4 else "",
                     "zip": "80010000" if j % 2 == 0 else "81020130",
                     "street": "Rua XV de Novembro" if j % 2 == 0 else "Av. Sete de Setembro, 2.775",
                     "number": "1200" if j % 3 else "SN", "complement": "Apto 12" if j % 4 == 1 else "",
                     "district": "Centro" if j % 2 == 0 else "Rebouças",
                     "phone": "4199%07d" % j if j % 3 else "", "cpf": CPFS[j]})
    return rows


if __name__ == "__main__":
    target = sys.argv[1]
    examples = {"bpa-c-21-lines.txt": build(HEADER, c_rows(), []),
                "bpa-i-25-lines.txt": build(HEADER, [], i_rows()),
                "bpa-mixed.txt": build(HEADER, c_rows()[:2], i_rows()[:2])}
    for name, data in examples.items():
        with open(f"{target}/{name}", "wb") as f:
            f.write(data)
        print(hashlib.sha256(data).hexdigest() + "  " + name)
