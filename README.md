# mkg-docx

Moteur de generation de documents Word (.docx) A4 a la charte MKG Consulting (V6) :
couvertures pleine page, intercalaires de chapitre, sommaires, encadres insight,
cartes KPI, tableaux denses, en-tetes/pieds courants, pagination.

## Installation

```bash
pip install git+https://github.com/<compte>/mkg_docx.git
# ou, depuis une copie locale :
pip install .
```

Dependances : `python-docx`, `Pillow` (installees automatiquement).

> La charte impose **Segoe UI**. Sans les fichiers `segoeui*.ttf` dans
> `mkg_docx/fonts/`, les pages « brand » rasterisees utilisent un repli de fonte ;
> le texte natif du .docx reste defini en Segoe UI. Voir `mkg_docx/fonts/README.md`.

## Usage rapide

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

Le contrat complet de la spec JSON est documente en tete de `mkg_docx/spec.py`,
et le guide d'usage agent dans `mkg_docx/SKILL.md`.
