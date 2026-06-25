"""Conversions d'unites pour la charte slides MKG.

La charte est dessinee sur un canevas fixe 1920x1080 px (16:9). En PowerPoint,
ce canevas vaut exactement 13,333 x 7,5 pouces, soit 144 px par pouce. Les
conversions sont donc exactes et sans approximation :

- 1 px  = 6350 EMU         (914400 / 144)
- 1 px  = 0,5 pt           (72 / 144)

On peut ainsi transcrire les coordonnees et tailles du CSS directement en px.
"""
from __future__ import annotations

from pptx.util import Emu, Pt

EMU_PER_PX = 6350
PT_PER_PX = 0.5

SLIDE_W_PX = 1920
SLIDE_H_PX = 1080


def emu(px: float) -> Emu:
    """px (canevas 1920x1080) -> EMU PowerPoint."""
    return Emu(int(round(px * EMU_PER_PX)))


def pt(px: float) -> Pt:
    """Taille de police en px (charte) -> points PowerPoint."""
    return Pt(px * PT_PER_PX)


def pt_val(px: float) -> float:
    """Valeur numerique en points (sans objet Pt)."""
    return px * PT_PER_PX
