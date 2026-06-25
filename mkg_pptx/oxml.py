"""Helpers bas niveau pour les slides natives python-pptx.

Couvre ce que l'API n'expose pas directement : transparence d'une couleur
(texte / fond), letter-spacing (tracking) des runs, rayon des coins arrondis,
et reglages fins des cadres de texte.
"""
from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn

from . import charte


def _apply_alpha(container, alpha):
    """Ajoute une transparence (alpha en %) au a:srgbClr d'un a:solidFill."""
    if alpha is None:
        return
    fill = container.find(qn("a:solidFill"))
    if fill is None:
        return
    srgb = fill.find(qn("a:srgbClr"))
    if srgb is None:
        return
    srgb.append(srgb.makeelement(qn("a:alpha"), {"val": str(int(round(alpha * 1000)))}))


def run_color(run, hex_str, alpha=None):
    """Couleur d'un run, avec transparence optionnelle (alpha 0-100)."""
    run.font.color.rgb = charte.rgb(hex_str)
    _apply_alpha(run._r.get_or_add_rPr(), alpha)


def shape_fill(shape, hex_str, alpha=None):
    """Remplissage plein d'une forme, avec transparence optionnelle."""
    shape.fill.solid()
    shape.fill.fore_color.rgb = charte.rgb(hex_str)
    _apply_alpha(shape.fill._xPr, alpha)


def no_line(shape):
    shape.line.fill.background()


def line(shape, hex_str, width_pt, alpha=None):
    shape.line.color.rgb = charte.rgb(hex_str)
    shape.line.width = width_pt
    _apply_alpha(shape.line._get_or_add_ln(), alpha)


def letter_spacing(run, em, size_px):
    """letter-spacing CSS (em) -> attribut spc (1/100 pt)."""
    pts = em * size_px * 0.5
    run._r.get_or_add_rPr().set("spc", str(int(round(pts * 100))))


def corner_radius(shape, radius_px, ref_px):
    """Regle le rayon d'un ROUNDED_RECTANGLE : fraction du plus petit cote."""
    try:
        frac = max(0.0, min(0.5, radius_px / ref_px))
        shape.adjustments[0] = frac
    except (IndexError, ZeroDivisionError):
        pass


def tidy_textframe(tf, *, anchor=MSO_ANCHOR.TOP, wrap=True):
    """Cadre de texte sans marges, sans auto-resize, ancrage vertical donne."""
    tf.word_wrap = wrap
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
