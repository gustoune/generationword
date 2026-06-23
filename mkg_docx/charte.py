"""Charte MKG Consulting - source unique de verite pour la generation Word.

Tokens extraits de `colors_and_type.css` (couche Document V6 << Refonte MARS >>)
et du Brand Kit. Tout le reste du moteur consomme ces constantes : aucune
valeur de couleur / taille / marge ne doit etre ecrite en dur ailleurs.
"""
from __future__ import annotations

from docx.shared import Mm, Pt, RGBColor

# ============================================================
# COULEURS
# ============================================================
# Couche Document V6 (documents Word/PDF)
INK = "2D3A5E"          # corps de texte navy (jamais noir pur) - couleur dominante
INK_SOFT = "5A6890"     # texte secondaire / legendes
INK_MUTED = "9AA5C4"    # texte tertiaire / en-tete courant
INK_FAINT = "8A9FD4"    # filets clairs
BLUE_DEEP = "0131B4"    # bleu primaire document - titres + chiffres cles
ELECTRIC = "1F66F6"     # accents, en-tetes de tableaux, liens
DARK = "0A0E1E"         # couvertures & pages de transition
TINT = "EEF1FC"         # fond de panneau / ligne paire de tableau
TINT2 = "E6EEFE"        # ligne impaire de tableau

# Ramp / web
BLUE_PRIMARY = "0634AC"  # bleu MKG (logo, web)
WHITE = "FFFFFF"
GRAY_100 = "E8E8E8"
GRAY_500 = "636363"

# Semantique (valeurs lisibles sur fond clair)
POS = "166534"          # variation positive
NEG = "991B1B"          # variation negative
SUCCESS = "16A34A"
WARNING = "D97706"
DANGER = "DC2626"

# Variantes "dark" (sur fond sombre)
DARK_POS = "4ADE80"
DARK_NEG = "F87171"


def rgb(hex_str: str) -> RGBColor:
    return RGBColor.from_string(hex_str)


def rgb_tuple(hex_str: str) -> tuple[int, int, int]:
    return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))


# ============================================================
# TYPOGRAPHIE
# ============================================================
FONT = "Segoe UI"
FONT_SEMILIGHT = "Segoe UI Semilight"
FONT_SEMIBOLD = "Segoe UI Semibold"
FONT_LIGHT = "Segoe UI Light"

# Echelle document (pt) - fidele a l'impression Word, corps dense 8,5pt
SIZE_DISPLAY = Pt(34)
SIZE_H1 = Pt(19)
SIZE_H2 = Pt(12)
SIZE_H3 = Pt(9)
SIZE_BODY = Pt(8.5)
SIZE_SMALL = Pt(7)
SIZE_EYEBROW = Pt(7.5)

# Tableaux denses
SIZE_TABLE_HEAD = Pt(6.5)
SIZE_TABLE_BODY = Pt(7.5)
SIZE_TABLE_FOOT = Pt(7.5)

# En-tete / pied courant
SIZE_RUNHEAD = Pt(6.5)
SIZE_RUNFOOT = Pt(6.5)
SIZE_PAGENO = Pt(8)

# Interlignes
LINE_BODY = 1.55
LINE_H3 = 1.3
LINE_H2 = 1.2

# Tracking (letter-spacing) en em -> convertis en twips a l'usage
TRACK_H2_EM = 0.06
TRACK_EYEBROW_EM = 0.14
TRACK_RUNHEAD_EM = 0.14


def tracking_twips(em: float, size_pt: float) -> int:
    """Convertit un letter-spacing CSS (em) en valeur w:spacing (1/20 pt)."""
    return round(em * size_pt * 20)


# ============================================================
# MISE EN PAGE / FORMATS A4
# ============================================================
PAGE_MARGIN_Y = Mm(16)
PAGE_MARGIN_X = Mm(14)
HEADER_DISTANCE = Mm(9)
FOOTER_DISTANCE = Mm(9)

A4_PORTRAIT = (Mm(210), Mm(297))
A4_LANDSCAPE = (Mm(297), Mm(210))

# Marges des pages "brand" pleine page (couverture, intercalaire, fin) : zero bleed
BLEED_MARGIN = Mm(0)


# ============================================================
# TEXTES PAR DEFAUT
# ============================================================
CONFIDENTIAL_LINE = "MKG CONSULTING \u00b7 DOCUMENT CONFIDENTIEL"
SIGNATURE = "MKG Consulting"
