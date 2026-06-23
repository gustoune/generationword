---
name: mkg-docx
description: "Use this skill whenever the user wants to produce a Word document (.docx) to the MKG Consulting visual identity (charte graphique) — hospitality/tourism studies, comptes rendus, notes blanches, market analyses, technical syntheses, or any branded MKG deliverable. Triggers include: any mention of 'à la charte MKG', 'document MKG', 'étude d'implantation', 'rapport MKG', or a request for an MKG-branded Word/PDF report with a cover page, chapter dividers, KPI cards, dense data tables, or running headers/footers. Also use to reformat an existing plain .docx into the MKG charte. Do NOT use for PowerPoint (.pptx), spreadsheets, generic unbranded Word docs (use the standard docx skill instead), or non-MKG clients."
---

# mkg_docx — génération de documents Word à la charte MKG Consulting

## Vue d'ensemble

`mkg_docx` est un moteur Python (sur `python-docx` + `Pillow`) qui produit des
`.docx` A4 conformes à la charte MKG Consulting (couche Document V6) : couvertures
pleine page, intercalaires de chapitre, sommaires, encadrés *insight*, cartes KPI,
tableaux denses, en-têtes/pieds courants, pagination. Toutes les couleurs, fontes
et marges proviennent d'une source unique (`charte.py`) — ne jamais coder une
valeur de charte en dur.

**Avant d'écrire du code, lire ce fichier en entier.** C'est la seule façon
fiable d'obtenir un rendu correct.

## Prérequis & installation

Le package n'est pas sur PyPI : il est fourni en archive. Dans une session Claude,
le déposer dans le répertoire de travail puis l'ajouter au `PYTHONPATH`.

```bash
# si fourni en zip
unzip -q mkg_docx.zip -d /home/claude/
cd /home/claude
python3 -c "import mkg_docx; print('OK')"   # python-docx & Pillow sont préinstallés
```

Dépendances : `python-docx`, `Pillow`. Si absentes :
`pip install python-docx Pillow --break-system-packages -q`.

> **Police.** La charte impose **Segoe UI**. Les pages « brand » (couverture,
> intercalaires, fin) sont rasterisées en image : sans les fichiers Segoe UI dans
> `mkg_docx/fonts/`, ces images utilisent un repli (DejaVu/Arial) — la mise en
> page reste correcte mais la fonte des images diffère. Le **texte natif** du
> `.docx` reste défini sur Segoe UI et s'affiche parfaitement chez l'utilisateur
> (Windows). Pour un rendu image pixel-perfect, déposer `segoeui*.ttf` dans
> `mkg_docx/fonts/` (voir `fonts/README.md`).

## Trois voies d'usage — choisir selon le cas

| Voie | Quand l'utiliser | Entrée |
|------|------------------|--------|
| **Spec JSON** (recommandée pour un agent) | Document structuré généré à partir d'un brief | dict / fichier `.json` |
| **API Python** | Contrôle fin, logique conditionnelle, données calculées | code |
| **Texte / markdown léger** | Conversion rapide d'une note existante | `.md` |
| **Reformat** | Remettre un `.docx` brut à la charte | `.docx` |

### Voie 1 — Spec JSON (à privilégier)

```python
from mkg_docx import build_from_spec
spec = {
  "meta": {"orientation": "portrait", "study_title": "Étude d'implantation",
           "date": "Juin 2026", "confidential": "MKG CONSULTING · DOCUMENT CONFIDENTIEL"},
  "blocks": [
    {"type": "cover", "title": "Résidence les\nAigues Blanches",
     "eyebrow": "Étude d'implantation", "subtitle": "Aix-les-Bains · Savoie",
     "fields": [["Client", "Turenne Hôtellerie"], ["Auteur", "..."], ["Date", "Juin 2026"]],
     "confidential": "DOCUMENT CONFIDENTIEL · USAGE EXCLUSIF TURENNE"},
    {"type": "summary", "entries": [{"number": "01", "title": "Zone d'étude", "desc": "Démographie · environnement"}]},
    {"type": "divider", "number": "01", "title": "Zone d'étude",
     "chapter_label": "Chapitre 01", "items": ["1.1 Démographie", "1.2 Économie"]},
    {"type": "section_title", "text": "Performances par segment"},
    {"type": "kpi", "cards": [{"label": "RevPAR marché", "value": "78,30 €", "trend": "+3,4 %", "trend_dir": "up"}]},
    {"type": "table", "headers": ["Segment", "RevPAR", "Occupation"],
     "rows": [["4★ & 5★", "92,10 €", "74,2 %"]],
     "footer": ["Total marché", "78,30 €", "71,4 %"],
     "aligns": ["left", "num", "num"], "source": "Source : MKG Hospitality Database."},
    {"type": "end", "tagline": "MKG Consulting", "fields": [["Contact", "..."]]}
  ]
}
doc = build_from_spec(spec)
doc.save("/mnt/user-data/outputs/etude.docx")
```

### Voie 2 — API Python directe

```python
from mkg_docx import MKGDocument
doc = MKGDocument(orientation="portrait", study_title="...", date="Juin 2026")
doc.add_cover(title="...", eyebrow="...", subtitle="...", fields=[("Client","...")])
doc.section_title("Analyse")
doc.paragraph("...")
doc.kpi_row([{"label":"...","value":"...","trend":"+2 %","trend_dir":"up"}])
doc.table(["A","B"], [["1","2"]], aligns=["left","num"], source="Source : ...")
doc.add_end(tagline="MKG Consulting")
doc.save("/mnt/user-data/outputs/doc.docx")
```

### Voie 3 — CLI

```bash
python3 -m mkg_docx.cli spec brief.json sortie.docx
python3 -m mkg_docx.cli text note.md sortie.docx
python3 -m mkg_docx.cli reformat brut.docx sortie.docx --cover --title "..." --date "Juin 2026"
python3 -m mkg_docx.cli demo demo.docx          # document de démonstration complet
```

## Référence des blocs (spec JSON)

Pages « brand » pleine page : `cover`, `divider`, `end`.
Contenu : `eyebrow`, `section_title` (filet dégradé), `title_h1`, `subheading`,
`paragraph`, `small`, `bullets`, `summary`, `glossary`, `insight`, `kpi`,
`table`, `gradient_rule`, `spacer`, `page_break`.

Détails utiles :
- **table** — `aligns[i]` ∈ `{left, right, num, pos, neg}` (`pos`/`neg` colorent les
  variations vert/rouge) ; `col_ratios` fixe les largeurs relatives ; `footer`
  ajoute une ligne de total surlignée ; `source` ajoute une ligne légende.
- **kpi** — `cards[i]` = `{label, value, trend?, trend_dir?(up/down/neutral), variant?(default/dark)}`.
- **cover / end / divider** — `\n` dans `title` force un saut de ligne.

Le contrat complet est documenté en tête de `spec.py`.

## Règles d'or

1. **Toujours produire le fichier final dans `/mnt/user-data/outputs/`** puis le
   présenter via `present_files`.
2. **Vérifier le rendu** sur les documents importants : convertir en PDF
   (`soffice --headless --convert-to pdf`) puis rasteriser quelques pages
   (`pdftoppm`) et inspecter visuellement avant de livrer.
3. **Ne jamais coder de couleur/taille/marge en dur** — passer par `charte.py`.
4. Orientation `paysage` pour les documents à tableaux larges (comptes
   d'exploitation multi-années), `portrait` par défaut.
5. Privilégier la **spec JSON** : c'est le contrat conçu pour un agent.
