"""Interface ligne de commande du generateur Word MKG.

Exemples :
    python -m mkg_docx.cli spec exemple.json sortie.docx
    python -m mkg_docx.cli text note.md sortie.docx
    python -m mkg_docx.cli reformat source.docx sortie.docx --cover --date "Juin 2026"
    python -m mkg_docx.cli demo demo.docx
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .spec import build_from_spec, build_from_spec_file
from .text_adapter import text_to_spec


def _cmd_spec(args):
    doc = build_from_spec_file(args.spec)
    out = doc.save(args.out)
    print(f"OK -> {out}")


def _cmd_text(args):
    text = Path(args.input).read_text(encoding="utf-8")
    spec = text_to_spec(text)
    doc = build_from_spec(spec)
    out = doc.save(args.out)
    print(f"OK -> {out}")


def _cmd_reformat(args):
    from .reformat import reformat_docx
    out = reformat_docx(args.src, args.out, orientation=args.orientation,
                        add_cover=args.cover, study_title=args.title,
                        author=args.author, date=args.date, subtitle=args.subtitle)
    print(f"OK -> {out}")


def _cmd_demo(args):
    from .demo import build_demo
    out = build_demo(args.out, orientation=args.orientation)
    print(f"OK -> {out}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mkg_docx",
                                     description="Generateur Word a la charte MKG")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("spec", help="Genere depuis une spec JSON")
    p.add_argument("spec")
    p.add_argument("out")
    p.set_defaults(func=_cmd_spec)

    p = sub.add_parser("text", help="Genere depuis un texte / markdown leger")
    p.add_argument("input")
    p.add_argument("out")
    p.set_defaults(func=_cmd_text)

    p = sub.add_parser("reformat", help="Remet un .docx existant a la charte")
    p.add_argument("src")
    p.add_argument("out")
    p.add_argument("--orientation", default="portrait", choices=["portrait", "paysage", "landscape"])
    p.add_argument("--cover", action="store_true", help="Ajoute une couverture")
    p.add_argument("--title", default=None)
    p.add_argument("--author", default=None)
    p.add_argument("--subtitle", default="")
    p.add_argument("--date", default="")
    p.set_defaults(func=_cmd_reformat)

    p = sub.add_parser("demo", help="Genere un document de demonstration complet")
    p.add_argument("out")
    p.add_argument("--orientation", default="portrait", choices=["portrait", "paysage", "landscape"])
    p.set_defaults(func=_cmd_demo)

    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
