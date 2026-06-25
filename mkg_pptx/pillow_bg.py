"""Rendu Pillow des slides << brand >> pleine page de la charte MKG (16:9).

Ces slides (couverture, transition, stat hero, citation, merci, cloture)
reposent sur des fonds sombres / colores avec gradient diagonal, texture grain
et formes, que PowerPoint ne reproduit pas fidelement. On les rend donc en une
image pleine page (1920x1080 a l'echelle `scale`), inseree ensuite bord a bord
dans la slide.

Tout le texte de ces slides est rasterise ici (Segoe UI via Pillow).
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

from . import charte, sanitize
from .fonts import get_font


def _c(hex_str, alpha=255):
    r, g, b = charte.rgb_tuple(hex_str)
    return (r, g, b, alpha)


def _clip_halfplane(rect_pts, a, b, c):
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


class BrandRenderer:
    """Rend les slides brand a l'echelle `scale` (2 = 3840x2160, texte net)."""

    def __init__(self, assets_dir, *, scale: int = 2, grain: bool = True):
        self.s = scale
        self.W = charte.W * scale
        self.H = charte.H * scale
        self.grain = grain
        self.assets = Path(assets_dir)
        self.logo_white = self.assets / "logo-mkg-blanc.png"
        blue = self.assets / "logo-mkg-new-rvb.png"
        self.logo_blue = blue if blue.exists() else self.assets / "logo-mkg-bleu.png"
        self._tex_path = self.assets / "bg-texture.jpg"
        self._tex_cache = None

    # ---- unites ----
    def px(self, v: float) -> int:
        return int(round(v * self.s))

    def _f(self, weight, size_px):
        return get_font(charte.PILLOW_WEIGHT.get(weight, "regular"), self.px(size_px))

    # ---- primitives de fond ----
    def _base(self, hex_str):
        return Image.new("RGBA", (self.W, self.H), _c(hex_str))

    def _tex(self):
        if self._tex_cache is None and self._tex_path.exists():
            self._tex_cache = Image.open(self._tex_path).convert("RGB")
        return self._tex_cache

    def texture_panel(self, w_px, h_px, hex_color, opacity=0.10):
        """Panneau plein (couleur unie) + texture grain a faible opacite (RGB)."""
        w_px, h_px = max(1, int(w_px)), max(1, int(h_px))
        img = Image.new("RGB", (w_px, h_px), charte.rgb_tuple(hex_color))
        tex = self._tex()
        if tex is not None and opacity > 0:
            screened = ImageChops.screen(img, tex.resize((w_px, h_px)))
            img = Image.blend(img, screened, opacity)
        return img

    def _texture(self, img, box, opacity):
        tex = self._tex()
        if tex is None or opacity <= 0:
            return
        x0, y0, x1, y1 = [int(v) for v in box]
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            return
        region = img.crop((x0, y0, x1, y1)).convert("RGB")
        screened = ImageChops.screen(region, tex.resize((w, h)))
        blended = Image.blend(region, screened, opacity)
        img.paste(blended, (x0, y0))

    def _grain(self, img, opacity=0.05):
        if not self.grain or opacity <= 0:
            return
        import random
        rnd = random.Random(7)
        small = Image.new("L", (self.W // 6, self.H // 6))
        small.putdata([rnd.randint(0, 255) for _ in range(small.width * small.height)])
        noise = small.resize((self.W, self.H))
        overlay = Image.new("RGBA", (self.W, self.H), (255, 255, 255, 0))
        overlay.putalpha(noise.point(lambda v: int(v * opacity)))
        img.alpha_composite(overlay)

    def _diag_fill(self, img, angle_deg, stop, color_hex, alpha=255):
        """Peint la moitie << avant >> (a*x+b*y>=c) d'un gradient CSS lineaire."""
        rad = math.radians(angle_deg)
        dx, dy = math.sin(rad), -math.cos(rad)
        corners = [(0, 0), (self.W, 0), (self.W, self.H), (0, self.H)]
        projs = [dx * x + dy * y for x, y in corners]
        pmin, pmax = min(projs), max(projs)
        c = pmin + stop * (pmax - pmin)
        poly = _clip_halfplane(corners, dx, dy, c)
        if len(poly) >= 3:
            ImageDraw.Draw(img, "RGBA").polygon(poly, fill=_c(color_hex, alpha))

    def _gradient_rect(self, box, angle_deg, stops):
        """Rectangle a gradient lineaire. stops: [(pos 0-1, hex), ...]."""
        x0, y0, x1, y1 = [int(v) for v in box]
        w, h = x1 - x0, y1 - y0
        L = max(2, int(math.hypot(w, h)))
        line = Image.new("RGB", (L, 1))
        cols = [(p, charte.rgb_tuple(c)) for p, c in stops]
        px = line.load()
        for i in range(L):
            t = i / (L - 1)
            for j in range(len(cols) - 1):
                p0, c0 = cols[j]
                p1, c1 = cols[j + 1]
                if t <= p1 or j == len(cols) - 2:
                    k = 0 if p1 == p0 else max(0.0, min(1.0, (t - p0) / (p1 - p0)))
                    px[i, 0] = tuple(int(round(c0[m] + (c1[m] - c0[m]) * k)) for m in range(3))
                    break
        grad = line.resize((L, L)).rotate(90 - angle_deg, resample=Image.BICUBIC, expand=True)
        gw, gh = grad.size
        grad = grad.crop(((gw - w) // 2, (gh - h) // 2, (gw - w) // 2 + w, (gh - h) // 2 + h))
        return grad.convert("RGBA")

    # ---- texte ----
    def _text(self, draw, xy, text, font, fill, anchor="la"):
        draw.text(xy, sanitize.clean(text), font=font, fill=fill, anchor=anchor)

    def _tracked(self, draw, xy, text, font, fill, em, size_px, align="l", anchor_y="a"):
        text = sanitize.clean(text).upper()
        track = em * self.px(size_px)
        widths = [font.getlength(ch) + track for ch in text]
        total = sum(widths) - (track if widths else 0)
        x, y = xy
        if align == "m":
            x -= total / 2
        elif align == "r":
            x -= total
        for ch, w in zip(text, widths):
            draw.text((x, y), ch, font=font, fill=fill, anchor="l" + anchor_y)
            x += w

    def _wrap(self, text, font, max_px):
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

    def _logo_size(self, path, height_px):
        if not Path(path).exists():
            return 0, 0
        logo = Image.open(path)
        h = self.px(height_px)
        return round(logo.width * h / logo.height), h

    def _paste_logo(self, img, path, x, y, height_px, align_right=False):
        if not Path(path).exists():
            return 0
        logo = Image.open(path).convert("RGBA")
        ratio = self.px(height_px) / logo.height
        logo = logo.resize((round(logo.width * ratio), self.px(height_px)))
        if align_right:
            x -= logo.width
        img.alpha_composite(logo, (round(x), round(y)))
        return logo.width

    # ---- formes translucides (compositees correctement) ----
    def _fill_rect(self, img, box, hex_str=None, alpha=255, radius=0,
                   outline=None, ow=0, oalpha=255):
        x0, y0, x1, y1 = [int(round(v)) for v in box]
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            return
        ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        dd = ImageDraw.Draw(ov)
        shape = [0, 0, w - 1, h - 1]
        fill = _c(hex_str, alpha) if hex_str else None
        ol = _c(outline, oalpha) if outline else None
        if radius:
            dd.rounded_rectangle(shape, radius=radius, fill=fill, outline=ol, width=ow)
        else:
            dd.rectangle(shape, fill=fill, outline=ol, width=ow)
        img.alpha_composite(ov, (x0, y0))

    def _fill_ellipse(self, img, box, hex_str=None, alpha=255, outline=None, ow=0, oalpha=255):
        x0, y0, x1, y1 = [int(round(v)) for v in box]
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            return
        ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        dd = ImageDraw.Draw(ov)
        dd.ellipse([0, 0, w - 1, h - 1], fill=_c(hex_str, alpha) if hex_str else None,
                   outline=_c(outline, oalpha) if outline else None, width=ow)
        img.alpha_composite(ov, (x0, y0))

    def _hline(self, img, x0, y, x1, hex_str, alpha, width):
        self._fill_rect(img, (x0, y, x1, y + width), hex_str, alpha)

    # ================================================================
    # SLIDES BRAND
    # ================================================================
    def cover(self, *, title, eyebrow="", subtitle="", meta=None,
              kpis=None, footer_note="", logo_height=40):
        img = self._base(charte.DARK)
        split = self.px(806)  # 42 %
        # panneau droit : gradient electrique -> bleu -> dark + texture + forme
        grad = self._gradient_rect((split, 0, self.W, self.H), 135,
                                    [(0.0, charte.ELECTRIC), (0.6, charte.BLUE), (1.0, charte.DARK)])
        img.paste(grad, (split, 0))
        ov = Image.new("RGBA", (self.W - split, self.H), _c(charte.DARK, 38))
        img.alpha_composite(ov, (split, 0))
        self._texture(img, (split, 0, self.W, self.H), 0.22)
        # liseré sombre en biais sur le bord gauche du panneau
        ImageDraw.Draw(img, "RGBA").polygon(
            [(split, 0), (split + self.px(120), 0), (split, self.H), (split - self.px(2), self.H)],
            fill=_c(charte.DARK))
        self._grain(img, 0.05)
        d = ImageDraw.Draw(img, "RGBA")

        px = self.px(64)
        # eyebrow haut
        self._tracked(d, (px, self.px(80)), eyebrow, self._f("semibold", 18),
                      _c(charte.ELECTRIC), 0.14, 18)
        # bloc central gauche
        col_w = split - px - self.px(40)
        ft = self._f("bold", 72)
        lines = self._wrap(title, ft, col_w)
        th = len(lines) * self.px(72 * 1.05) + (self.px(24) + self.px(34) if subtitle else 0)
        ty = (self.H - th) // 2
        for ln in lines:
            self._text(d, (px, ty), ln, ft, _c(charte.WHITE))
            ty += self.px(72 * 1.05)
        if subtitle:
            ty += self.px(24)
            for ln in self._wrap(subtitle, self._f("light", 22), self.px(560)):
                self._text(d, (px, ty), ln, self._f("light", 22), _c(charte.WHITE, 165))
                ty += self.px(22 * 1.5)
        # separateur + meta
        if meta:
            ty += self.px(32)
            self._hline(img, px, ty, px + col_w, charte.WHITE, 38, self.px(2))
            ty += self.px(32)
            fk = self._f("semibold", 11)
            fv = self._f("regular", 16)
            cols2 = 2
            cw = col_w // cols2
            for i, (k, v) in enumerate(meta):
                cx = px + (i % cols2) * cw
                ry = ty + (i // cols2) * self.px(58)
                self._tracked(d, (cx, ry), k, fk, _c(charte.WHITE, 90), 0.12, 11)
                self._text(d, (cx, ry + self.px(18)), v, fv, _c(charte.WHITE, 205))
        # footer : logo + note
        fy = self.H - self.px(80) - self.px(logo_height)
        self._paste_logo(img, self.logo_white, px, fy, logo_height)
        if footer_note:
            self._tracked(d, (split - self.px(40), fy + self.px(logo_height - 12)),
                          footer_note, self._f("regular", 11), _c(charte.WHITE, 64), 0.08, 11,
                          align="r")
        # KPI grid (panneau droit)
        if kpis:
            self._cover_kpis(img, split, kpis)
        return img

    def _cover_kpis(self, img, split, kpis):
        d = ImageDraw.Draw(img, "RGBA")
        kpis = kpis[:3]
        pad = self.px(80)
        gx0 = split + pad
        gx1 = self.W - pad
        gw = gx1 - gx0
        cell_w = gw // len(kpis)
        ch = self.px(150)
        cy0 = (self.H - ch) // 2
        for i, k in enumerate(kpis):
            x0 = gx0 + i * cell_w
            self._fill_rect(img, (x0, cy0, x0 + cell_w - self.px(2), cy0 + ch),
                            charte.WHITE, 20, outline=charte.WHITE, ow=self.px(1), oalpha=28)
            cx = x0 + cell_w // 2
            self._text(d, (cx, cy0 + self.px(46)), k.get("value", ""),
                       self._f("bold", 48), _c(charte.WHITE), anchor="mm")
            self._tracked(d, (cx, cy0 + self.px(104)), k.get("label", ""),
                          self._f("regular", 13), _c(charte.WHITE, 128), 0.08, 13)

    def section_bg(self):
        """Fond SEUL de l'intercalaire (sans aucun texte) : panneau electrique +
        texture + diagonale sombre + grain. Le texte (numero, eyebrow, titre,
        description, sommaire) est pose en natif/editable par le builder."""
        img = self._base(charte.DARK)
        split = self.px(806)
        img.paste(self._base(charte.ELECTRIC).crop((0, 0, self.W - split, self.H)), (split, 0))
        self._texture(img, (split, 0, self.W, self.H), 0.14)
        ImageDraw.Draw(img, "RGBA").polygon(
            [(split, 0), (split + self.px(90), 0), (split, self.H)], fill=_c(charte.DARK))
        self._grain(img, 0.05)
        return img

    def section(self, *, number, title, eyebrow="", desc="", toc=None):
        img = self._base(charte.DARK)
        split = self.px(806)
        img.paste(self._base(charte.ELECTRIC).crop((0, 0, self.W - split, self.H)), (split, 0))
        self._texture(img, (split, 0, self.W, self.H), 0.14)
        ImageDraw.Draw(img, "RGBA").polygon(
            [(split, 0), (split + self.px(90), 0), (split, self.H)], fill=_c(charte.DARK))
        self._grain(img, 0.05)
        d = ImageDraw.Draw(img, "RGBA")
        px = self.px(72)
        # numero geant faiblement visible
        self._text(d, (px - self.px(8), self.px(300)), str(number),
                   self._f("black", 200), _c(charte.WHITE, 12))
        cy = int(self.H * 0.40)
        self._tracked(d, (px, cy), eyebrow, self._f("semibold", 14),
                      _c(charte.WHITE, 90), 0.16, 14)
        self._text(d, (px, cy + self.px(28)), title, self._f("bold", 72), _c(charte.WHITE))
        if desc:
            ty = cy + self.px(28 + 92)
            for ln in self._wrap(desc, self._f("light", 21), self.px(540)):
                self._text(d, (px, ty), ln, self._f("light", 21), _c(charte.WHITE, 150))
                ty += self.px(21 * 1.6)
        # toc a droite
        if toc:
            ix = split + self.px(70)
            iy = int(self.H * 0.40)
            for i, item in enumerate(toc):
                active = isinstance(item, dict) and item.get("active")
                label = item.get("label") if isinstance(item, dict) else str(item)
                col = _c(charte.WHITE) if active else _c(charte.WHITE, 115)
                r = self.px(19)
                ncx, ncy = ix + r, iy + r
                if active:
                    self._fill_ellipse(img, (ix, iy, ix + 2 * r, iy + 2 * r), charte.WHITE)
                    self._text(d, (ncx, ncy), str(i + 1), self._f("semibold", 15),
                               _c(charte.ELECTRIC), anchor="mm")
                else:
                    self._fill_ellipse(img, (ix, iy, ix + 2 * r, iy + 2 * r),
                                       outline=charte.WHITE, ow=self.px(2), oalpha=77)
                    self._text(d, (ncx, ncy), str(i + 1), self._f("regular", 15), col, anchor="mm")
                self._text(d, (ix + 2 * r + self.px(16), ncy),
                           label, self._f("semibold" if active else "regular", 21),
                           col, anchor="lm")
                iy += self.px(60)
        return img

    def stat(self, *, number, unit="", eyebrow="", desc="", source="", dark=False):
        img = self._base(charte.DARK if dark else charte.BLUE)
        self._texture(img, (0, 0, self.W, self.H), 0.08)
        self._grain(img, 0.04)
        d = ImageDraw.Draw(img, "RGBA")
        cx = self.W // 2
        self._tracked(d, (cx, int(self.H * 0.22)), eyebrow, self._f("semibold", 20),
                      _c(charte.WHITE, 140), 0.14, 20, align="m", anchor_y="m")
        # numero geant centre, avec unite plus petite
        fnum = self._f("bold", 280)
        funit = self._f("light", 120)
        num = sanitize.clean(str(number))
        wnum = d.textlength(num, font=fnum)
        wunit = d.textlength(" " + unit, font=funit) if unit else 0
        total = wnum + wunit
        ny = int(self.H * 0.50)
        x0 = cx - total / 2
        self._text(d, (x0, ny), num, fnum, _c(charte.WHITE), anchor="lm")
        if unit:
            self._text(d, (x0 + wnum, ny + self.px(40)), " " + unit, funit,
                       _c(charte.WHITE), anchor="lm")
        if desc:
            ty = int(self.H * 0.50) + self.px(170)
            for ln in self._wrap(desc, self._f("light", 28), self.px(1100)):
                self._text(d, (cx, ty), ln, self._f("light", 28), _c(charte.WHITE, 184),
                           anchor="ma")
                ty += self.px(28 * 1.5)
        if source:
            self._text(d, (cx, self.H - self.px(70)), source, self._f("regular", 15),
                       _c(charte.WHITE, 102), anchor="ma")
        return img

    def quote(self, *, text, author=""):
        img = self._base(charte.BLUE)
        self._texture(img, (0, 0, self.W, self.H), 0.08)
        self._grain(img, 0.04)
        d = ImageDraw.Draw(img, "RGBA")
        cx = self.W // 2
        self._text(d, (self.px(176), self.px(220)), "\u201C", self._f("black", 200),
                   _c(charte.WHITE, 20))
        lines = self._wrap(text, self._f("light", 52), self.px(1300))
        th = len(lines) * self.px(52 * 1.35)
        ty = (self.H - th) // 2
        for ln in lines:
            self._text(d, (cx, ty), ln, self._f("light", 52), _c(charte.WHITE), anchor="ma")
            ty += self.px(52 * 1.35)
        if author:
            ty += self.px(48)
            self._hline(img, cx - self.px(40), ty, cx + self.px(40), charte.WHITE, 51, self.px(2))
            self._tracked(d, (cx, ty + self.px(24)), author, self._f("semibold", 20),
                          _c(charte.WHITE, 128), 0.06, 20, align="m", anchor_y="a")
        return img

    def merci(self, *, title="Merci", subtitle="", contact="", logo_height=52):
        img = self._base(charte.DARK)
        self._texture(img, (0, 0, self.W, self.H), 0.12)
        self._grain(img, 0.05)
        d = ImageDraw.Draw(img, "RGBA")
        cx = self.W // 2
        cy = int(self.H * 0.38)
        self._text(d, (cx, cy), title, self._f("bold", 160), _c(charte.WHITE), anchor="mm")
        ty = cy + self.px(110)
        if subtitle:
            for ln in self._wrap(subtitle, self._f("light", 26), self.px(900)):
                self._text(d, (cx, ty), ln, self._f("light", 26), _c(charte.WHITE, 158),
                           anchor="ma")
                ty += self.px(26 * 1.5)
        lw, _ = self._logo_size(self.logo_white, logo_height)
        self._paste_logo(img, self.logo_white, cx - lw / 2, ty + self.px(40), logo_height)
        if contact:
            self._tracked(d, (cx, ty + self.px(40 + logo_height + 28)), contact,
                          self._f("regular", 18), _c(charte.WHITE, 115), 0.04, 18, align="m")
        return img

    def closing(self, *, title, eyebrow="", subtitle="", contacts=None, logo_height=44):
        img = self._base(charte.DARK)
        split = self.px(1114)  # 58 %
        img.paste(self._base(charte.ELECTRIC).crop((0, 0, self.W - split, self.H)), (split, 0))
        self._texture(img, (split, 0, self.W, self.H), 0.12)
        self._grain(img, 0.05)
        d = ImageDraw.Draw(img, "RGBA")
        px = self.px(72)
        self._tracked(d, (px, self.px(80)), eyebrow, self._f("semibold", 17),
                      _c(charte.ELECTRIC), 0.14, 17)
        title_lines = self._wrap(title, self._f("bold", 64), split - px - self.px(60))
        line_h = self.px(64 * 1.1)
        cy = int(self.H * 0.42) - max(0, len(title_lines) - 2) * line_h // 2
        for i, ln in enumerate(title_lines):
            self._text(d, (px, cy + i * line_h), ln, self._f("bold", 64), _c(charte.WHITE))
        if subtitle:
            sy = cy + len(title_lines) * line_h + self.px(28)
            for ln in self._wrap(subtitle, self._f("light", 22), split - px - self.px(60)):
                self._text(d, (px, sy), ln, self._f("light", 22), _c(charte.WHITE, 158))
                sy += self.px(22 * 1.55)
        self._paste_logo(img, self.logo_white, px, self.H - self.px(80) - self.px(logo_height),
                         logo_height)
        # contacts (panneau electrique)
        if contacts:
            ix = split + self.px(56)
            iy = int(self.H * 0.30)
            for j, ct in enumerate(contacts):
                if j > 0:
                    self._hline(img, ix, iy - self.px(18), self.W - self.px(56),
                                charte.WHITE, 46, self.px(2))
                self._tracked(d, (ix, iy), ct.get("label", ""), self._f("semibold", 14),
                              _c(charte.WHITE, 140), 0.12, 14)
                self._text(d, (ix, iy + self.px(22)), ct.get("name", ""),
                           self._f("semibold", 28), _c(charte.WHITE))
                ny = iy + self.px(22 + 40)
                if ct.get("role"):
                    self._text(d, (ix, ny), ct["role"], self._f("regular", 17),
                               _c(charte.WHITE, 184))
                    ny += self.px(28)
                for ln in ct.get("lines", []):
                    self._text(d, (ix, ny), ln, self._f("regular", 18), _c(charte.WHITE))
                    ny += self.px(30)
                iy = ny + self.px(48)
        return img
