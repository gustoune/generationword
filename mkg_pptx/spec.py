"""Construction d'un deck a partir d'une specification JSON declarative.

Format :

{
  "meta": {"doc_line": "...", "scale": 2, "grain": true},
  "slides": [
    {"type": "cover", "title": "...", "eyebrow": "...", "subtitle": "...",
     "meta": [["Client", "Turenne"], ["Date", "Nov. 2025"]],
     "kpis": [{"value": "84", "label": "Appartements"}],
     "footer_note": "Document confidentiel"},
    {"type": "agenda", "title": "Sommaire", "eyebrow": "...", "subtitle": "...",
     "items": [{"title": "...", "desc": "..."}]},
    {"type": "section", "number": "01", "title": "...", "eyebrow": "...",
     "desc": "...", "toc": [{"label": "...", "active": true}]},
    {"type": "content", "eyebrow": "...", "title": "...", "badge": "...",
     "body": {...}  |  "columns": [ {...}, {...} ]},
    {"type": "gen", "eyebrow": "...", "title": "...", "subtitle": "...",
     "dark": false, "intro": false, "body": {...} | "columns": [{...}, {...}]},
    {"type": "beforeafter",
     "before": {"tag": "Avant", "headline": "...", "points": ["..."]},
     "after":  {"tag": "Apres", "headline": "...", "points": ["..."]}},
    {"type": "stat", "number": "1,2M", "unit": "", "eyebrow": "...",
     "desc": "...", "source": "...", "dark": false},
    {"type": "quote", "text": "...", "author": "..."},
    {"type": "closing", "title": "...", "eyebrow": "...", "subtitle": "...",
     "contacts": [{"label": "...", "name": "...", "role": "...", "lines": ["..."]}]},
    {"type": "merci", "title": "Merci", "subtitle": "...", "contact": "..."}
  ]
}

Blocs de corps (`body` / `columns`) : voir reference.md (paragraphs, bullets,
numbered, kpis, table, swot, reco, timeline, takeaways, features, cards,
concept, steps, steps2, ranking, linechart, photos, table_grouped).
"""
from __future__ import annotations

import json
from pathlib import Path

from .builder import MKGDeck


def _tuples(seq):
    return [tuple(x) if isinstance(x, (list, tuple)) else x for x in (seq or [])]


def build_from_spec(spec, out_path) -> Path:
    if isinstance(spec, (str, Path)):
        spec = json.loads(Path(spec).read_text(encoding="utf-8"))
    meta = spec.get("meta", {})
    deck = MKGDeck(doc_line=meta.get("doc_line", ""),
                   scale=int(meta.get("scale", 2)),
                   grain=bool(meta.get("grain", True)))
    for s in spec.get("slides", []):
        _add_slide(deck, s)
    return deck.save(out_path)


def _add_slide(deck: MKGDeck, s: dict) -> None:
    t = s.get("type")
    if t == "cover":
        deck.add_cover(title=s.get("title", ""), eyebrow=s.get("eyebrow", ""),
                       subtitle=s.get("subtitle", ""), meta=_tuples(s.get("meta")),
                       kpis=s.get("kpis", []),
                       footer_note=s.get("footer_note", ""))
    elif t == "agenda":
        deck.add_agenda(title=s.get("title", "Sommaire"), eyebrow=s.get("eyebrow", ""),
                        subtitle=s.get("subtitle", ""), items=s.get("items", []))
    elif t == "section":
        deck.add_section(number=s.get("number", ""), title=s.get("title", ""),
                         eyebrow=s.get("eyebrow", ""), desc=s.get("desc", ""),
                         toc=s.get("toc", []))
    elif t == "content":
        deck.content(eyebrow=s.get("eyebrow", ""), title=s.get("title", ""),
                     badge=s.get("badge", ""), body=s.get("body"),
                     columns=s.get("columns"))
    elif t == "gen":
        deck.gen(eyebrow=s.get("eyebrow", ""), title=s.get("title", ""),
                 subtitle=s.get("subtitle", ""), body=s.get("body"),
                 columns=s.get("columns"), dark=bool(s.get("dark")),
                 title_size=int(s.get("title_size", 46)), intro=bool(s.get("intro")))
    elif t == "beforeafter":
        deck.add_beforeafter(before=s.get("before", {}), after=s.get("after", {}),
                             eyebrow=s.get("eyebrow", ""), title=s.get("title", ""))
    elif t == "stat":
        deck.add_stat(number=s.get("number", ""), unit=s.get("unit", ""),
                      eyebrow=s.get("eyebrow", ""), desc=s.get("desc", ""),
                      source=s.get("source", ""), dark=bool(s.get("dark")))
    elif t == "quote":
        deck.add_quote(text=s.get("text", ""), author=s.get("author", ""))
    elif t == "closing":
        deck.add_closing(title=s.get("title", ""), eyebrow=s.get("eyebrow", ""),
                         subtitle=s.get("subtitle", ""), contacts=s.get("contacts", []))
    elif t == "merci":
        deck.add_merci(title=s.get("title", "Merci"), subtitle=s.get("subtitle", ""),
                       contact=s.get("contact", ""))
    else:
        raise ValueError(f"Type de slide inconnu : {t!r}")
