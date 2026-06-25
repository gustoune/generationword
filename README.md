# mkg-suite

Moteurs de generation de livrables a la charte MKG Consulting :

- **`mkg_docx`** - documents Word (.docx) A4 (V6) : couvertures pleine page,
  intercalaires de chapitre, sommaires, encadres insight, cartes KPI, tableaux
  denses, en-tetes/pieds courants, pagination.
- **`mkg_pptx`** - presentations PowerPoint (.pptx) 16:9 : couverture, sommaire,
  intercalaires, slides de contenu editables (KPI, tableaux, SWOT, timeline,
  recommandations), slides editoriales a icones, stat hero, citation, cloture.

## Installation

```bash
pip install git+https://github.com/gustoune/generationword.git
# ou, depuis une copie locale :
pip install .
```

Dependances : `python-docx`, `python-pptx`, `Pillow` (installees automatiquement).

> La charte impose **Segoe UI**. Sans les fichiers `segoeui*.ttf` dans
> `mkg_docx/fonts/` ou `mkg_pptx/fonts/`, les pages/slides « brand » rasterisees
> utilisent un repli de fonte ; le texte natif reste defini en Segoe UI.

## Usage rapide - Word

```python
from mkg_docx import build_from_spec
doc = build_from_spec({
    "meta": {"date": "Juin 2026", "study_title": "Etude"},
    "blocks": [
        {"type": "cover", "title": "Titre", "eyebrow": "Sous-titre"},
        {"type": "section_title", "text": "Analyse"},
        {"type": "end"},
    ],
})
doc.save("sortie.docx")
```

```bash
mkg-docx demo demo.docx          # document de demonstration
mkg-docx spec brief.json out.docx
```

## Usage rapide - PowerPoint

```python
from mkg_pptx import MKGDeck
deck = MKGDeck(doc_line="MKG Consulting - Etude - 2025")
deck.add_cover(title="Etude d'implantation", eyebrow="MKG - 2025")
deck.content(eyebrow="Chapitre 01", title="Indicateurs cles",
             body={"type": "kpis", "cards": [
                 {"label": "RevPAR", "value": "117eur", "trend": "+2,8%", "trend_dir": "up"}]})
deck.save("sortie.pptx")
```

```bash
mkg-pptx demo demo.pptx          # deck de demonstration
mkg-pptx spec brief.json out.pptx
mkg-pptx text note.md out.pptx
```

Le contrat des specs JSON est documente en tete de `mkg_docx/spec.py` et
`mkg_pptx/spec.py`. Les guides d'usage agent sont dans `mkg_docx/SKILL.md` et
`mkg_pptx/SKILL.md` (catalogue complet des slides : `mkg_pptx/reference.md`).
