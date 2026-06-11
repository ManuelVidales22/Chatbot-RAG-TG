"""Extrae y normaliza el temario (temas y subtemas) de microcurrículos."""
import re

SUBTOPIC_PATTERN = re.compile(r"\b\d+\.\d+\b")
MAIN_TOPIC_PATTERN = re.compile(r"(?<!\d)\b(\d+)\.\s+")

END_MARKERS = re.compile(
    r"\b(METODOLOG[IÍ]A|RECURSOS DE APOYO|EVALUACI[OÓ]N DEL CURSO|EVALUACI[OÓ]N|BIBLIOGRAF[IÍ]A|Herramientas a usar)\b",
    re.IGNORECASE,
)

INDICATOR_LINE = re.compile(
    r"^[·•]\s*(Identifica|Reconoce|Maneja|Aplica|Resuelve|Emplea|Desarrolla|Es capaz|Describe|Generaliza|Utiliza)\b",
    re.IGNORECASE,
)


def has_numbered_syllabus(text):
    return len(SUBTOPIC_PATTERN.findall(text)) >= 3


def has_bullet_syllabus(text):
    return text.count("●") >= 3 or text.count("•") >= 4


def find_syllabus_region(text):
    preferred_patterns = [
        r"##\s*Contenidos\s+Tem[aá]ticos",
        r"Contenidos\s+Tem[aá]ticos",
        r"CONTENIDO\s+SCC",
        r"CONTENIDO\s+C\.E",
        r"CONTENIDO\s+RA",
        r"Contenido\s+\d+\.",
        r"DESARROLLO DEL CURSO[\s\S]{0,4000}?\bCONTENIDO\b",
    ]
    start = -1
    for pattern in preferred_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = match.start()
            break

    if start < 0:
        upper = text.upper()
        desarrollo_idx = upper.find("DESARROLLO DEL CURSO")
        contenido_idx = upper.find("CONTENIDO", desarrollo_idx if desarrollo_idx >= 0 else 0)
        if contenido_idx >= 0:
            start = contenido_idx
        elif desarrollo_idx >= 0:
            start = desarrollo_idx
        else:
            contenido_simple = re.search(r"\bContenido\b", text, re.IGNORECASE)
            start = contenido_simple.start() if contenido_simple else 0

    end_match = END_MARKERS.search(text, start + 20)
    end = end_match.start() if end_match else len(text)
    region = text[start:end].strip()

    if len(region) < 100 or (not has_numbered_syllabus(region) and not has_bullet_syllabus(region)):
        match = SUBTOPIC_PATTERN.search(text)
        if match:
            start = max(0, match.start() - 200)
            end_match = END_MARKERS.search(text, match.end())
            end = end_match.start() if end_match else min(len(text), match.end() + 4000)
            region = text[start:end].strip()

    return region


def normalize_numbered_lines(text):
    text = SUBTOPIC_PATTERN.sub(lambda match: f"\n{match.group()} ", text)
    text = re.sub(r"(?<!\d)\b(\d+)\.\s+([A-ZÁÉÍÓÚÑ])", r"\n\1. \2", text)

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if INDICATOR_LINE.match(line):
            continue
        if re.match(r"^RA\d", line):
            continue
        if "SCC" in line and "RA" in line and len(line) < 100:
            continue
        lines.append(line)

    return "\n".join(lines)


def strip_syllabus_header_noise(text):
    text = re.sub(
        r"^.*?\bCONTENIDO\b\s*(?:SCC\s*\d+|C\.E\.|RA\.?|\d+)?[:\s]*",
        "",
        text,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(r"^.*?\bRESULTADO DE APRENDIZAJE\b.*?(?=\n|$)", "", text, flags=re.IGNORECASE)
    return text.strip()


def normalize_bullet_lines(text):
    text = strip_syllabus_header_noise(text)
    text = re.sub(r"\s*●\s*", "\n- ", text)
    text = re.sub(r"\s*•\s*", "\n- ", text)
    # Temas numerados sueltos (p. ej. "1.\n\nCaracterísticas Generales")
    text = re.sub(r"(?<!\d)\b(\d+)\.\s*\n", r"\n\1. ", text)
    text = re.sub(r"(?<!\d)\b(\d+)\.\s+([A-ZÁÉÍÓÚÑ])", r"\n\1. \2", text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def format_as_markdown(subject_name, body):
    return (
        f"## Contenidos temáticos — {subject_name}\n\n"
        f"Listado oficial de temas y subtemas del microcurrículo:\n\n{body}"
    )


def extract_syllabus(text, subject_name):
    """
    Extrae temario normalizado en Markdown.
    Retorna None si no se detecta estructura temática suficiente.
    """
    region = find_syllabus_region(text)
    if not region:
        return None

    if has_numbered_syllabus(region):
        body = normalize_numbered_lines(region)
    elif has_bullet_syllabus(region):
        body = normalize_bullet_lines(region)
    else:
        body = normalize_bullet_lines(normalize_numbered_lines(region))

    if len(body) < 80:
        return None

    has_structure = (
        SUBTOPIC_PATTERN.search(body)
        or body.count("- ") >= 3
        or bool(MAIN_TOPIC_PATTERN.search(body))
        or len(re.findall(r"(?<!\d)\b\d+\.\s+[A-ZÁÉÍÓÚÑ]", body)) >= 2
    )
    if not has_structure:
        return None

    return format_as_markdown(subject_name, body)
