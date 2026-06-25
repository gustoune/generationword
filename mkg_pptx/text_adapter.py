"""Adaptateur texte / markdown leger -> specification de deck.

Conventions (volontairement simples ; pour un controle total, utiliser la spec
JSON ou l'API) :

- Un bloc front-matter optionnel delimite par `---` en tete fournit la meta et
  la couverture :

      ---
      title: Etude d'implantation hoteliere
      subtitle: Residence les Aigues Blanches - Aix-les-Bains
      eyebrow: MKG - Rapport d'etude - 2025
      doc_line: MKG Consulting - Etude - Aix-les-Bains - 2025
      Client: Turenne Hotellerie
      Date: Novembre 2025
      ---

  Les cles connues (title, subtitle, eyebrow, doc_line) pilotent la couverture ;
  toute autre cle `K: V` devient une meta de couverture.

- `# Titre`           -> slide de transition (section).
- `## Titre`          -> slide de contenu. Le corps est deduit du contenu :
                         lignes `-` -> bullets ; tableau `| a | b |` -> table ;
                         sinon -> paragraphes. Une ligne `> ...` -> encadre.
- `### Eyebrow`       -> eyebrow de la slide de contenu courante.
- `1.` / `2.` ...     -> liste numerotee.
"""
from __future__ import annotations

import re
from pathlib import Path

_NUM_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")


def _split_front_matter(text):
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is not None:
            fm = {}
            for ln in lines[1:end]:
                if ":" in ln:
                    k, v = ln.split(":", 1)
                    fm[k.strip()] = v.strip()
            return fm, "\n".join(lines[end + 1:])
    return {}, text


def _flush_table(buf):
    rows = []
    for ln in buf:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        rows.append(cells)
    if not rows:
        return None
    return {"type": "table", "headers": rows[0],
            "rows": rows[1:], "aligns": ["left"] + ["right"] * (len(rows[0]) - 1)}


def _body_from(paras, bullets, numbered, table_buf, quote):
    if table_buf:
        blk = _flush_table(table_buf)
        if blk:
            return blk
    if numbered:
        return {"type": "numbered", "items": numbered}
    if bullets:
        return {"type": "bullets", "items": bullets}
    blk = {"type": "paragraphs", "paras": paras or [""]}
    if quote:
        blk["highlight"] = {"title": "A retenir", "text": quote}
    return blk


def text_to_spec(text: str) -> dict:
    fm, rest = _split_front_matter(text)
    meta = {"doc_line": fm.get("doc_line", "")}
    known = {"title", "subtitle", "eyebrow", "doc_line"}
    cover = {"type": "cover", "title": fm.get("title", "Presentation"),
             "subtitle": fm.get("subtitle", ""), "eyebrow": fm.get("eyebrow", ""),
             "meta": [[k, v] for k, v in fm.items() if k not in known]}
    slides = [cover]

    cur = None
    paras, bullets, numbered, table_buf, quote = [], [], [], [], ""

    def close():
        nonlocal cur, paras, bullets, numbered, table_buf, quote
        if cur is not None:
            cur["body"] = _body_from(paras, bullets, numbered, table_buf, quote)
            slides.append(cur)
        cur = None
        paras, bullets, numbered, table_buf, quote = [], [], [], [], ""

    for raw in rest.splitlines():
        ln = raw.rstrip()
        st = ln.strip()
        if not st:
            continue
        if st.startswith("# ") and not st.startswith("## "):
            close()
            slides.append({"type": "section", "number": "", "title": st[2:].strip()})
        elif st.startswith("## "):
            close()
            cur = {"type": "content", "title": st[3:].strip(), "eyebrow": ""}
        elif st.startswith("### "):
            if cur is not None:
                cur["eyebrow"] = st[4:].strip()
        elif st.startswith("|"):
            table_buf.append(ln)
        elif st.startswith("> "):
            quote = st[2:].strip()
        elif _NUM_RE.match(st):
            numbered.append(_NUM_RE.match(st).group(1).strip())
        elif st.startswith(("- ", "* ")):
            bullets.append(st[2:].strip())
        else:
            paras.append(st)
    close()
    return {"meta": meta, "slides": slides}


def text_file_to_spec(path) -> dict:
    return text_to_spec(Path(path).read_text(encoding="utf-8"))
