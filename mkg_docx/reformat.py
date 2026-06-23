"""Remise a la charte MKG d'un .docx existant (mode << reformat >>).

Strategie robuste (sources mixtes) :
- pre-scan : titre reel (style Title / 1er titre), sous-titre, auteur valide,
  et niveaux de titres reellement utilises -> remappes relativement (le plus
  haut niveau present devient un titre de section, quelle que soit sa valeur) ;
- lecture du document dans l'ordre (paragraphes + tableaux) ;
- classement par style Word, a defaut par heuristiques (longueur, gras, taille) ;
- tableaux 2 colonnes a libelles courts -> fiche cle/valeur (pas d'en-tete data) ;
- amorces en gras des puces preservees ;
- reconstruction d'un MKGDocument propre (en-tete/pied/pagination, couverture
  optionnelle).
"""
from __future__ import annotations

import re
from pathlib import Path
from statistics import mean

from docx import Document as OpenDocx
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from .builder import MKGDocument

_NUM_RE = re.compile(r"^[\(\-\u2212]?[\d\s\u00a0.,]+\s*(%|\u20ac|M\u20ac|pt|\u00d7|x)?\s*$")
_PLACEHOLDER_AUTHORS = {"", "un-named", "unnamed", "unknown", "user",
                        "utilisateur", "auteur", "windows user"}

_HEADING_LEVEL = {
    "heading 1": 1, "titre 1": 1, "heading1": 1, "title": 0, "titre": 0,
    "heading 2": 2, "titre 2": 2, "heading2": 2,
    "heading 3": 3, "titre 3": 3, "heading3": 3,
    "heading 4": 4, "titre 4": 4, "heading 5": 5, "titre 5": 5,
}


def _iter_block_items(doc):
    body = doc.element.body
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield Table(child, doc)


def _style_level(par: Paragraph):
    """Niveau de titre depuis le style Word, sinon None. 0 = Title."""
    style = (par.style.name or "").strip().lower() if par.style else ""
    return _HEADING_LEVEL.get(style)


def _is_list(par: Paragraph) -> bool:
    style = (par.style.name or "").strip().lower() if par.style else ""
    if "list" in style:
        return True
    return par._p.find(".//" + qn("w:numPr")) is not None


def _bullet_segments(par: Paragraph):
    """Separe l'amorce en gras (lead) du reste d'une puce."""
    text = re.sub(r"^[\u2022\u2013\u2014\-\*\u00b7\s]+", "", par.text.strip())
    lead = ""
    consumed = 0
    for run in par.runs:
        rt = run.text
        if not rt.strip():
            consumed += len(rt)
            continue
        if run.bold:
            lead += rt
            consumed += len(rt)
        else:
            break
    lead = re.sub(r"^[\u2022\u2013\u2014\-\*\u00b7\s]+", "", lead).strip()
    if lead and text.startswith(lead):
        rest = text[len(lead):]
        return lead, rest
    return "", text


def _looks_numeric(text: str) -> bool:
    return bool(_NUM_RE.match(text.strip())) and any(c.isdigit() for c in text)


def _is_key_value(rows: list[list[str]]) -> bool:
    if not rows or len(rows[0]) != 2:
        return False
    col0 = [r[0] for r in rows if r and r[0]]
    col1 = [r[1] for r in rows if len(r) > 1 and r[1]]
    if not col0 or not col1:
        return False
    labels_short = all(len(c) <= 28 for c in col0)
    vals_textual = not all(_looks_numeric(c) for c in col1)
    longer_values = mean(len(c) for c in col1) > mean(len(c) for c in col0)
    return labels_short and vals_textual and longer_values


def _table_to_charte(doc: MKGDocument, tbl: Table) -> None:
    rows = [[c.text.strip() for c in r.cells] for r in tbl.rows]
    if not rows:
        return
    if _is_key_value(rows):
        doc.key_value([(r[0], r[1] if len(r) > 1 else "") for r in rows])
        return
    headers = rows[0]
    body = rows[1:]
    ncol = len(headers)
    aligns = ["left"] * ncol
    for j in range(ncol):
        sample = [r[j] for r in body if j < len(r) and r[j]]
        if sample and all(_looks_numeric(v) for v in sample):
            aligns[j] = "num"
    footer = None
    if body and body[-1] and re.search(r"total|ensemble", body[-1][0], re.I):
        footer = body[-1]
        body = body[:-1]
    doc.table(headers, body, footer=footer, aligns=aligns)


def reformat_docx(src: str | Path, out: str | Path, *,
                  orientation: str = "portrait", add_cover: bool = False,
                  study_title: str | None = None, author: str | None = None,
                  date: str = "", subtitle: str = "") -> Path:
    src_doc = OpenDocx(str(src))
    props = src_doc.core_properties

    # ----- pre-scan -----
    title_par = None
    subtitle_par = None
    levels = set()
    first_heading_seen = False
    for item in _iter_block_items(src_doc):
        if isinstance(item, Table):
            first_heading_seen = True
            continue
        lvl = _style_level(item)
        if lvl is not None and lvl >= 1:
            levels.add(lvl)
            first_heading_seen = True
        if lvl == 0 and title_par is None and item.text.strip():
            title_par = item
        elif (title_par is not None and subtitle_par is None
              and not first_heading_seen and lvl is None
              and item.text.strip()):
            subtitle_par = item

    base_level = min(levels) if levels else 2

    detected_title = (props.title or "").strip()
    if not detected_title and title_par is not None:
        detected_title = title_par.text.strip()
    title = study_title or detected_title or Path(src).stem

    detected_sub = subtitle or (subtitle_par.text.strip() if subtitle_par else "")

    raw_author = author if author is not None else (props.author or "").strip()
    if raw_author.lower() in _PLACEHOLDER_AUTHORS:
        raw_author = ""

    mkg = MKGDocument(orientation=orientation, study_title=title, date=date)

    if add_cover:
        fields = []
        if raw_author:
            fields.append(("Auteur", raw_author))
        if date:
            fields.append(("Date", date))
        mkg.add_cover(title=title, eyebrow="Document", subtitle=detected_sub,
                      fields=fields, confidential=mkg.confidential)

    skip_ids = set()
    if title_par is not None:
        skip_ids.add(id(title_par._p))
    if add_cover and subtitle_par is not None:
        skip_ids.add(id(subtitle_par._p))

    bullet_buffer: list = []

    def flush_bullets():
        if bullet_buffer:
            mkg.bullets(bullet_buffer.copy())
            bullet_buffer.clear()

    def emit_heading(level: int, text: str):
        if level <= base_level:
            mkg.section_title(text)
        else:
            mkg.subheading(text)

    for item in _iter_block_items(src_doc):
        if isinstance(item, Table):
            flush_bullets()
            _table_to_charte(mkg, item)
            continue
        if id(item._p) in skip_ids:
            continue
        text = item.text.strip()
        if not text:
            continue

        if _is_list(item):
            lead, rest = _bullet_segments(item)
            bullet_buffer.append((lead, rest) if lead else rest)
            continue
        flush_bullets()

        lvl = _style_level(item)
        if lvl == 0:
            mkg.title_h1(text)
            continue
        if lvl is not None and lvl >= 1:
            emit_heading(lvl, text)
            continue

        # heuristique pour le style Normal
        max_size = max((r.font.size.pt for r in item.runs if r.font.size), default=0.0)
        any_bold = any(r.bold for r in item.runs)
        short = len(text) <= 90
        no_end_punct = not text.endswith((".", ":", ";", ","))
        if short and no_end_punct and (any_bold or max_size >= 13):
            mkg.subheading(text)
        else:
            mkg.paragraph(text)
    flush_bullets()

    return mkg.save(out)
