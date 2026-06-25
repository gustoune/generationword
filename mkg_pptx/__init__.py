"""mkg_pptx - generation de presentations PowerPoint a la charte MKG Consulting.

API principale :

    from mkg_pptx import MKGDeck, build_from_spec

    deck = MKGDeck(doc_line="MKG Consulting - Etude - 2025")
    deck.add_cover(title="...", eyebrow="...", meta=[["Client", "..."]])
    deck.content(eyebrow="...", title="...", body={"type": "kpis", "cards": [...]})
    deck.save("sortie.pptx")
"""
from __future__ import annotations

from .builder import MKGDeck
from .spec import build_from_spec

__all__ = ["MKGDeck", "build_from_spec"]
