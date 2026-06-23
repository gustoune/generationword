"""Spec declarative JSON -> MKGDocument.

Contrat d'entree canonique (celui qu'un agent produit a partir de texte brut) :

{
  "meta": {
    "orientation": "portrait" | "paysage",
    "study_title": "...",          # repris dans l'en-tete courant
    "date": "Novembre 2025",       # repris dans le pied
    "confidential": "...",         # ligne de pied (defaut charte)
    "grain": true
  },
  "blocks": [
    {"type": "cover", "title": "...", "eyebrow": "...", "subtitle": "...",
     "fields": [["Client", "..."], ["Auteur", "..."], ["Date", "..."]],
     "confidential": "...", "address": "...", "title_size_pt": 32},
    {"type": "divider", "number": "01", "title": "...",
     "chapter_label": "Chapitre 01", "items": ["...", "..."], "footer": "..."},
    {"type": "eyebrow", "text": "..."},
    {"type": "section_title", "text": "...", "rule": true},
    {"type": "title_h1", "text": "..."},
    {"type": "subheading", "text": "..."},
    {"type": "paragraph", "text": "..."},
    {"type": "small", "text": "..."},
    {"type": "bullets", "items": ["...", "..."]},
    {"type": "summary", "entries": [{"number": "01", "title": "...", "desc": "..."}]},
    {"type": "glossary", "entries": [{"term": "...", "definition": "..."}]},
    {"type": "insight", "text": "...", "eyebrow": "Insight cle"},
    {"type": "kpi", "cards": [{"label": "...", "value": "...", "trend": "...",
                               "trend_dir": "up", "variant": "default"}]},
    {"type": "table", "headers": ["..."], "rows": [["..."]], "footer": ["..."],
     "aligns": ["left", "num"], "col_ratios": [2, 1], "source": "..."},
    {"type": "gradient_rule"},
    {"type": "spacer", "pt": 6},
    {"type": "page_break"},
    {"type": "end", "tagline": "...", "eyebrow": "...", "fields": [["Contact", "..."]],
     "confidential": "...", "date": "..."}
  ]
}
"""
from __future__ import annotations

import json
from pathlib import Path

from .builder import MKGDocument


def _orientation(value: str | None) -> str:
    v = (value or "portrait").lower()
    return "landscape" if v in ("paysage", "landscape", "paysage", "land") else "portrait"


def build_from_spec(spec: dict) -> MKGDocument:
    meta = spec.get("meta", {})
    doc = MKGDocument(
        orientation=_orientation(meta.get("orientation")),
        study_title=meta.get("study_title", ""),
        date=meta.get("date", ""),
        confidential=meta.get("confidential", _default_conf()),
        grain=meta.get("grain", True),
    )
    for block in spec.get("blocks", []):
        _dispatch(doc, block)
    return doc


def _default_conf():
    from . import charte
    return charte.CONFIDENTIAL_LINE


def build_from_spec_file(path: str | Path) -> MKGDocument:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return build_from_spec(data)


def _dispatch(doc: MKGDocument, block: dict) -> None:
    btype = block.get("type")
    if btype == "cover":
        doc.add_cover(
            title=block["title"], eyebrow=block.get("eyebrow", ""),
            subtitle=block.get("subtitle", ""),
            fields=[tuple(f) for f in block.get("fields", [])],
            confidential=block.get("confidential", ""),
            address=block.get("address", ""),
            title_size_pt=block.get("title_size_pt", 32.0))
    elif btype == "divider":
        doc.add_divider(number=block["number"], title=block["title"],
                        chapter_label=block.get("chapter_label", ""),
                        items=block.get("items", []),
                        footer=block.get("footer", ""))
    elif btype == "end":
        doc.add_end(tagline=block.get("tagline"),
                    eyebrow=block.get("eyebrow"),
                    fields=[tuple(f) for f in block.get("fields", [])],
                    confidential=block.get("confidential", ""),
                    date=block.get("date", ""))
    elif btype == "eyebrow":
        doc.eyebrow(block["text"])
    elif btype == "section_title":
        doc.section_title(block["text"], rule=block.get("rule", True))
    elif btype == "title_h1":
        doc.title_h1(block["text"])
    elif btype == "subheading":
        doc.subheading(block["text"])
    elif btype == "paragraph":
        doc.paragraph(block["text"])
    elif btype == "small":
        doc.small(block["text"])
    elif btype == "bullets":
        doc.bullets(block["items"])
    elif btype == "summary":
        doc.summary(block["entries"])
    elif btype == "glossary":
        doc.glossary(block["entries"])
    elif btype == "insight":
        doc.insight(block["text"], eyebrow=block.get("eyebrow", "Insight cl\u00e9"))
    elif btype == "kpi":
        doc.kpi_row(block["cards"])
    elif btype == "table":
        doc.table(block["headers"], block["rows"], footer=block.get("footer"),
                  aligns=block.get("aligns"), col_ratios=block.get("col_ratios"),
                  source=block.get("source", ""))
    elif btype == "gradient_rule":
        doc.gradient_rule()
    elif btype == "spacer":
        doc.spacer(block.get("pt", 6.0))
    elif btype == "page_break":
        doc.page_break()
    else:
        raise ValueError(f"Type de bloc inconnu : {btype!r}")
