"""Deck de demonstration : exerce tous les types de slides et de blocs."""
from __future__ import annotations

from pathlib import Path

from .builder import MKGDeck

DOC = "MKG Consulting \u00b7 Etude d'implantation \u00b7 Aix-les-Bains \u00b7 2025"


def build_demo(out_path) -> Path:
    deck = MKGDeck(doc_line=DOC)

    deck.add_cover(
        title="Etude d'implantation hoteliere",
        eyebrow="MKG \u00b7 Rapport d'etude \u00b7 2025",
        subtitle="Residence les Aigues Blanches - Aix-les-Bains, Savoie",
        meta=[["Client", "Turenne Hotellerie"], ["Date", "Novembre 2025"],
              ["Auteur", "Sylvie Bergeret, MRICS"], ["Reference", "MKG-2025-AIX-001"]],
        kpis=[{"value": "84", "label": "Appartements"},
              {"value": "4,5 Meur", "label": "Valeur actuelle"},
              {"value": "13,2 Meur", "label": "Valeur potentielle"}],
        footer_note="Document confidentiel \u00b7 Usage exclusif")

    deck.add_agenda(
        title="Sommaire", eyebrow="Plan du rapport",
        subtitle="Etude d'implantation hoteliere \u00b7 Aix-les-Bains",
        items=[{"title": "Lettre de mission & objectifs", "desc": "Contexte, mandat et conditions"},
               {"title": "Analyse de l'environnement", "desc": "Profil, localisation, economie locale"},
               {"title": "Marche hotelier", "desc": "Offre, demande, concurrence, performances"},
               {"title": "Evaluation financiere", "desc": "Methodologie, projections, valorisation"},
               {"title": "Conclusions & recommandations", "desc": "Synthese, forces, preconisations"}])

    deck.add_section(
        number="01", title="Environnement", eyebrow="Chapitre 1 - Analyse",
        desc="Profil de l'actif, localisation, acces et contexte economique du territoire.",
        toc=[{"label": "Environnement", "active": True}, {"label": "Marche hotelier"},
             {"label": "Evaluation"}])

    deck.content(
        eyebrow="Chapitre 01 - Lettre de mission", title="Objectifs de l'etude",
        badge="8 objectifs",
        body={"type": "numbered", "cols": 2, "items": [
            {"lead": "Mesurer les flux", "text": "de clienteles actuelles et potentielles."},
            {"lead": "Analyser l'offre", "text": "actuelle et future du territoire."},
            {"lead": "Identifier les concurrents", "text": "et le positionnement du projet."},
            {"lead": "Analyser les performances", "text": "des etablissements de la zone."},
            {"lead": "Anticiper la demande", "text": "potentielle et son evolution."},
            {"lead": "Emettre des recommandations", "text": "de positionnement et capacite."}]})

    deck.content(
        eyebrow="Chapitre 01 - Environnement", title="Contexte economique & touristique",
        badge="Aix-les-Bains",
        columns=[
            {"type": "paragraphs", "eyebrow": "Dynamique du territoire",
             "paras": ["Premiere station thermale de France par sa frequentation, Aix-les-Bains conjugue bien-etre, clientele affaires et attractivite du lac.",
                       "La requalification du front de lac et le tourisme MICE soutiennent une demande en croissance sur le milieu de gamme."],
             "highlight": {"title": "Tendance porteuse",
                           "text": "Le tourisme thermal progresse de +6,2% par an, tire par une clientele senior et MICE."}},
            {"type": "kpis", "eyebrow": "Indicateurs cles", "cols": 2, "cards": [
                {"label": "Nuitees annuelles", "value": "1,2M", "trend": "+4,8% vs N-1", "trend_dir": "up"},
                {"label": "Curistes / an", "value": "28 000", "trend": "+3,1%", "trend_dir": "up"},
                {"label": "Duree sejour moy.", "value": "4,2 nuits", "trend": "stable", "trend_dir": "neutral"},
                {"label": "Saisonnalite ete", "value": "91%", "variant": "accent", "sub": "Taux occ. juin-aout"}]}])

    deck.add_section(number="02", title="Marche hotelier", eyebrow="Chapitre 2 - Analyse",
                     desc="Offre concurrentielle, performances et segmentation de la clientele.",
                     toc=[{"label": "Environnement"}, {"label": "Marche hotelier", "active": True},
                          {"label": "Evaluation"}])

    deck.content(
        eyebrow="Chapitre 02 - Marche hotelier", title="Offre concurrentielle",
        badge="Novembre 2025",
        body={"type": "table",
              "headers": ["Etablissement", "Categorie", "RevPAR", "Occ.", "Var."],
              "aligns": ["left", "key", "key", "right", "pos"],
              "rows": [["Hotel du Lac", "4* Milieu", "118eur", "76%", "+4,2%"],
                       ["Domaine Thermal", "3* Eco.", "84eur", "71%", "-1,8%"],
                       ["Residence Savoia", "4* Res.", "97eur", "68%", "+2,1%"],
                       ["Le Revard Hotel", "3* Eco.", "72eur", "65%", "stable"],
                       ["Chateau des Bains", "5* Luxe", "215eur", "82%", "+9,7%"]],
              "footer": ["Moyenne marche", "", "117eur", "72%", "+2,8%"]})

    deck.add_stat(number="+6,2", unit="%", eyebrow="Croissance annuelle du marche",
                  desc="Progression du tourisme thermal et de bien-etre dans la zone de chalandise.",
                  source="Source : Observatoire MKG \u00b7 2025")

    deck.content(
        eyebrow="Chapitre 03 - Conclusions", title="Forces & points de vigilance",
        badge="Synthese",
        body={"type": "swot",
              "pros": ["Emplacement premium en bord de lac",
                       "Marche 4* en croissance soutenue",
                       "Forte saisonnalite estivale (91%)"],
              "cons": ["Travaux de repositionnement importants",
                       "Saisonnalite hivernale marquee (54%)",
                       "Concurrence 5* sur le haut de gamme"]})

    deck.content(
        eyebrow="Chapitre 03 - Conclusions", title="Recommandations",
        body={"type": "reco", "items": [
            {"title": "Positionner l'actif en 4* milieu de gamme",
             "desc": "Cibler le couple croissance / RevPAR le plus favorable du marche."},
            {"title": "Phaser les travaux sur 18 mois",
             "desc": "Limiter l'impact d'exploitation et securiser l'ouverture 2028."},
            {"title": "Nouer un partenariat enseigne",
             "desc": "Maximiser la distribution et la montee en gamme."}]})

    deck.content(
        eyebrow="Calendrier", title="Trajectoire du projet",
        body={"type": "timeline", "phases": [
            {"year": "2025", "title": "Etude & validation", "desc": "Faisabilite et valorisation."},
            {"year": "2026", "title": "Conception", "desc": "Permis et design."},
            {"year": "2027", "title": "Travaux", "desc": "Repositionnement 4*."},
            {"year": "2028", "title": "Ouverture", "desc": "Mise en exploitation."}]})

    deck.content(
        eyebrow="En bref", title="A retenir",
        body={"type": "takeaways", "items": [
            {"lead": "13,2 Meur", "text": "de valeur potentielle apres travaux."},
            {"lead": "4* milieu de gamme", "text": "le positionnement cible optimal."},
            {"lead": "Ouverture 2028", "text": "pour capter la croissance du marche."}]})

    # ---- Famille GEN : grilles et visuels riches -------------------
    deck.gen(eyebrow="Methode", title="Une approche structuree du marche",
             subtitle="Quatre piliers d'analyse pour eclairer la decision.",
             body={"type": "features", "items": [
                 {"icon": "search", "title": "Observation", "text": "Releve terrain et collecte des donnees de marche."},
                 {"icon": "bars", "title": "Analyse", "text": "Croisement des performances et des tendances."},
                 {"icon": "target", "title": "Positionnement", "text": "Definition du couple offre / clientele cible."},
                 {"icon": "award", "title": "Recommandation", "text": "Trajectoire de valeur et plan d'action."}]})

    deck.gen(eyebrow="Leviers", title="Six leviers de creation de valeur",
             body={"type": "cards", "items": [
                 {"icon": "home", "title": "Repositionnement", "text": "Montee en gamme 4* milieu."},
                 {"icon": "users", "title": "Mix clientele", "text": "Equilibrer affaires et loisirs."},
                 {"icon": "calendar", "title": "Saisonnalite", "text": "Lisser l'occupation annuelle."},
                 {"icon": "dollar", "title": "Yield", "text": "Optimiser l'ADR par segment."},
                 {"icon": "globe", "title": "Distribution", "text": "Renforcer le direct et l'OTA."},
                 {"icon": "shield", "title": "Marque", "text": "Affiliation a une enseigne."}]})

    deck.gen(eyebrow="Mecanique", title="Du marche a la valorisation",
             body={"type": "concept", "items": [
                 {"icon": "search", "tag": "Entree", "title": "Donnees de marche",
                  "text": "Offre, demande et performances de la zone."},
                 {"icon": "merge", "tag": "Croisement", "title": "Modele d'analyse", "accent": True,
                  "text": "Confrontation des signaux et scenarios."},
                 {"icon": "trending-up", "tag": "Sortie", "title": "Valeur de l'actif",
                  "text": "Projection de RevPAR et valorisation."}]})

    deck.gen(eyebrow="Demarche", title="Le deroule de la mission", dark=True,
             body={"type": "steps", "flow": "Un fil conducteur unique, du terrain a la decision.",
                   "items": [
                       {"title": "Cadrage", "text": "Objectifs et perimetre."},
                       {"title": "Terrain", "text": "Collecte et entretiens."},
                       {"title": "Analyse", "text": "Traitement des donnees."},
                       {"title": "Resultats", "text": "Recommandations chiffrees."}]})

    deck.add_beforeafter(
        before={"tag": "Avant", "headline": "Un actif sous-exploite",
                "points": ["Positionnement 3* indifferencie",
                           "RevPAR inferieur de 20% au marche",
                           "Saisonnalite hivernale non maitrisee"]},
        after={"tag": "Apres", "headline": "Un 4* createur de valeur",
               "points": ["Montee en gamme assumee et lisible",
                          "RevPAR aligne sur les leaders du segment",
                          "Occupation lissee sur l'annee"]})

    deck.gen(eyebrow="Performance", title="Classement des concurrents",
             subtitle="RevPAR 2025 des etablissements de la zone, en euros.",
             body={"type": "ranking", "items": [
                 {"name": "Chateau des Bains", "value": 215, "display": "215 EUR"},
                 {"name": "Hotel du Lac", "value": 118, "display": "118 EUR"},
                 {"name": "Residence Savoia", "value": 97, "display": "97 EUR"},
                 {"name": "Domaine Thermal", "value": 84, "display": "84 EUR"},
                 {"name": "Le Revard Hotel", "value": 72, "display": "72 EUR"}]})

    deck.gen(eyebrow="Tendance", title="Evolution du taux d'occupation",
             body={"type": "linechart", "yfmt": "{:.0f}%",
                   "xlabels": ["2021", "2022", "2023", "2024", "2025"],
                   "series": [
                       {"label": "Projet 4*", "color": "0634AC", "values": [0, 0, 0, 71, 76]},
                       {"label": "Marche milieu de gamme", "color": "1F66F6", "values": [58, 64, 68, 72, 74]},
                       {"label": "Moyenne zone", "color": "B4B4B4", "dashed": True, "values": [55, 60, 64, 68, 70]}]})

    deck.gen(eyebrow="Terrain", title="L'actif en images",
             body={"type": "photos", "items": [
                 {"label": "Vue 01", "caption": "Front de lac", "sub": "Emplacement premium, Aix-les-Bains"},
                 {"label": "Vue 02", "caption": "Hall d'accueil", "sub": "A repositionner en 4*"},
                 {"label": "Vue 03", "caption": "Espace bien-etre", "sub": "Atout thermal differenciant"}]})

    deck.content(
        eyebrow="Synthese chiffree", title="Indicateurs par segment",
        body={"type": "table_grouped", "label_header": "Segment",
              "groups": [{"label": "Occupation", "span": 2}, {"label": "Tarification", "span": 2}],
              "subheaders": ["2024", "2025", "ADR", "RevPAR"],
              "rows": [
                  ["Luxe", {"v": "80%"}, {"v": "82%", "cls": "pos"}, {"v": "265 EUR", "cls": "key"}, {"v": "215 EUR", "cls": "key"}],
                  ["Milieu 4*", {"v": "73%"}, {"v": "76%", "cls": "pos"}, {"v": "155 EUR", "cls": "key"}, {"v": "118 EUR", "cls": "key"}],
                  ["Economique 3*", {"v": "70%"}, {"v": "68%", "cls": "neg"}, {"v": "118 EUR", "cls": "key"}, {"v": "82 EUR", "cls": "key"}]]})

    deck.add_quote(
        text="Le projet 4* cible un RevPAR de 110-125eur des la 3eme annee, en ligne avec les leaders du segment milieu de gamme.",
        author="Sylvie Bergeret, MRICS")

    deck.add_closing(
        title="Discutons de votre projet", eyebrow="Conclusions",
        subtitle="MKG Consulting accompagne votre strategie d'implantation hoteliere.",
        contacts=[{"label": "Contact", "name": "Sylvie Bergeret", "role": "Directrice | MRICS",
                   "lines": ["contact@mkg-consulting.com"]}])

    deck.add_merci(title="Merci", subtitle="MKG Consulting \u00b7 L'intelligence de marche hoteliere.",
                   contact="contact@mkg-consulting.com")

    return deck.save(out_path)
