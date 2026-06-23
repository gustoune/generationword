"""Rendu Pillow des pages << brand >> pleine page (bleed) de la charte MKG.

Ces pages (couverture, intercalaire de chapitre, page de fin) reposent sur des
fonds sombres avec split diagonal / bande verticale bleue + texture, que docx ne
sait pas reproduire nativement. On les rend donc en une image pleine page,
inseree ensuite sans marge dans le .docx.

Toutes les images sont produites a `dpi` (defaut 200) pour un A4 net.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFilter

from . import charte
from . import sanitize
from .fonts import get_font

DEFAULT_DPI = 200
MM_PER_INCH = 25.4
PT_PER_INCH = 72.0


def mm_to_px(mm: float, dpi: int) -> int:
    return round(mm / MM_PER_INCH * dpi)


def pt_to_px(pt: float, dpi: int) -> int:
    return round(pt / PT_PER_INCH * dpi)


def _c(hex_str: str, alpha: int = 255) -> tuple[int, int, int, int]:
    r, g, b = charte.rgb_tuple(hex_str)
    return (r, g, b, alpha)


# ------------------------------------------------------------------
# Primitives de fond
# ------------------------------------------------------------------
def _clip_halfplane(rect_pts, a, b, c):
    """Sutherland-Hodgman : garde la portion ou a*x + b*y >= c."""
    out = []
    n = len(rect_pts)
    for i in range(n):
        cur = rect_pts[i]
        nxt = rect_pts[(i + 1) % n]
        cur_in = (a * cur[0] + b * cur[1]) >= c
        nxt_in = (a * nxt[0] + b * nxt[1]) >= c
        if cur_in:
            out.append(cur)
        if cur_in != nxt_in:
            d_cur = a * cur[0] + b * cur[1] - c
            d_nxt = a * nxt[0] + b * nxt[1] - c
            t = d_cur / (d_cur - d_nxt)
            out.append((cur[0] + t * (nxt[0] - cur[0]),
                        cur[1] + t * (nxt[1] - cur[1])))
    return out


def diagonal_split(img: Image.Image, angle_deg: float, stop: float,
                   color_b: str) -> None:
    """Remplit la moitie << avant >> d'un gradient lineaire CSS par une couleur pleine.

    Reproduit `linear-gradient(angle, color_a 0 stop, color_b stop 100%)` :
    le fond (color_a) est deja en place, on peint la region color_b.
    """
    w, h = img.size
    rad = math.radians(angle_deg)
    dx, dy = math.sin(rad), -math.cos(rad)
    corners = [(0, 0), (w, 0), (w, h), (0, h)]
    projs = [dx * x + dy * y for x, y in corners]
    pmin, pmax = min(projs), max(projs)
    c = pmin + stop * (pmax - pmin)
    poly = _clip_halfplane(corners, dx, dy, c)
    if len(poly) >= 3:
        ImageDraw.Draw(img).polygon(poly, fill=_c(color_b))


def add_grain(img: Image.Image, opacity: float = 0.05, seed: int = 7) -> None:
    """Grain subtil (texture de couverture) en blend << screen >> leger."""
    if opacity <= 0:
        return
    rnd = random.Random(seed)
    w, h = img.size
    small = Image.new("L", (w // 4, h // 4))
    small.putdata([rnd.randint(0, 255) for _ in range(small.width * small.height)])
    noise = small.resize((w, h))
    overlay = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    alpha = noise.point(lambda v: int(v * opacity))
    overlay.putalpha(alpha)
    img.alpha_composite(overlay)


# ------------------------------------------------------------------
# Texte
# ------------------------------------------------------------------
def _text(draw, xy, text, font, fill, anchor="la"):
    draw.text(xy, sanitize.clean(text), font=font, fill=fill, anchor=anchor)


def _tracked(draw, xy, text, font, fill, track_px, anchor_right=False):
    """Texte avec letter-spacing (eyebrows / labels uppercase)."""
    text = sanitize.clean(text)
    widths = [font.getlength(ch) + track_px for ch in text]
    total = sum(widths)
    x, y = xy
    if anchor_right:
        x -= total
    for ch, wch in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += wch
    return total


def _paste_logo(img, logo_path, x, y, height_px, align_right=False):
    logo = Image.open(logo_path).convert("RGBA")
    ratio = height_px / logo.height
    logo = logo.resize((round(logo.width * ratio), height_px))
    if align_right:
        x -= logo.width
    img.alpha_composite(logo, (round(x), round(y)))
    return logo.width


def _rounded_mask(size, radius):
    w, h = size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    return m


def logo_badge(img, logo_path, *, center_xy, badge_w, badge_h, logo_h,
               blur_px, shadow_dy, logo_shift_x=0):
    """Cartouche blanc << stadium >> (coins totalement arrondis) avec ombre douce,
    contenant le logo bleu MKG.

    Regle de charte : sur fond bleu / sombre / photo, le logo n'est JAMAIS pose nu
    sur la couleur ni en noir -> il est toujours place dans ce cartouche blanc
    arrondi (classe `.mkg-logo-badge`). Le cartouche peut deborder hors page.
    """
    badge_w = round(badge_w)
    badge_h = round(badge_h)
    radius = badge_h // 2
    mask = _rounded_mask((badge_w, badge_h), radius)
    cx, cy = center_xy
    x0 = round(cx - badge_w / 2)
    y0 = round(cy - badge_h / 2)

    # Ombre portee : box-shadow 0 8px 36px rgba(10,14,30,0.28)
    pad = blur_px * 3
    sh = Image.new("RGBA", (badge_w + 2 * pad, badge_h + 2 * pad), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", (badge_w, badge_h), (10, 14, 30, 72)), (pad, pad), mask)
    sh = sh.filter(ImageFilter.GaussianBlur(blur_px))
    img.alpha_composite(sh, (x0 - pad, y0 - pad + shadow_dy))

    # Cartouche blanc
    badge = Image.new("RGBA", (badge_w, badge_h), (0, 0, 0, 0))
    badge.paste(Image.new("RGBA", (badge_w, badge_h), (255, 255, 255, 255)), (0, 0), mask)

    logo = Image.open(logo_path).convert("RGBA")
    ratio = logo_h / logo.height
    logo = logo.resize((round(logo.width * ratio), round(logo_h)))
    lx = (badge_w - logo.width) // 2 + round(logo_shift_x)
    ly = (badge_h - logo.height) // 2
    badge.alpha_composite(logo, (lx, ly))
    img.alpha_composite(badge, (x0, y0))


# ------------------------------------------------------------------
# Specs de pages
# ------------------------------------------------------------------
@dataclass
class CoverSpec:
    title: str
    eyebrow: str = ""
    subtitle: str = ""
    fields: list[tuple[str, str]] = field(default_factory=list)  # (label, value)
    confidential: str = ""
    address: str = ""
    title_size_pt: float = 32.0


@dataclass
class DividerSpec:
    number: str
    title: str
    chapter_label: str = ""
    items: list[str] = field(default_factory=list)
    footer: str = ""


@dataclass
class EndSpec:
    tagline: str = "L'intelligence de march\u00e9 au service de l'h\u00f4tellerie et de l'hospitality."
    eyebrow: str = charte.SIGNATURE
    fields: list[tuple[str, str]] = field(default_factory=list)
    confidential: str = ""
    date: str = ""


class BrandPageRenderer:
    def __init__(self, page_w_mm: float, page_h_mm: float,
                 logo_white_path: str, logo_blue_path: str | None = None,
                 dpi: int = DEFAULT_DPI, grain: bool = True):
        self.dpi = dpi
        self.w = mm_to_px(page_w_mm, dpi)
        self.h = mm_to_px(page_h_mm, dpi)
        self.pad_x = mm_to_px(14, dpi)
        self.pad_y = mm_to_px(16, dpi)
        self.logo_white = logo_white_path
        self.logo_blue = logo_blue_path or logo_white_path
        self.grain = grain

    # -- helpers internes --
    def _base(self) -> Image.Image:
        img = Image.new("RGBA", (self.w, self.h), _c(charte.DARK))
        return img

    def _f(self, weight, size_pt):
        return get_font(weight, pt_to_px(size_pt, self.dpi))

    def _track(self, em: float, size_pt: float) -> float:
        """letter-spacing (em) -> px a la resolution courante."""
        return charte.tracking_twips(em, size_pt) / 20 * self.dpi / 72

    def _badge(self, img: Image.Image, *, center_y: float) -> None:
        """Cartouche logo blanc arrondi debordant du bord droit, centre sur center_y."""
        bw = mm_to_px(53, self.dpi)
        bh = mm_to_px(40, self.dpi)
        lh = mm_to_px(20, self.dpi)
        bleed = mm_to_px(19, self.dpi)
        cx = self.w + bleed - bw / 2
        logo_badge(img, self.logo_blue, center_xy=(cx, center_y),
                   badge_w=bw, badge_h=bh, logo_h=lh,
                   blur_px=mm_to_px(9, self.dpi), shadow_dy=mm_to_px(2, self.dpi),
                   logo_shift_x=-bleed / 2)

    # -- pages --
    def cover(self, spec: CoverSpec) -> Image.Image:
        img = self._base()
        diagonal_split(img, 115, 0.46, charte.BLUE_DEEP)
        if self.grain:
            add_grain(img, 0.06)
        draw = ImageDraw.Draw(img)
        px, py = self.pad_x, self.pad_y
        right = self.w - px

        # Logo : cartouche blanc arrondi debordant du bord droit (centre vertical)
        self._badge(img, center_y=self.h // 2)

        # Eyebrow haut-gauche
        if spec.eyebrow:
            f = self._f("semibold", charte.SIZE_EYEBROW.pt)
            _tracked(draw, (px, py), spec.eyebrow.upper(), f, _c(charte.WHITE, 190),
                     self._track(charte.TRACK_EYEBROW_EM, charte.SIZE_EYEBROW.pt))

        # Tout le contenu textuel dans la colonne gauche (~57 %)
        col_w = int(self.w * 0.57) - px

        # Titre (retour a la ligne + reduction auto)
        size = spec.title_size_pt
        lines = []
        while size > 16:
            ftitle = self._f("bold", size)
            lines = []
            for raw in spec.title.split("\n"):
                lines.extend(_wrap(raw, ftitle, col_w))
            if all(ftitle.getlength(l) <= col_w for l in lines):
                break
            size -= 2
        ftitle = self._f("bold", size)

        block_y = self.h - py - mm_to_px(96, self.dpi)
        ty = block_y
        for line in lines:
            _text(draw, (px, ty), line, ftitle, _c(charte.WHITE))
            ty += pt_to_px(size * 1.05, self.dpi)
        if spec.subtitle:
            ty += mm_to_px(4, self.dpi)
            _text(draw, (px, ty), spec.subtitle, self._f("regular", 11),
                  _c(charte.WHITE, 185))
            ty += pt_to_px(13, self.dpi)

        # Filet + champs (colonne gauche)
        if spec.fields:
            ty += mm_to_px(5, self.dpi)
            draw.line([(px, ty), (px + col_w, ty)], fill=_c(charte.WHITE, 60), width=1)
            ty += mm_to_px(5, self.dpi)
            flabel = self._f("semibold", charte.SIZE_EYEBROW.pt)
            fval = self._f("regular", 9)
            label_x = px + mm_to_px(28, self.dpi)
            for label, value in spec.fields:
                _tracked(draw, (px, ty + pt_to_px(1, self.dpi)), label.upper(), flabel,
                         _c(charte.INK_FAINT),
                         self._track(charte.TRACK_EYEBROW_EM, charte.SIZE_EYEBROW.pt))
                _text(draw, (label_x, ty), value, fval, _c(charte.WHITE))
                ty += pt_to_px(15, self.dpi)

        # Filet + ligne de bas
        line_y = self.h - py
        draw.line([(px, line_y), (right, line_y)], fill=_c(charte.WHITE, 50), width=1)
        fsmall = self._f("regular", charte.SIZE_SMALL.pt)
        if spec.confidential:
            _tracked(draw, (px, line_y + mm_to_px(2, self.dpi)), spec.confidential.upper(),
                     fsmall, _c(charte.WHITE, 140),
                     0.14 * charte.SIZE_SMALL.pt * self.dpi / 72)
        if spec.address:
            _text(draw, (right, line_y + mm_to_px(2, self.dpi)), spec.address, fsmall,
                  _c(charte.WHITE, 140), anchor="ra")
        return img

    def divider(self, spec: DividerSpec) -> Image.Image:
        img = self._base()
        band_x = int(self.w * 0.62)
        ImageDraw.Draw(img).rectangle([band_x, 0, self.w, self.h], fill=_c(charte.BLUE_DEEP))
        if self.grain:
            add_grain(img, 0.05)
        draw = ImageDraw.Draw(img)
        px, py = self.pad_x, self.pad_y
        right = self.w - px

        # Logo : cartouche blanc arrondi debordant en haut a droite (sur la bande bleue)
        self._badge(img, center_y=mm_to_px(34, self.dpi))
        if spec.chapter_label:
            f = self._f("semibold", charte.SIZE_EYEBROW.pt)
            _tracked(draw, (px, py), spec.chapter_label.upper(), f,
                     _c(charte.WHITE, 190),
                     self._track(charte.TRACK_EYEBROW_EM, charte.SIZE_EYEBROW.pt))

        # numero geant + titre
        fnum = self._f("bold", 110)
        num_y = int(self.h * 0.52)
        _text(draw, (px, num_y), spec.number, fnum, _c(charte.ELECTRIC))
        ftitle = self._f("bold", 30)
        _text(draw, (px, num_y + pt_to_px(118, self.dpi)), spec.title, ftitle, _c(charte.WHITE))

        # sommaire local (a droite, sur bande bleue)
        if spec.items:
            fitem = self._f("regular", 9)
            flabel = self._f("semibold", charte.SIZE_EYEBROW.pt)
            ix = band_x + mm_to_px(10, self.dpi)
            iy = int(self.h * 0.55)
            _tracked(draw, (ix, iy), "DANS CE CHAPITRE", flabel, _c(charte.WHITE, 150),
                     0.14 * charte.SIZE_EYEBROW.pt * self.dpi / 72)
            iy += pt_to_px(16, self.dpi)
            for it in spec.items:
                _text(draw, (ix, iy), it, fitem, _c(charte.WHITE))
                iy += pt_to_px(11, self.dpi)
                draw.line([(ix, iy), (self.w - px, iy)], fill=_c(charte.WHITE, 50), width=1)
                iy += pt_to_px(6, self.dpi)

        # bas
        line_y = self.h - py
        draw.line([(px, line_y), (right, line_y)], fill=_c(charte.WHITE, 50), width=1)
        if spec.footer:
            fsmall = self._f("regular", charte.SIZE_SMALL.pt)
            _tracked(draw, (px, line_y + mm_to_px(2, self.dpi)), spec.footer.upper(),
                     fsmall, _c(charte.WHITE, 140),
                     0.14 * charte.SIZE_SMALL.pt * self.dpi / 72)
        return img

    def end(self, spec: EndSpec) -> Image.Image:
        img = self._base()
        diagonal_split(img, 115, 0.54, charte.BLUE_DEEP)
        if self.grain:
            add_grain(img, 0.06)
        draw = ImageDraw.Draw(img)
        px, py = self.pad_x, self.pad_y
        right = self.w - px

        # Logo : cartouche blanc arrondi debordant du bord droit (centre vertical)
        self._badge(img, center_y=self.h // 2)

        block_y = self.h - py - mm_to_px(72, self.dpi)
        if spec.eyebrow:
            f = self._f("semibold", charte.SIZE_EYEBROW.pt)
            _tracked(draw, (px, block_y), spec.eyebrow.upper(), f, _c(charte.WHITE, 150),
                     self._track(charte.TRACK_EYEBROW_EM, charte.SIZE_EYEBROW.pt))
        ftag = self._f("light", 17)
        ty = block_y + mm_to_px(6, self.dpi)
        for line in _wrap(spec.tagline, ftag, int(self.w * 0.52)):
            _text(draw, (px, ty), line, ftag, _c(charte.WHITE))
            ty += pt_to_px(22, self.dpi)

        if spec.fields:
            ty += mm_to_px(6, self.dpi)
            flabel = self._f("semibold", charte.SIZE_EYEBROW.pt)
            fval = self._f("regular", 9)
            label_x = px + mm_to_px(28, self.dpi)
            for label, value in spec.fields:
                _tracked(draw, (px, ty + pt_to_px(1, self.dpi)), label.upper(), flabel,
                         _c(charte.INK_FAINT),
                         self._track(charte.TRACK_EYEBROW_EM, charte.SIZE_EYEBROW.pt))
                _text(draw, (label_x, ty), value, fval, _c(charte.WHITE))
                ty += pt_to_px(15, self.dpi)

        line_y = self.h - py
        draw.line([(px, line_y), (right, line_y)], fill=_c(charte.WHITE, 50), width=1)
        fsmall = self._f("regular", charte.SIZE_SMALL.pt)
        if spec.confidential:
            _tracked(draw, (px, line_y + mm_to_px(2, self.dpi)), spec.confidential.upper(),
                     fsmall, _c(charte.WHITE, 140),
                     0.14 * charte.SIZE_SMALL.pt * self.dpi / 72)
        if spec.date:
            _text(draw, (right, line_y + mm_to_px(2, self.dpi)), spec.date, fsmall,
                  _c(charte.WHITE, 140), anchor="ra")
        return img


def _wrap(text: str, font, max_px: int) -> list[str]:
    words = sanitize.clean(text).split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= max_px or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines
