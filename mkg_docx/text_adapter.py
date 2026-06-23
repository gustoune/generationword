"""Adaptateur << texte brut -> spec >> (fallback de confort).

Pour les cas riches, un agent produit directement la spec JSON ou appelle l'API
Python. Cet adaptateur couvre le besoin courant : transformer rapidement un
texte (markdown leger) en rapport a la charte.

Front-matter optionnel (entre deux lignes ``---``) :
    ---
    study_title: Etude d'implantation
    date: Novembre 2025
    orientation: portrait
    title: Residence les Aigues Blanches      # si present -> couverture
    subtitle: Aix-les-Bains, Savoie
    eyebrow: Etude d'implantation hoteliere
    client: Turenne Hotellerie
    author: Sylvie Bergeret
    ---

Corps :
    # Titre de section     -> section_title (filet degrade)
    ## Sous-titre          -> subheading
    ### Sous-titre         -> subheading
    - item / * item        -> liste a puces
    | a | b |              -> tableau (ligne de separation |---| ignoree)
    > insight              -> encadre insight
    ligne(s) de texte      -> paragraphe
"""
from __future__ import annotations

import re


def _parse_front_matter(text: str):
    meta = {}
    body = text
    if text.lstrip().startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
            body = parts[2]
    return meta, body


def _is_table_row(line: str) -> bool:
    return line.strip().startswith("|") and line.strip().endswith("|")


def _cells(line: str):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _looks_numeric(v: str) -> bool:
    return bool(re.match(r"^[\(\-\u2212]?[\d\s\u00a0.,]+\s*(%|\u20ac|M\u20ac|pt|\u00d7|x)?$", v.strip())) \
        and any(c.isdigit() for c in v)


def text_to_spec(text: str) -> dict:
    meta_raw, body = _parse_front_matter(text)
    meta = {
        "orientation": meta_raw.get("orientation", "portrait"),
        "study_title": meta_raw.get("study_title", meta_raw.get("title", "")),
        "date": meta_raw.get("date", ""),
    }
    if "confidential" in meta_raw:
        meta["confidential"] = meta_raw["confidential"]

    blocks = []

    # couverture si un titre de couverture est fourni
    if meta_raw.get("title"):
        fields = []
        if meta_raw.get("client"):
            fields.append(["Client", meta_raw["client"]])
        if meta_raw.get("author"):
            fields.append(["Auteur", meta_raw["author"]])
        if meta_raw.get("date"):
            fields.append(["Date", meta_raw["date"]])
        blocks.append({
            "type": "cover",
            "title": meta_raw["title"].replace("\\n", "\n"),
            "eyebrow": meta_raw.get("eyebrow", ""),
            "subtitle": meta_raw.get("subtitle", ""),
            "fields": fields,
            "confidential": meta_raw.get("confidential", ""),
            "address": meta_raw.get("address", ""),
        })

    lines = body.splitlines()
    i = 0
    para_buf: list[str] = []
    bullet_buf: list[str] = []

    def flush_para():
        if para_buf:
            blocks.append({"type": "paragraph", "text": " ".join(para_buf).strip()})
            para_buf.clear()

    def flush_bullets():
        if bullet_buf:
            blocks.append({"type": "bullets", "items": bullet_buf.copy()})
            bullet_buf.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_para()
            flush_bullets()
            i += 1
            continue

        if _is_table_row(line):
            flush_para()
            flush_bullets()
            tbl_lines = []
            while i < len(lines) and _is_table_row(lines[i]):
                tbl_lines.append(lines[i])
                i += 1
            rows = [_cells(l) for l in tbl_lines]
            rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
            if rows:
                headers = rows[0]
                data = rows[1:]
                ncol = len(headers)
                aligns = ["left"] * ncol
                for j in range(ncol):
                    sample = [r[j] for r in data if j < len(r) and r[j]]
                    if sample and all(_looks_numeric(v) for v in sample):
                        aligns[j] = "num"
                footer = None
                if data and re.search(r"total|ensemble", data[-1][0], re.I):
                    footer = data[-1]
                    data = data[:-1]
                blocks.append({"type": "table", "headers": headers, "rows": data,
                               "footer": footer, "aligns": aligns})
            continue

        if stripped.startswith("### "):
            flush_para(); flush_bullets()
            blocks.append({"type": "subheading", "text": stripped[4:].strip()})
        elif stripped.startswith("## "):
            flush_para(); flush_bullets()
            blocks.append({"type": "subheading", "text": stripped[3:].strip()})
        elif stripped.startswith("# "):
            flush_para(); flush_bullets()
            blocks.append({"type": "section_title", "text": stripped[2:].strip()})
        elif stripped.startswith(("- ", "* ")):
            flush_para()
            bullet_buf.append(stripped[2:].strip())
        elif stripped.startswith("> "):
            flush_para(); flush_bullets()
            blocks.append({"type": "insight", "text": stripped[2:].strip()})
        else:
            flush_bullets()
            para_buf.append(stripped)
        i += 1

    flush_para()
    flush_bullets()

    # page de fin si couverture
    if meta_raw.get("title"):
        blocks.append({
            "type": "end",
            "fields": [["Contact", meta_raw["author"]]] if meta_raw.get("author") else [],
            "confidential": meta_raw.get("confidential", ""),
            "date": meta_raw.get("date", ""),
        })

    return {"meta": meta, "blocks": blocks}
