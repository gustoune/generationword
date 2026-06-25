---
name: mkg-ppt
description: >-
  Genere des presentations PowerPoint (.pptx) strictement conformes a la charte
  MKG Consulting (deck 16:9 1920x1080) : couverture, sommaire, intercalaires de
  chapitre, slides de contenu (paragraphes, KPI, tableaux, liste numerotee,
  SWOT, recommandations, timeline, takeaways), slides editoriales `gen` (fond
  clair/sombre, grand titre, grilles de cartes a icones : 4 box, 6 box, mecanisme,
  chaine d'etapes, classement a barres, courbe temporelle, trois images, tableau
  a en-tetes groupes), comparaison avant/apres plein ecran, stat hero, citation,
  cloture, merci. Les slides brand sont
  rendues en image pleine page (fidelite charte), les slides de contenu sont
  natives et editables. Utiliser des qu'il faut
  produire un deck / une presentation MKG a partir d'un contenu (texte, spec
  JSON ou API Python).
---

# MKG PPT - generateur de presentations a la charte MKG

Produit des `.pptx` fideles a la charte slides MKG (bleu #0634AC, electrique
#1F66F6, dark #0A0E1A, Segoe UI, 16:9). Le package est **auto-suffisant** :
code + assets (logos, texture) embarques dans `mkg_pptx/`.

Approche hybride :

- **Slides brand** (couverture, intercalaire, stat, citation, merci, cloture) :
  rendues en image pleine page (Pillow) -> gradient diagonal, texture, fidelite
  au pixel.
- **Slides de contenu** : natives python-pptx, **editables** dans PowerPoint
  (bandeau bleu + corps + pied avec pagination).

## Quand l'utiliser

- Generer un deck / presentation MKG (rapport, etude, pitch, analyse de marche).
- A partir d'un texte, d'une spec JSON ou via l'API Python.

## Etape 0 - Installation (recuperer le moteur)

Le package `mkg_pptx` est distribue avec `mkg_docx` dans le depot public
`gustoune/generationword`. **Installer une seule fois par session** :

```bash
pip install git+https://github.com/gustoune/generationword.git --break-system-packages -q
python3 -c "import mkg_pptx; print('OK')"
```

Le depot est public ; logos, texture et assets sont embarques dans le package :
rien d'autre a fournir. Les dependances (`python-pptx`, `Pillow`) sont installees
automatiquement.

**Methode de secours (sans `git`)** - telecharger l'archive du depot, la
decompresser puis installer :

```bash
curl -sSL -o mkg.zip https://codeload.github.com/gustoune/generationword/zip/refs/heads/main
unzip -q mkg.zip          # -> generationword-main/
pip install ./generationword-main --break-system-packages -q
```

**Si l'agent n'a aucun acces reseau** : demander a l'utilisateur de fournir le
dossier `mkg_pptx/` (avec ses `assets/`) dans le dossier de travail, puis
l'importer via `sys.path`.

Sous Windows, Segoe UI est detectee automatiquement ; sur macOS/Linux/conteneur,
voir `mkg_pptx/fonts/README.md` pour un rendu pixel-perfect des slides brand
(sinon un repli de fonte est utilise pour les images des slides brand, le texte
natif des slides de contenu restant en Segoe UI).

Dans les commandes ci-dessous, `PY` = `python3`.

## Workflow

```
- [ ] 1. Choisir le mode (texte / spec JSON / API)
- [ ] 2. Generer le .pptx
- [ ] 3. Verifier visuellement (rendu PDF/PNG optionnel)
```

### Mode A - depuis un texte / markdown leger

Front-matter (meta + couverture) + sections `#` (intercalaire) / `##` (slide de
contenu), listes `-`, listes `1.`, tableaux `| ... |`, citations `>`. Voir
`examples/note.md`.

```bash
PY -m mkg_pptx.cli text examples/note.md sortie.pptx
```

### Mode B - depuis une spec JSON declarative

Controle total des slides et des blocs. Voir `examples/exemple.json` et
[reference.md](reference.md) pour le catalogue complet.

```bash
PY -m mkg_pptx.cli spec examples/exemple.json sortie.pptx
```

### Mode C - via l'API Python (cas complexes)

```python
from mkg_pptx import MKGDeck

deck = MKGDeck(doc_line="MKG Consulting - Etude - Aix-les-Bains - 2025")
deck.add_cover(title="Etude d'implantation hoteliere",
               eyebrow="MKG - Rapport d'etude - 2025",
               subtitle="Residence les Aigues Blanches - Aix-les-Bains",
               meta=[["Client", "Turenne"], ["Date", "Nov. 2025"]],
               kpis=[{"value": "84", "label": "Appartements"}])
deck.add_agenda(title="Sommaire", items=[{"title": "Marche", "desc": "Offre & demande"}])
deck.add_section(number="01", title="Marche hotelier", eyebrow="Chapitre 1")
deck.content(eyebrow="Chapitre 01", title="Indicateurs cles",
             body={"type": "kpis", "cards": [
                 {"label": "RevPAR", "value": "117eur", "trend": "+2,8%", "trend_dir": "up"}]})
# slide editoriale gen + grille de cartes a icones (4 box / 6 box / mecanisme / etapes)
deck.gen(eyebrow="Pourquoi nous sommes reunis", title="Quatre objectifs",
         body={"type": "features", "items": [
             {"icon": "eye", "title": "Montrer", "text": "Notre lecture des donnees."},
             {"icon": "star", "title": "Valider", "text": "La direction prise."}]})
# classement a barres / courbe temporelle / trois images dans une slide gen
deck.gen(eyebrow="Tendance", title="Taux d'occupation",
         body={"type": "linechart", "yfmt": "{:.0f}%",
               "xlabels": ["2023", "2024", "2025"],
               "series": [{"label": "Marche", "values": [68, 72, 74]}]})
# comparaison avant / apres plein ecran
deck.add_beforeafter(
    before={"tag": "Avant", "headline": "Actif sous-exploite", "points": ["RevPAR < marche"]},
    after={"tag": "Apres", "headline": "4* createur de valeur", "points": ["RevPAR aligne"]})
deck.add_stat(number="+6,2", unit="%", eyebrow="Croissance du marche")
deck.add_quote(text="Un marche 4* en forte croissance.", author="S. Bergeret")
deck.add_closing(title="Discutons de votre projet",
                 contacts=[{"label": "Contact", "name": "S. Bergeret",
                            "lines": ["contact@mkg-consulting.com"]}])
deck.save("sortie.pptx")
```

### Demonstration (tous les types)

```bash
PY -m mkg_pptx.cli demo demo.pptx
```

## Verification visuelle (optionnel)

Si LibreOffice est disponible :

```bash
soffice --headless --convert-to pdf --outdir . sortie.pptx
```

## Regles de charte (a respecter absolument)

- Police **Segoe UI** uniquement.
- Palette : bleu **#0634AC**, electrique **#1F66F6**, dark **#0A0E1A**, tint
  **#E8EDF8**. Le bleu domine les bandeaux et chiffres cles.
- Slides brand : fonds sombres / colores + split diagonal + texture, rendus en
  image pleine page.
- **Logo** : `logo-mkg-new-rvb.png` (pied des slides de contenu) et
  `logo-mkg-blanc.png` (slides brand sombres).
- Tableaux : en-tete **electric**, lignes alternees (tint), total en bandeau
  bleu profond ; colonnes cles en bleu, variations en vert/rouge.
- **Typographie** : jamais de tiret cadratin/demi-cadratin (« — », « – ») ->
  toujours « - ». Le moteur normalise automatiquement.
- **Aucun pictogramme / emoji** nulle part. Le moteur supprime tout emoji ; les
  etoiles « * » du classement hotelier restent autorisees.

## Deploiement multi-plateforme

Ce dossier est portable tel quel (code + assets). Voir la section
« Deploiement » de [reference.md](reference.md) pour Cursor, Claude et ChatGPT.

## Ressources

- [reference.md](reference.md) : catalogue des slides et blocs, spec JSON,
  API, architecture, deploiement.
- `examples/note.md`, `examples/exemple.json` : entrees pretes a l'emploi.
