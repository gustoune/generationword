"""Document de demonstration : exerce tous les blocs de la charte.

Contenu d'exemple repris du rapport de reference (Residence les Aigues Blanches),
utile pour valider visuellement le rendu.
"""
from __future__ import annotations

from pathlib import Path

from .builder import MKGDocument


def build_demo(out: str | Path, *, orientation: str = "portrait") -> Path:
    doc = MKGDocument(
        orientation=orientation,
        study_title="\u00c9tude d'implantation \u00b7 R\u00e9sidence les Aigues Blanches \u2014 Aix-les-Bains",
        date="Novembre 2025",
    )

    # 1 - Couverture
    doc.add_cover(
        title="R\u00e9sidence les\nAigues Blanches",
        eyebrow="\u00c9tude d'implantation",
        subtitle="Aix-les-Bains \u00b7 Savoie \u00b7 73100",
        fields=[
            ("Client", "Turenne H\u00f4tellerie"),
            ("Auteur", "Sylvie Bergeret \u2014 Directrice \u00b7 MRICS"),
            ("Date", "Novembre 2025"),
        ],
        confidential="Document confidentiel \u00b7 Usage exclusif Turenne H\u00f4tellerie",
        address="13 Mont\u00e9e des Carri\u00e8res Romaines, 73100 Aix-les-Bains",
    )

    # 2 - Lettre de mission
    doc.section_title("Lettre de mission")
    doc.subheading("Objectifs de l'\u00e9tude")
    doc.paragraph(
        "MKG Consulting a proc\u00e9d\u00e9, \u00e0 la demande de Turenne H\u00f4tellerie, \u00e0 "
        "l'\u00e9valuation de l'actif h\u00f4telier projet\u00e9 sur le site de la R\u00e9sidence "
        "les Aigues Blanches, en vue d'appr\u00e9cier la faisabilit\u00e9 de l'op\u00e9ration "
        "et d'en estimer la valeur actuelle et potentielle. La date de valorisation "
        "retenue est le 30 novembre 2025.")
    doc.subheading("Le pr\u00e9sent rapport comprend")
    doc.bullets([
        "Un descriptif du bien \u00e9tudi\u00e9",
        "Une analyse de l'environnement \u2014 d\u00e9mographie, \u00e9conomie, tourisme",
        "Une estimation du march\u00e9 h\u00f4telier et para-h\u00f4telier",
        "L'estimation financi\u00e8re et la valorisation du bien",
    ])

    # 3 - Sommaire
    doc.page_break()
    doc.section_title("Sommaire")
    doc.summary([
        {"number": "01", "title": "Zone d'\u00e9tude",
         "desc": "D\u00e9mographie \u00b7 environnement \u00e9conomique \u00b7 environnement touristique"},
        {"number": "02", "title": "March\u00e9 h\u00f4telier",
         "desc": "Offre h\u00f4teli\u00e8re et para-h\u00f4teli\u00e8re \u00b7 locative \u00b7 performances"},
        {"number": "03", "title": "\u00c9valuation",
         "desc": "Comptes d'exploitation \u00b7 valeur actuelle et potentielle"},
    ])

    # 4 - Synthese : KPI + insight
    doc.page_break()
    doc.eyebrow("Faits marquants")
    doc.section_title("Synth\u00e8se et faits marquants")
    doc.kpi_row([
        {"label": "RevPAR moyen", "value": "78,30 \u20ac", "trend": "+4,2 % vs 2024", "trend_dir": "up"},
        {"label": "Taux d'occupation", "value": "71,4 %", "trend": "+1,8 pt vs 2024", "trend_dir": "up"},
        {"label": "Prix moyen", "value": "109,60 \u20ac", "trend": "+2,1 % vs 2024", "trend_dir": "up"},
        {"label": "Valeur estim\u00e9e", "value": "4,5 M\u20ac", "trend": "Fourchette haute", "variant": "dark"},
    ])
    doc.paragraph(
        "Le bassin d'Aix-les-Bains confirme une dynamique touristique soutenue, "
        "port\u00e9e par le thermalisme, le lac du Bourget et le tourisme d'affaires. "
        "Le segment 4\u2605 affiche la croissance la plus solide du march\u00e9.")
    doc.insight(
        "Le segment 4\u2605 affiche la croissance la plus solide du bassin, avec un "
        "RevPAR en hausse de +4,2 % en moyenne annuelle.")

    # 5 - Intercalaire
    doc.add_divider(
        number="01", title="Zone d'\u00e9tude", chapter_label="Chapitre 01",
        items=["2.1 \u2014 Donn\u00e9es d\u00e9mographiques",
               "2.2 \u2014 Environnement \u00e9conomique",
               "2.3 \u2014 Environnement touristique"],
        footer="Novembre 2025 \u00b7 R\u00e9sidence les Aigues Blanches \u00b7 p. 09")

    # 6 - Tableau dense
    doc.eyebrow("Chapitre 02 \u00b7 March\u00e9 h\u00f4telier")
    doc.section_title("Performances par segment")
    doc.table(
        headers=["Segment", "\u00c9tablissements", "RevPAR", "Occupation", "\u00c9volution"],
        rows=[
            ["4\u2605 & 5\u2605", "412", "92,10 \u20ac", "74,2 %", "+4,2 %"],
            ["3\u2605", "1 086", "64,80 \u20ac", "71,0 %", "+2,1 %"],
            ["1\u2605 & 2\u2605", "743", "41,30 \u20ac", "68,5 %", "\u22120,8 %"],
        ],
        footer=["Total march\u00e9", "2 241", "78,30 \u20ac", "71,4 %", "+3,4 %"],
        aligns=["left", "right", "num", "right", "pos"],
        col_ratios=[2, 1.4, 1.2, 1.2, 1.2],
        source="Source : MKG Hospitality Database \u2014 bassin d'Aix-les-Bains, exercice 2024.")

    # 7 - Comptes d'exploitation (tableau large)
    doc.section_title("Comptes d'exploitation pr\u00e9visionnels")
    doc.table(
        headers=["Poste (\u20ac HT)", "An 1", "An 2", "An 3", "An 4", "An 5"],
        rows=[
            ["Chiffre d'affaires h\u00e9bergement", "2 184 000", "2 472 000", "2 686 000", "2 814 000", "2 902 000"],
            ["Chiffre d'affaires restauration", "468 000", "541 000", "598 000", "632 000", "658 000"],
            ["Autres revenus (spa, s\u00e9minaire)", "188 000", "221 000", "246 000", "264 000", "280 000"],
            ["Marge brute d'exploitation", "1 020 000", "1 258 000", "1 434 000", "1 538 000", "1 610 000"],
        ],
        footer=["EBITDAR retenu", "1 020 000", "1 258 000", "1 434 000", "1 538 000", "1 610 000"],
        aligns=["left", "num", "num", "num", "num", "num"],
        col_ratios=[2.4, 1, 1, 1, 1, 1])

    # 8 - Glossaire
    doc.page_break()
    doc.section_title("Glossaire")
    doc.glossary([
        {"term": "Offre", "definition": "capacit\u00e9 en nombre de chambres."},
        {"term": "Taux d'occupation (TO)", "definition": "chambres vendues / chambres disponibles."},
        {"term": "Prix moyen (PM)", "definition": "chiffre d'affaires h\u00e9bergement / chambres vendues (HT)."},
        {"term": "RevPAR", "definition": "taux d'occupation \u00d7 prix moyen ; ou CA h\u00e9bergement / chambres disponibles (HT)."},
    ])

    # 9 - Page de fin
    doc.add_end(
        eyebrow="MKG Consulting",
        fields=[
            ("Contact", "Sylvie Bergeret \u2014 Directrice \u00b7 MRICS"),
            ("Courriel", "s.bergeret@mkg-consulting.com"),
            ("Web", "www.mkg-consulting.com"),
        ],
        confidential="Document confidentiel \u00b7 Usage exclusif Turenne H\u00f4tellerie",
        date="Novembre 2025")

    return doc.save(out)
