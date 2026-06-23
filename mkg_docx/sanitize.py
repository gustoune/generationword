"""Assainissement editorial du texte selon la charte MKG.

Deux regles imposees a tout contenu textuel injecte dans un document :

1. Aucun tiret typographique. Les cadratins, demi-cadratins, barres et signe
   moins Unicode sont normalises en trait d'union ASCII ``-``.
2. Aucun pictogramme / emoji. Les blocs Unicode d'emoji et de pictogrammes sont
   supprimes. Les etoiles ``*`` (U+2605 / U+2606) restent autorisees car elles
   servent au classement hotelier, qui est un contenu metier legitime.

``clean()`` est applique au plus bas niveau (runs Word et primitives de texte
Pillow) : tout texte produit par le moteur est ainsi systematiquement nettoye,
quelle que soit sa source (specification JSON, adaptateur texte, remise a la
charte d'un .docx existant ou appels directs de l'API).
"""
from __future__ import annotations

import re

# Tirets typographiques et signe moins -> trait d'union simple.
_DASH_RE = re.compile("[\u2010-\u2015\u2212]")

# Pictogrammes / emoji a supprimer. On conserve volontairement les etoiles
# pleines / vides (U+2605 / U+2606) utilisees pour le classement hotelier, ainsi
# que le point median U+00B7 (separateur de charte) qui n'appartient a aucune
# plage ci-dessous. On couvre emoji, fleches, formes geometriques (puces
# carrees/rondes/triangulaires), symboles divers et techniques, dingbats, et les
# puces de la plage Ponctuation generale, en fractionnant autour des etoiles.
_EMOJI_RE = re.compile(
    "["
    "\U00002022\U00002023\U00002043\U0000204C\U0000204D"  # puces . ‣ ⁃ ⁌ ⁍
    "\U00002190-\U000021FF"   # fleches (-> <- up down, etc.)
    "\U00002219"              # operateur puce ∙
    "\U00002300-\U000023FF"   # symboles techniques divers
    "\U00002460-\U000024FF"   # alphanumeriques encadres (① ② ...)
    "\U000025A0-\U000025FF"   # formes geometriques (puces . . . carres, ronds)
    "\U00002600-\U00002604"   # symboles divers (avant l'etoile pleine)
    "\U00002607-\U000026FF"   # symboles divers (apres l'etoile vide)
    "\U00002700-\U000027BF"   # dingbats
    "\U00002900-\U0000297F"   # fleches supplementaires B
    "\U00002B00-\U00002BFF"   # symboles et fleches divers (etoiles emoji, etc.)
    "\U0001F000-\U0001FAFF"   # emoji, pictogrammes, transport, symboles etendus
    "\U0000FE00-\U0000FE0F"   # selecteurs de variation (presentation emoji)
    "\U0000200D"              # liant sans largeur (sequences emoji)
    "]+",
    flags=re.UNICODE,
)

# Espaces multiples laisses par la suppression d'un picto entoure d'espaces.
_MULTISPACE_RE = re.compile(r"  +")


def clean(text):
    """Normalise les tirets et retire les pictogrammes d'une chaine.

    Renvoie l'argument tel quel si ce n'est pas une chaine non vide.
    L'effondrement des espaces n'a lieu que si un picto a reellement ete retire,
    afin de ne jamais alterer une mise en forme volontaire.
    """
    if not isinstance(text, str) or not text:
        return text
    text = _DASH_RE.sub("-", text)
    stripped = _EMOJI_RE.sub("", text)
    if stripped != text:
        stripped = _MULTISPACE_RE.sub(" ", stripped)
    return stripped
