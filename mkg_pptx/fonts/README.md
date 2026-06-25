# Polices Segoe UI (rendu des slides brand)

Les slides « brand » (couverture, transition, stat, citation, merci, clôture)
sont rasterisées avec Pillow, qui a besoin des fichiers `.ttf` Segoe UI.

- **Windows** : Segoe UI est détectée automatiquement dans `C:\Windows\Fonts`.
- **macOS / Linux** : déposez ici les fichiers Segoe UI pour un rendu fidèle :

```
segoeui.ttf        (regular)
segoeuib.ttf       (bold)
segoeuil.ttf       (light)
segoeuisl.ttf      (semilight)
seguisb.ttf        (semibold)
seguibl.ttf        (black)
```

Sans ces fichiers, un repli système (DejaVu/Arial) est utilisé uniquement pour
les images des slides brand ; le texte des slides de contenu reste « Segoe UI »
(natif PowerPoint, rendu avec la police installée sur le poste).
