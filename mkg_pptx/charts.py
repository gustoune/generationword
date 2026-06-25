"""Rendu Pillow des graphiques de la charte MKG (courbe temporelle).

python-pptx ne sait pas dessiner de courbes ; on rasterise donc le trace
(zone de plot + grille + axes + points) en une image nette (supersampling puis
reduction LANCZOS) inseree comme picture dans le corps de la slide. La legende
est rendue nativement par le bloc appelant pour rester editable.
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from . import charte, sanitize
from .fonts import get_font


def _c(hex_str, alpha=255):
    r, g, b = charte.rgb_tuple(hex_str)
    return (r, g, b, alpha)


def _dashed(d, p0, p1, col, w, dash=18, gap=12):
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    length = (dx * dx + dy * dy) ** 0.5
    if length <= 0:
        return
    ux, uy = dx / length, dy / length
    pos = 0.0
    while pos < length:
        a = min(pos + dash, length)
        d.line([(x0 + ux * pos, y0 + uy * pos), (x0 + ux * a, y0 + uy * a)],
               fill=col, width=w)
        pos += dash + gap


def linechart(width_px, height_px, *, series, xlabels, ymin=None, ymax=None,
              yticks=5, yfmt="{:.0f}", scale=3):
    """Trace une courbe multi-series. Renvoie une image RGBA (px*scale)."""
    s = scale
    W, H = int(width_px * s), int(height_px * s)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    pad_l, pad_r, pad_t, pad_b = int(78 * s), int(24 * s), int(22 * s), int(48 * s)
    px0, py0 = pad_l, pad_t
    px1, py1 = W - pad_r, H - pad_b
    pw, ph = px1 - px0, py1 - py0

    flat = [v for srv in series for v in srv.get("values", []) if v is not None]
    if not flat:
        return img
    lo = ymin if ymin is not None else min(flat)
    hi = ymax if ymax is not None else max(flat)
    if hi <= lo:
        hi = lo + 1
    # arrondi doux des bornes
    span = hi - lo
    lo = lo - span * 0.08
    hi = hi + span * 0.10

    def X(i, n):
        return px0 + (pw * i / (n - 1) if n > 1 else pw / 2)

    def Y(v):
        return py1 - (v - lo) / (hi - lo) * ph

    f_axis = get_font("regular", int(15 * s))
    grid_col = _c(charte.LINE_LIGHT, 255)
    lbl_col = _c(charte.INK_FAINT, 255)

    for k in range(yticks + 1):
        v = lo + (hi - lo) * k / yticks
        gy = Y(v)
        d.line([(px0, gy), (px1, gy)], fill=grid_col, width=max(1, int(s)))
        txt = sanitize.clean(yfmt.format(v))
        tb = d.textbbox((0, 0), txt, font=f_axis)
        d.text((px0 - int(14 * s) - (tb[2] - tb[0]), gy - (tb[3] - tb[1]) / 2 - tb[1]),
               txt, font=f_axis, fill=lbl_col)

    n = max(len(xlabels), max((len(sv.get("values", [])) for sv in series), default=0))
    for i, xl in enumerate(xlabels):
        gx = X(i, n)
        txt = sanitize.clean(str(xl))
        tb = d.textbbox((0, 0), txt, font=f_axis)
        d.text((gx - (tb[2] - tb[0]) / 2, py1 + int(16 * s)), txt, font=f_axis, fill=lbl_col)

    palette = [charte.BLUE, charte.ELECTRIC, charte.GRAY]
    lw = max(2, int(3.5 * s))
    for si, sv in enumerate(series):
        col = _c(sv.get("color") or palette[si % len(palette)])
        vals = sv.get("values", [])
        pts = [(X(i, n), Y(v)) for i, v in enumerate(vals) if v is not None]
        if len(pts) >= 2:
            if sv.get("dashed"):
                for a, b in zip(pts, pts[1:]):
                    _dashed(d, a, b, col, lw, dash=int(16 * s), gap=int(11 * s))
            else:
                d.line(pts, fill=col, width=lw, joint="curve")
        rdot = int(5.5 * s)
        rin = int(2.6 * s)
        for (cx, cy) in pts:
            d.ellipse([cx - rdot, cy - rdot, cx + rdot, cy + rdot], fill=col)
            d.ellipse([cx - rin, cy - rin, cx + rin, cy + rin], fill=_c(charte.WHITE))

    return img
