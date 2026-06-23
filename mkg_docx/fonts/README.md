# Polices (rendu des pages brand)

La charte MKG impose **Segoe UI**. Les pages pleine page (couverture,
intercalaires, page de fin) sont rasterisees par Pillow et ont besoin du
fichier de police reel.

## Windows

Rien a faire : Segoe UI est detectee dans `C:\Windows\Fonts`.

## macOS / Linux (rendu pixel-perfect)

Deposez ici les fichiers Segoe UI, par exemple :

```
segoeui.ttf        (regular)
segoeuib.ttf       (bold)
seguisb.ttf        (semibold)
segoeuil.ttf       (light)
segoeuisl.ttf      (semilight)
```

Sans ces fichiers, un repli systeme (DejaVu Sans / Arial) est utilise
**uniquement pour les images des pages brand**. Le texte natif du `.docx`
reste defini sur la fonte `Segoe UI` et s'affiche correctement a l'ouverture
dans Word sur une machine ou la police est installee.

> Segoe UI est une police proprietaire Microsoft : elle n'est pas redistribuee
> avec ce skill.
