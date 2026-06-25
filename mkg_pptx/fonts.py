"""Resolution des fichiers de police Segoe UI pour le rendu Pillow.

La charte MKG impose Segoe UI. Pour les slides << brand >> (couverture,
transition, citation, stat, merci, cloture) le texte est rasterise par Pillow,
qui a besoin d'un fichier de police reel. On cherche, dans l'ordre :

1. les polices embarquees dans le package (mkg_pptx/fonts/) ;
2. C:\\Windows\\Fonts (Windows) ;
3. les emplacements usuels macOS / Linux.

Sur une machine sans Segoe UI, deposez les .ttf dans mkg_pptx/fonts/ pour un
rendu pixel-perfect ; sinon un repli systeme est utilise (uniquement pour les
images des slides brand : le texte natif des slides de contenu reste Segoe UI).
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

_BUNDLED_FONTS = Path(__file__).resolve().parent / "fonts"
_WIN_FONTS = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
_EXTRA_FONT_DIRS = [
    Path("/Library/Fonts"),
    Path("/System/Library/Fonts"),
    Path.home() / "Library" / "Fonts",
    Path("/usr/share/fonts"),
    Path("/usr/local/share/fonts"),
    Path.home() / ".fonts",
    Path.home() / ".local" / "share" / "fonts",
]

_CANDIDATES = {
    "light": ["segoeuil.ttf", "SegoeUI-Light.ttf"],
    "semilight": ["segoeuisl.ttf", "SegoeUI-Semilight.ttf"],
    "regular": ["segoeui.ttf", "SegoeUI.ttf"],
    "semibold": ["seguisb.ttf", "SegoeUI-Semibold.ttf"],
    "bold": ["segoeuib.ttf", "SegoeUI-Bold.ttf"],
    "black": ["seguibl.ttf", "segoeuib.ttf", "SegoeUI-Bold.ttf"],
}

_FALLBACK_ORDER = ["regular", "semibold", "bold", "light", "semilight", "black"]

_SYSTEM_FALLBACK = [
    "DejaVuSans.ttf", "DejaVuSans-Bold.ttf",
    "Arial.ttf", "arial.ttf", "Helvetica.ttf",
    "LiberationSans-Regular.ttf",
]


def _search_dirs():
    yield _BUNDLED_FONTS
    yield _WIN_FONTS
    for d in _EXTRA_FONT_DIRS:
        yield d


def _find_file(names: list[str]) -> str | None:
    for base in _search_dirs():
        if not base.exists():
            continue
        for name in names:
            p = base / name
            if p.exists():
                return str(p)
    for base in _search_dirs():
        if not base.exists():
            continue
        for name in names:
            for hit in base.rglob(name):
                return str(hit)
    return None


@lru_cache(maxsize=None)
def _resolve_path(weight: str) -> str | None:
    return _find_file(_CANDIDATES.get(weight, []))


@lru_cache(maxsize=512)
def get_font(weight: str, size_px: int) -> ImageFont.FreeTypeFont:
    """Retourne une police Segoe UI de la graisse demandee, avec repli."""
    path = _resolve_path(weight)
    if path is None:
        for fb in _FALLBACK_ORDER:
            path = _resolve_path(fb)
            if path:
                break
    if path is None:
        path = _find_file(_SYSTEM_FALLBACK)
    if path is None:
        return ImageFont.load_default()
    return ImageFont.truetype(path, size_px)
