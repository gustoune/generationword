"""Pictogrammes line-art (style feather) rendus en PNG pour les slides natives.

python-pptx ne sait pas embarquer de SVG ; on rasterise donc chaque icone a
haute resolution (trace sur un canevas 1024 px puis reduction LANCZOS pour un
anti-aliasing propre) et on la place comme image dans les cartes.

Les traces suivent le viewBox 24x24 des icones feather. Les chemins sont des
approximations volontairement simples : l'objectif est une lecture claire du
symbole, pas une copie pixel a pixel.
"""
from __future__ import annotations

from PIL import Image, ImageDraw

_BIG = 1024  # canevas interne avant reduction


def _rgb(hex_str):
    return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), 255)


def _scaler():
    def P(x, y):
        return (x / 24.0 * _BIG, y / 24.0 * _BIG)
    return P


def _stroke(d, P, pts, col, w, closed=False):
    """Polyligne avec jointures/extremites arrondies."""
    seq = [P(x, y) for x, y in pts]
    if closed:
        seq = seq + [seq[0]]
    if len(seq) >= 2:
        d.line(seq, fill=col, width=w, joint="curve")
    r = w / 2.0
    for x, y in seq:
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)


def _ring(d, P, col, w, cx, cy, r, fill=None):
    x0, y0 = P(cx - r, cy - r)
    x1, y1 = P(cx + r, cy + r)
    if fill is not None:
        d.ellipse([x0, y0, x1, y1], fill=col)
    else:
        d.ellipse([x0, y0, x1, y1], outline=col, width=w)


def _arc(d, P, col, w, cx, cy, r, start, end):
    x0, y0 = P(cx - r, cy - r)
    x1, y1 = P(cx + r, cy + r)
    d.arc([x0, y0, x1, y1], start, end, fill=col, width=w)


# ------------------------------------------------------------------
# Definitions d'icones (chacune : d, P, col, w)
# ------------------------------------------------------------------
def _i_circle(d, P, c, w):
    _ring(d, P, c, w, 12, 12, 9)


def _i_eye(d, P, c, w):
    _ring(d, P, c, w, 12, 12, 0)  # noop guard
    x0, y0 = P(1.5, 6); x1, y1 = P(22.5, 18)
    d.ellipse([x0, y0, x1, y1], outline=c, width=w)
    _ring(d, P, c, w, 12, 12, 3)


def _i_bars(d, P, c, w):
    _stroke(d, P, [(6, 20), (6, 13.5)], c, w)
    _stroke(d, P, [(12, 20), (12, 4)], c, w)
    _stroke(d, P, [(18, 20), (18, 9.5)], c, w)


def _i_activity(d, P, c, w):
    _stroke(d, P, [(2, 12), (6, 12), (9, 3), (15, 21), (18, 12), (22, 12)], c, w)


def _i_trending_up(d, P, c, w):
    _stroke(d, P, [(1, 18), (8.5, 10.5), (13.5, 15.5), (23, 6)], c, w)
    _stroke(d, P, [(17, 6), (23, 6), (23, 12)], c, w)


def _i_star(d, P, c, w):
    _stroke(d, P, [(12, 2), (15.09, 8.26), (22, 9.27), (17, 14.14),
                   (18.18, 21.02), (12, 17.77), (5.82, 21.02), (7, 14.14),
                   (2, 9.27), (8.91, 8.26)], c, w, closed=True)


def _i_globe(d, P, c, w):
    _ring(d, P, c, w, 12, 12, 10)
    x0, y0 = P(7.5, 2); x1, y1 = P(16.5, 22)
    d.ellipse([x0, y0, x1, y1], outline=c, width=w)
    _stroke(d, P, [(2, 12), (22, 12)], c, w)


def _i_search(d, P, c, w):
    _ring(d, P, c, w, 11, 11, 8)
    _stroke(d, P, [(16.5, 16.5), (21, 21)], c, w)


def _i_grid(d, P, c, w):
    _stroke(d, P, [(3, 3), (21, 3), (21, 21), (3, 21)], c, w, closed=True)
    _stroke(d, P, [(3, 9), (21, 9)], c, w)
    _stroke(d, P, [(3, 15), (21, 15)], c, w)
    _stroke(d, P, [(9, 3), (9, 21)], c, w)


def _i_map_pin(d, P, c, w):
    _ring(d, P, c, w, 12, 9, 6)
    _stroke(d, P, [(7.1, 12.7), (12, 22), (16.9, 12.7)], c, w)
    _ring(d, P, c, w, 12, 9, 2.4)


def _i_dollar(d, P, c, w):
    _stroke(d, P, [(12, 1.5), (12, 22.5)], c, w)
    _stroke(d, P, [(16.5, 6), (9.5, 6), (8, 9), (9.5, 12), (14.5, 12),
                   (16, 15), (14.5, 18), (6.5, 18)], c, w)


def _i_home(d, P, c, w):
    _stroke(d, P, [(3, 10.5), (12, 3), (21, 10.5)], c, w)
    _stroke(d, P, [(5, 9.5), (5, 21), (19, 21), (19, 9.5)], c, w)
    _stroke(d, P, [(10, 21), (10, 15), (14, 15), (14, 21)], c, w)


def _i_building(d, P, c, w):
    _stroke(d, P, [(4, 2), (20, 2), (20, 22), (4, 22)], c, w, closed=True)
    for yy in (6, 10, 14):
        _stroke(d, P, [(8, yy), (10, yy)], c, w)
        _stroke(d, P, [(14, yy), (16, yy)], c, w)
    _stroke(d, P, [(10, 22), (10, 18), (14, 18), (14, 22)], c, w)


def _i_target(d, P, c, w):
    _ring(d, P, c, w, 12, 12, 10)
    _ring(d, P, c, w, 12, 12, 6)
    _ring(d, P, c, w, 12, 12, 2, fill=True)


def _i_layers(d, P, c, w):
    _stroke(d, P, [(12, 2), (22, 8.5), (12, 15), (2, 8.5)], c, w, closed=True)
    _stroke(d, P, [(2, 12.5), (12, 19), (22, 12.5)], c, w)
    _stroke(d, P, [(2, 16.5), (12, 23), (22, 16.5)], c, w)


def _i_check(d, P, c, w):
    _stroke(d, P, [(4, 12.5), (9, 17.5), (20, 6.5)], c, w)


def _i_check_circle(d, P, c, w):
    _ring(d, P, c, w, 12, 12, 10)
    _stroke(d, P, [(7.5, 12), (11, 15.5), (16.5, 8.5)], c, w)


def _i_credit_card(d, P, c, w):
    _stroke(d, P, [(1.5, 4.5), (22.5, 4.5), (22.5, 19.5), (1.5, 19.5)], c, w, closed=True)
    _stroke(d, P, [(1.5, 9.5), (22.5, 9.5)], c, w)


def _i_calendar(d, P, c, w):
    _stroke(d, P, [(3.5, 5), (20.5, 5), (20.5, 21), (3.5, 21)], c, w, closed=True)
    _stroke(d, P, [(8, 3), (8, 7)], c, w)
    _stroke(d, P, [(16, 3), (16, 7)], c, w)
    _stroke(d, P, [(3.5, 10), (20.5, 10)], c, w)
    _stroke(d, P, [(9, 15.5), (11, 17.5), (15, 13.5)], c, w)


def _i_users(d, P, c, w):
    _ring(d, P, c, w, 9, 8, 4)
    _stroke(d, P, [(2, 21), (2, 18), (4.5, 15.5), (13.5, 15.5), (16, 18), (16, 21)], c, w)
    _arc(d, P, c, w, 17.5, 8.5, 3.4, 270, 110)
    _stroke(d, P, [(18.5, 15.7), (20, 16.6), (21.5, 18.5), (21.5, 21)], c, w)


def _i_compass(d, P, c, w):
    _ring(d, P, c, w, 12, 12, 10)
    _stroke(d, P, [(16.2, 7.8), (10, 10), (7.8, 16.2), (14, 14)], c, w, closed=True)


def _i_briefcase(d, P, c, w):
    _stroke(d, P, [(2.5, 7), (21.5, 7), (21.5, 21), (2.5, 21)], c, w, closed=True)
    _stroke(d, P, [(8.5, 7), (8.5, 5), (15.5, 5), (15.5, 7)], c, w)
    _stroke(d, P, [(2.5, 12.5), (21.5, 12.5)], c, w)


def _i_zap(d, P, c, w):
    _stroke(d, P, [(13, 2), (3, 14), (12, 14), (11, 22), (21, 10), (12, 10)], c, w, closed=True)


def _i_pie(d, P, c, w):
    _ring(d, P, c, w, 12, 12, 9)
    _stroke(d, P, [(12, 12), (12, 3)], c, w)
    _stroke(d, P, [(12, 12), (20, 15.5)], c, w)


def _i_droplet(d, P, c, w):
    _stroke(d, P, [(12, 2.7), (6.5, 11)], c, w)
    _arc(d, P, c, w, 12, 13.5, 6.2, 30, 330)
    _stroke(d, P, [(17.5, 11), (12, 2.7)], c, w)


def _i_merge(d, P, c, w):
    _stroke(d, P, [(12, 4), (12, 20)], c, w)
    _stroke(d, P, [(4.5, 11.5), (12, 11.5)], c, w)
    _stroke(d, P, [(19.5, 11.5), (12, 11.5)], c, w)


def _i_sliders(d, P, c, w):
    _stroke(d, P, [(4, 21), (4, 14)], c, w)
    _stroke(d, P, [(4, 10), (4, 3)], c, w)
    _stroke(d, P, [(12, 21), (12, 12)], c, w)
    _stroke(d, P, [(12, 8), (12, 3)], c, w)
    _stroke(d, P, [(20, 21), (20, 16)], c, w)
    _stroke(d, P, [(20, 12), (20, 3)], c, w)
    _ring(d, P, c, w, 4, 12, 1.6, fill=True)
    _ring(d, P, c, w, 12, 10, 1.6, fill=True)
    _ring(d, P, c, w, 20, 14, 1.6, fill=True)


def _i_award(d, P, c, w):
    _ring(d, P, c, w, 12, 9, 6)
    _stroke(d, P, [(8.5, 14), (7, 22), (12, 19), (17, 22), (15.5, 14)], c, w)


def _i_phone(d, P, c, w):
    _stroke(d, P, [(7, 2), (5.5, 2), (4, 3.5), (4, 7), (8, 14), (15, 19),
                   (18, 19), (20, 17.5), (20, 16), (16.5, 14.5), (15, 16),
                   (11, 13.5), (8.5, 9), (10, 7.5), (8.5, 4)], c, w, closed=True)


def _i_book(d, P, c, w):
    _stroke(d, P, [(4, 4), (4, 20), (12, 18), (20, 20), (20, 4), (12, 6), (4, 4)], c, w, closed=True)
    _stroke(d, P, [(12, 6), (12, 18)], c, w)


def _i_flag(d, P, c, w):
    _stroke(d, P, [(5, 21), (5, 3)], c, w)
    _stroke(d, P, [(5, 4), (19, 4), (15, 9), (19, 14), (5, 14)], c, w, closed=True)


def _i_shield(d, P, c, w):
    _stroke(d, P, [(12, 2.5), (20, 5.5), (20, 11), (12, 21.5), (4, 11), (4, 5.5)], c, w, closed=True)
    _stroke(d, P, [(8.5, 11.5), (11, 14), (15.5, 8.5)], c, w)


def _i_clock(d, P, c, w):
    _ring(d, P, c, w, 12, 12, 9.5)
    _stroke(d, P, [(12, 7), (12, 12), (16, 14)], c, w)


def _i_image(d, P, c, w):
    x0, y0 = P(3, 4)
    x1, y1 = P(21, 20)
    d.rounded_rectangle([x0, y0, x1, y1], radius=(x1 - x0) * 0.10, outline=c, width=w)
    _ring(d, P, c, w, 8.5, 9, 1.6)
    _stroke(d, P, [(4, 18), (10, 12), (14, 16), (17, 13), (20, 16)], c, w)


def _i_minus(d, P, c, w):
    _stroke(d, P, [(5, 12), (19, 12)], c, w)


def _i_arrow_right(d, P, c, w):
    _stroke(d, P, [(4, 12), (20, 12)], c, w)
    _stroke(d, P, [(13, 5), (20, 12), (13, 19)], c, w)


def _i_refresh(d, P, c, w):
    _arc(d, P, c, w, 12, 12, 8.5, 300, 200)
    _stroke(d, P, [(4.5, 8), (3.5, 4), (7.5, 4.5)], c, w)
    _arc(d, P, c, w, 12, 12, 8.5, 120, 20)
    _stroke(d, P, [(19.5, 16), (20.5, 20), (16.5, 19.5)], c, w)


_ICONS = {
    "circle": _i_circle, "eye": _i_eye, "bars": _i_bars, "bar-chart": _i_bars,
    "activity": _i_activity, "pulse": _i_activity, "trending-up": _i_trending_up,
    "star": _i_star, "globe": _i_globe, "search": _i_search, "grid": _i_grid,
    "map-pin": _i_map_pin, "location": _i_map_pin, "dollar": _i_dollar,
    "euro": _i_dollar, "money": _i_dollar, "home": _i_home, "building": _i_building,
    "bank": _i_building, "target": _i_target, "layers": _i_layers, "check": _i_check,
    "check-circle": _i_check_circle, "credit-card": _i_credit_card, "card": _i_credit_card,
    "calendar": _i_calendar, "calendar-check": _i_calendar, "event": _i_calendar,
    "users": _i_users, "people": _i_users, "compass": _i_compass, "briefcase": _i_briefcase,
    "zap": _i_zap, "lightning": _i_zap, "pie": _i_pie, "pie-chart": _i_pie,
    "droplet": _i_droplet, "drop": _i_droplet, "merge": _i_merge, "git-merge": _i_merge,
    "cross": _i_merge, "sliders": _i_sliders, "controls": _i_sliders, "award": _i_award,
    "phone": _i_phone, "book": _i_book, "flag": _i_flag, "shield": _i_shield,
    "scale": _i_shield, "clock": _i_clock, "time": _i_clock, "refresh": _i_refresh,
    "cycle": _i_refresh, "minus": _i_minus, "arrow-right": _i_arrow_right,
    "arrow": _i_arrow_right, "image": _i_image, "photo": _i_image, "camera": _i_image,
}


def available():
    return sorted(_ICONS.keys())


def render(name, stroke_hex, width=2.0):
    """Rend l'icone `name` en RGBA (1024 px), trait `stroke_hex`."""
    img = Image.new("RGBA", (_BIG, _BIG), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = _rgb(stroke_hex)
    w = max(2, int(round(width / 24.0 * _BIG)))
    P = _scaler()
    fn = _ICONS.get((name or "").strip().lower(), _i_circle)
    try:
        fn(d, P, col, w)
    except Exception:
        _i_circle(d, P, col, w)
    return img
