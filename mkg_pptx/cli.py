"""Interface en ligne de commande pour mkg_pptx.

    python -m mkg_pptx.cli spec   entree.json   sortie.pptx
    python -m mkg_pptx.cli text   note.md       sortie.pptx
    python -m mkg_pptx.cli demo   demo.pptx
"""
from __future__ import annotations

import argparse
import sys

from .builder import MKGDeck
from .spec import build_from_spec
from .text_adapter import text_file_to_spec


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="mkg_pptx", description="Generateur de decks MKG")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_spec = sub.add_parser("spec", help="Construire depuis une spec JSON")
    p_spec.add_argument("input")
    p_spec.add_argument("output")

    p_text = sub.add_parser("text", help="Construire depuis un texte / markdown leger")
    p_text.add_argument("input")
    p_text.add_argument("output")

    p_demo = sub.add_parser("demo", help="Generer le deck de demonstration")
    p_demo.add_argument("output")

    args = parser.parse_args(argv)

    if args.cmd == "spec":
        out = build_from_spec(args.input, args.output)
    elif args.cmd == "text":
        out = build_from_spec(text_file_to_spec(args.input), args.output)
    elif args.cmd == "demo":
        from .demo import build_demo
        out = build_demo(args.output)
    else:  # pragma: no cover
        parser.error("commande inconnue")
        return 2

    print(f"OK -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
