# MKG PPT - reference

Documentation detaillee du skill `mkg-ppt`. Le `SKILL.md` couvre le workflow ;
ce fichier detaille les types de slides, les blocs de contenu, la spec JSON,
l'API, l'architecture et le deploiement.

## Architecture

| Fichier | Role |
|---|---|
| `mkg_pptx/charte.py` | Tokens (palette slides, fonts, geometrie 1920x1080) - source unique |
| `mkg_pptx/units.py` | Conversions px -> EMU (x6350) et px -> pt (x0,5) |
| `mkg_pptx/oxml.py` | Helpers natifs (couleur + alpha, tracking, coins arrondis, marges) |
| `mkg_pptx/fonts.py` | Resolution Segoe UI pour le rendu Pillow (slides brand) |
| `mkg_pptx/icons.py` | Pictogrammes line-art (style feather) rasterises en PNG pour les cartes |
| `mkg_pptx/charts.py` | Courbe temporelle rasterisee (grille, axes, series) via Pillow |
| `mkg_pptx/pillow_bg.py` | Rendu image des slides brand (cover, section, stat, quote, merci, closing) + panneau texture |
| `mkg_pptx/builder.py` | `MKGDeck` - slides natives + brand, blocs de corps |
| `mkg_pptx/spec.py` | Spec JSON declarative -> deck |
| `mkg_pptx/text_adapter.py` | Texte / markdown leger -> spec |
| `mkg_pptx/sanitize.py` | Assainissement editorial (tirets -> `-`, suppression pictos) |
| `mkg_pptx/cli.py` | Ligne de commande |
| `mkg_pptx/demo.py` | Deck de demonstration (tous les types) |
| `mkg_pptx/assets/` | Logos PNG + `bg-texture.jpg` |

Conversion : le canevas charte 1920x1080 px vaut exactement 13,333 x 7,5 pouces
(144 px/pouce). On transcrit donc les coordonnees CSS directement en px.

## Types de slides (spec JSON `slides[].type`)

| type | role | champs principaux |
|---|---|---|
| `cover` | couverture | title, eyebrow, subtitle, meta[[k,v]], kpis[{value,label}], footer_note |
| `agenda` | sommaire | title, eyebrow, subtitle, items[{title,desc}] |
| `section` | intercalaire chapitre | number, title, eyebrow, desc, toc[{label,active}] |
| `content` | slide de contenu (bandeau bleu) | eyebrow, title, badge, `body` ou `columns` |
| `gen` | slide editoriale (fond clair/sombre, grand titre, grilles riches) | eyebrow, title, subtitle, `body` ou `columns`, dark, title_size, intro |
| `beforeafter` | comparaison plein ecran (avant clair / apres bleu) | before{tag,headline,points[]}, after{tag,headline,points[]} |
| `stat` | chiffre hero | number, unit, eyebrow, desc, source, dark |
| `quote` | citation | text, author |
| `closing` | cloture / contact | title, eyebrow, subtitle, contacts[{label,name,role,lines}] |
| `merci` | remerciement | title, subtitle, contact |

`content` et `gen` acceptent soit `body` (un bloc), soit `columns` (1 ou 2 blocs
cote a cote). `gen` reproduit la famille `.gen` de `slides.css` (couverture
editoriale claire ou sombre) ; `intro: true` centre verticalement un grand titre
sans corps (slide d'accroche).

## Blocs de corps (`body` / `columns[]`)

Chaque bloc est un objet `{ "type": ..., ... }`. `eyebrow` est commun (libelle
de section au-dessus du bloc).

| type | champs |
|---|---|
| `paragraphs` | `paras` [str], `highlight` {title, text} (encadre bleu) |
| `bullets` | `items` [str] ou [{lead, text}] |
| `numbered` | `items` [str] ou [{lead, text}], `cols` (defaut 2) |
| `kpis` | `cards` [{label, value, trend?, trend_dir? up/down/neutral, sub?, variant? accent}], `cols` |
| `table` | `headers` [str], `rows` [[...]], `footer` [...], `aligns` [left/right/key/pos/neg], `widths` |
| `swot` | `pros` [str], `cons` [str], `pro_title`, `con_title` |
| `reco` | `items` [{title, desc}] |
| `timeline` | `phases` [{year, title, desc}] |
| `takeaways` | `items` [str] ou [{lead, text}] |
| `features` | grille 4 box (carte bleu-clair, pastille ronde sombre + icone) : `items` [{icon, title, text}] |
| `cards` | grille 6 box : `items` [{icon, title, text}], `cols`, `variant` (`light` defaut / `tint` bleu) |
| `concept` | mecanisme 2-3 cartes + fleches rondes : `items` [{icon, tag, title, text, accent?}] |
| `steps` | chaine d'etapes horizontale (claire ou sombre) : `items` [{title, text}], `flow` (legende italique) |
| `steps2` | etapes en cartes : `items` [{eyebrow, title, text}] |
| `ranking` | classement a barres (top 3 bleu, 4-6 electrique, reste gris) : `items` [{name, value, display?}], `maxval?` |
| `linechart` | courbe temporelle : `series` [{label, color?, values[], dashed?}], `xlabels` [str], `ymin?`, `ymax?`, `yfmt?` (ex `"{:.0f}%"`) |
| `photos` | emplacements photo MKG (cadre sombre + legende) : `items` [{label, caption, sub}] |
| `table_grouped` | tableau a en-tetes groupes : `label_header`, `groups` [{label, span}], `subheaders` [str], `rows` [[lbl, cellule...]] ; cellule = str ou {v, cls} (cls : key/pos/neg) |

Les blocs `features`, `cards`, `concept` portent un champ `icon` (nom de
pictogramme). Icones disponibles dans `icons.py` : `eye`, `bar-chart`,
`activity`, `trending-up`, `star`, `globe`, `search`, `grid`, `map-pin`,
`dollar`, `home`, `building`, `target`, `layers`, `check`, `check-circle`,
`credit-card`, `calendar`, `users`, `compass`, `briefcase`, `zap`, `pie`,
`droplet`, `merge`, `sliders`, `award`, `phone`, `book`, `flag`, `shield`,
`clock`, `refresh`, `image`, `minus`, `arrow-right` (+ alias). Nom inconnu ->
cercle neutre.

## API Python - methodes de `MKGDeck`

- Brand : `add_cover`, `add_agenda`, `add_section`, `add_stat`, `add_quote`,
  `add_closing`, `add_merci`.
- Contenu : `content(eyebrow, title, badge, body=..., columns=[...])`.
- Editorial : `gen(eyebrow, title, subtitle, body=..., columns=[...], dark=False, title_size=46, intro=False)`.
- Comparaison : `add_beforeafter(before={...}, after={...})`.
- `save(path)`.

Constructeur : `MKGDeck(doc_line="", scale=2, grain=True, assets_dir=None)`.
`scale` controle la nettete des images brand (2 = 3840x2160).

## Regles editoriales (assainissement automatique)

Tout texte est nettoye au plus bas niveau via `sanitize.clean()` :

- tirets typographiques (« — », « – », signe moins) -> « - » ;
- pictogrammes / emoji supprimes (les etoiles « * » du classement hotelier
  restent autorisees).

## Regeneration des assets

Les logos et la texture sont copies depuis `MKG/assets/`. Pour les mettre a
jour, remplacer les fichiers de `mkg_pptx/assets/` (memes noms).

## Deploiement multi-plateforme

`mkg_pptx` est distribue avec `mkg_docx` dans le depot public
`github.com/gustoune/generationword` et s'installe via pip.

### Installation standard (Claude, Cursor, ChatGPT, CI)
```bash
pip install git+https://github.com/gustoune/generationword.git --break-system-packages -q
python3 -m mkg_pptx.cli demo demo.pptx
```
Logos, texture et assets sont embarques (package data) : aucune ressource a
fournir. Dependances installees automatiquement (`python-pptx`, `Pillow`).

### Installation locale (copie du depot)
```bash
git clone https://github.com/gustoune/generationword.git
pip install ./generationword
python3 -m mkg_pptx.cli demo demo.pptx
```

### Methode de secours (sans git)
```bash
curl -sSL -o mkg.zip https://codeload.github.com/gustoune/generationword/zip/refs/heads/main
unzip -q mkg.zip && pip install ./generationword-main --break-system-packages -q
```
