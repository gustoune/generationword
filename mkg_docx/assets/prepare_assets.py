"""Prepare les assets raster (PNG transparents) a partir des logos SVG MKG.

python-docx ne sait pas embarquer du SVG : on rasterise donc les logos une fois,
en PNG haute resolution avec canal alpha, recolores selon la charte :

- logo-mkg-bleu.png  : carre bleu profond (#0634ac) + lettres blanches, transparent
- logo-mkg-blanc.png : logo entierement blanc (contour + lettres), transparent

Les PNG generes sont ecrits dans CE dossier (mkg_docx/assets). Le script lit les
SVG embarques dans le meme dossier : le package est donc auto-suffisant.

Methode : on rend chaque variante de forme en blanc sur fond noir via svglib,
puis on derive l'alpha depuis la luminance (blanc -> opaque, noir -> transparent).
Cela evite toute dependance native problematique et reste 100 % deterministe.

Usage :
    python -m mkg_docx.assets.prepare_assets
    # ou : python mkg_docx/assets/prepare_assets.py
"""
from __future__ import annotations

import io
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

ASSETS = Path(__file__).resolve().parent

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

BLUE_PRIMARY = (6, 52, 172)        # #0634ac
WHITE = (255, 255, 255)

RENDER_SCALE = 3.0                 # 800 -> 2400 px


def _load_svg_root(svg_path: Path) -> ET.Element:
    return ET.parse(svg_path).getroot()


def _set_fills(root: ET.Element, class_to_fill: dict[str, str]) -> ET.Element:
    for el in root.iter():
        cls = el.get("class")
        if cls is None:
            continue
        fill = class_to_fill.get(cls.strip())
        if fill is not None:
            el.set("fill", fill)
            if "style" in el.attrib:
                del el.attrib["style"]
    return root


def _render_mask(root: ET.Element) -> Image.Image:
    data = ET.tostring(root, encoding="unicode")
    drawing = svg2rlg(io.StringIO(data))
    drawing.scale(RENDER_SCALE, RENDER_SCALE)
    drawing.width *= RENDER_SCALE
    drawing.height *= RENDER_SCALE
    buf = io.BytesIO()
    renderPM.drawToFile(drawing, buf, fmt="PNG", bg=0x000000)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def _mask_to_alpha(mask_rgb: Image.Image) -> Image.Image:
    return mask_rgb.convert("L")


def _colored_logo(alpha: Image.Image, color: tuple[int, int, int]) -> Image.Image:
    out = Image.new("RGBA", alpha.size, color + (0,))
    solid = Image.new("RGBA", alpha.size, color + (255,))
    out.paste(solid, (0, 0), alpha)
    return out


def _trim(img: Image.Image, pad_ratio: float = 0.0) -> Image.Image:
    bbox = img.split()[-1].getbbox()
    if bbox is None:
        return img
    if pad_ratio:
        w, h = img.size
        px = int(w * pad_ratio)
        py = int(h * pad_ratio)
        bbox = (max(0, bbox[0] - px), max(0, bbox[1] - py),
                min(w, bbox[2] + px), min(h, bbox[3] + py))
    return img.crop(bbox)


def build_logo_bleu(src: Path, dst: Path) -> None:
    square_root = _set_fills(_load_svg_root(src),
                             {"st0": "#ffffff", "st1": "#000000", "st2": "#000000"})
    square_alpha = _mask_to_alpha(_render_mask(square_root))

    letters_root = _set_fills(_load_svg_root(src),
                              {"st0": "#000000", "st1": "#ffffff", "st2": "#000000"})
    letters_alpha = _mask_to_alpha(_render_mask(letters_root))

    logo = _colored_logo(square_alpha, BLUE_PRIMARY)
    white_letters = _colored_logo(letters_alpha, WHITE)
    logo = Image.alpha_composite(logo, white_letters)
    logo = _trim(logo)
    logo.save(dst)
    print(f"  -> {dst.name}  {logo.size[0]}x{logo.size[1]}")


def build_logo_blanc(src: Path, dst: Path) -> None:
    root = _set_fills(_load_svg_root(src), {"st0": "#ffffff", "st1": "#ffffff"})
    alpha = _mask_to_alpha(_render_mask(root))
    logo = _colored_logo(alpha, WHITE)
    logo = _trim(logo)
    logo.save(dst)
    print(f"  -> {dst.name}  {logo.size[0]}x{logo.size[1]}")


def main() -> None:
    print("Preparation des logos PNG MKG :")
    build_logo_bleu(ASSETS / "logo-mkg-bleu.svg", ASSETS / "logo-mkg-bleu.png")
    build_logo_blanc(ASSETS / "logo-mkg-blanc.svg", ASSETS / "logo-mkg-blanc.png")
    print("Termine.")


if __name__ == "__main__":
    main()
