import re
import json

with open("medicina.xml", "r", encoding="utf-8") as f:
    xml = f.read()

# Extrair conteúdo das tags <text>
texts = re.findall(r"<text[^>]*>(.*?)</text>", xml, re.DOTALL)

# Remover linhas <b>...</b> para ajudar na remoçaõ dos Vid
texts = [re.sub(r"<b>\s*(?!\d)[^<]*</b>", "", t) if not re.match(r"^\s*\d", re.sub(r"<.*?>", "", t)) else t for t in texts]

# Remover tags internas (<i>, <b>, etc.)
texts = [re.sub(r"<.*?>", "", t) for t in texts]

# Juntar tudo num único texto
text = "\n".join(t.strip() for t in texts if t.strip())

# Marcar início de conceito
text = re.sub(r"\n(\d+) ", r"@\1 ", text)

# Separar conceitos
concepts = re.split(r"@", text)

def process_concepts(c):
    c = re.sub(r"SIN\.-", r"@SIN.-", c)
    c = re.sub(r"VAR\.-", r"@VAR.-", c)
    c = re.sub(r"Nota\.-", r"@NOTA.-", c)
    c = re.sub(r"(?m)^(en|pt|es|la)\s", r"#\1 ", c)
    c = re.sub(r"^.*Vid\.-.*$", "", c, flags=re.MULTILINE)
    c = re.sub(r"^.*Vid\..*$", "", c, flags=re.MULTILINE)

    id = re.search(r"^(\d+)", c)
    # Extrai termo e classe gramatical (f, m, a) se existir
    term_match = re.search(r"^\d+\s+(.+?)\s+([fma])(?:\s|$)", c, re.IGNORECASE)
    if term_match:
        term = term_match.group(1).strip()
        classe = term_match.group(2).lower()
    else:
        term = None
        classe = None
    sin = re.search(r"@SIN\.-([^@#]+)", c)
    var = re.search(r"@VAR\.-([^@#]+)", c)
    nota = re.search(r"@NOTA\.-([^@#]+)", c)
    es = re.search(r"#es\s([^@#]+)", c)
    en = re.search(r"#en\s([^@#]+)", c)
    pt = re.search(r"#pt\s([^@#]+)", c)
    la = re.search(r"#la\s([^@#]+)", c)

    def extract_translations(match):
        if not match:
            return []
        text = re.sub(r"\s*\n\s*", " ", match.group(1))
        return [t.strip() for t in text.split(";")]

    return {
        "id": id.group(1) if id else None,
        "ga": term,
        "classe": classe,
        "sin": sin.group(1).strip() if sin else None,
        "var": var.group(1).strip() if var else None,
        "nota": nota.group(1).strip() if nota else None,
        "es": extract_translations(es),
        "en": extract_translations(en),
        "pt": extract_translations(pt),
        "la": extract_translations(la)
    }

entries = []
for c in concepts:
    if c.strip():
        entry = process_concepts(c)
        if entry["id"]:
            entries.append(entry)

with open("dicionario_medicina_xml.json", "w", encoding="utf8") as f_out:
    json.dump(entries, f_out, indent=4, ensure_ascii=False)

print(f"Processados {len(entries)} conceitos")
print(f"Guardados em dicionario_medicina_xml.json")