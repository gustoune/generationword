"""Charte MKG Consulting - source unique de verite pour la generation PPTX.

Tokens extraits de `slides.css` (deck 16:9 1920x1080). Aucune valeur de couleur,
taille ou marge ne doit etre ecrite en dur ailleurs dans le moteur.
"""
from __future__ import annotations

from pptx.dml.color import RGBColor

# ============================================================
# COULEURS (slides.css :root + declinaisons)
# ============================================================
BLUE = "0634AC"          # bleu MKG primaire (bandeaux, KPI, titres)
BLUE_600 = "042A8A"      # bleu fonce
BLUE_50 = "E8EDF8"       # tint clair (fonds de panneau)
ELECTRIC = "1F66F6"      # accent electrique (en-tetes de tableau, liens)
DARK = "0A0E1A"          # fonds couverture / transition / cloture
GRAY = "B4B4B4"          # gris neutre

# Neutres de contenu
WHITE = "FFFFFF"
INK = "1A1A1A"           # corps de texte sur fond clair
INK_SOFT = "3D3D3D"      # texte secondaire
INK_MUTED = "636363"     # descriptions / sous-titres
INK_FAINT = "8A8A8A"     # labels / legendes
LINE_LIGHT = "E8E8E8"    # filets clairs
PANEL = "F5F5F5"         # fonds de carte neutres
FEAT_BG = "F5F7FC"       # carte feature (grille 4 box) - blanc bleute
ROW_ALT = "EEF1FC"       # ligne paire de tableau (tint bleute)

# Semantique
POS = "166534"           # variation positive (texte)
NEG = "991B1B"           # variation negative (texte)
SUCCESS = "16A34A"       # vert vif (badges, barres)
DANGER = "DC2626"        # rouge vif

# Tint methodologie / cartes accent claires
TINT_ALT = "DBEAFE"

# Pros / cons (SWOT)
SWOT_PRO_BG = "F0F7F2"
SWOT_PRO_BORDER = "CCE8D6"
SWOT_PRO_TITLE = "166534"
SWOT_CON_BG = "FDF3F3"
SWOT_CON_BORDER = "F3D4D4"
SWOT_CON_TITLE = "991B1B"


def rgb(hex_str: str) -> RGBColor:
    return RGBColor.from_string(hex_str)


def rgb_tuple(hex_str: str) -> tuple[int, int, int]:
    return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))


# ============================================================
# TYPOGRAPHIE
# ============================================================
FONT = "Segoe UI"
FONT_LIGHT = "Segoe UI Light"
FONT_SEMILIGHT = "Segoe UI Semilight"
FONT_SEMIBOLD = "Segoe UI Semibold"

# Graisses logiques -> (nom de police, bold) pour le rendu natif PPTX
WEIGHTS = {
    "light": (FONT_LIGHT, False),
    "semilight": (FONT_SEMILIGHT, False),
    "regular": (FONT, False),
    "semibold": (FONT_SEMIBOLD, False),
    "bold": (FONT, True),
    "black": (FONT, True),
}

# Graisses logiques -> graisse fichier Pillow (pages brand rasterisees)
PILLOW_WEIGHT = {
    "light": "light", "semilight": "semilight", "regular": "regular",
    "semibold": "semibold", "bold": "bold", "black": "black",
}


# ============================================================
# GEOMETRIE DU CANEVAS (px)
# ============================================================
W = 1920
H = 1080

# Bandeau d'en-tete des slides de contenu (.content-header)
HEADER_H = 122          # hauteur approx du bandeau bleu
HEADER_PAD_X = 72
FOOTER_H = 78           # .content-footer
BODY_PAD_X = 72
BODY_PAD_Y = 56


# ============================================================
# TEXTES PAR DEFAUT
# ============================================================
SIGNATURE = "MKG Consulting"
CONFIDENTIAL_LINE = "Document confidentiel \u00b7 Usage exclusif"
TAGLINE = "L'intelligence de marche au service de l'hotellerie et de l'hospitality."
