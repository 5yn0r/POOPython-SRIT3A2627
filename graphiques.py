"""Statistiques et graphiques calculés à partir des objets de la bibliothèque."""
from decimal import Decimal
from pathlib import Path
from textwrap import fill


def calculer_indicateurs(bibliotheque):
    """Renvoyer des données simples ; aucun graphique n'est créé ici."""
    exemplaires = [e for livre in bibliotheque.livres for e in livre.exemplaires]
    etats = {nom: 0 for nom in ("neuf", "bon", "abime", "detruit")}
    for exemplaire in exemplaires:
        etats[exemplaire.etat] += 1
    disponibles = sum(e.disponible for e in exemplaires)
    empruntes = sum(
        e.etat in ("neuf", "bon") and not e.disponible for e in exemplaires
    )
    valeurs = [
        livre.prix_unitaire * sum(e.etat != "detruit" for e in livre.exemplaires)
        for livre in bibliotheque.livres
    ]
    return {
        "titres_livres": len(bibliotheque.livres),
        "titres_revues": len(bibliotheque.revues),
        "numeros_revues": sum(len(r.numeros) for r in bibliotheque.revues),
        "exemplaires": len(exemplaires),
        "etats": etats,
        "disponibles": disponibles,
        "empruntes": empruntes,
        "indisponibles_etat": etats["abime"] + etats["detruit"],
        "titres": [livre.titre for livre in bibliotheque.livres],
        "valeurs": valeurs,
        "valeur_totale": sum(valeurs, Decimal("0")),
    }


def generer_graphiques(bibliotheque, dossier):
    """Exporter un tableau de bord et quatre PNG, sans fenêtre graphique."""
    import matplotlib
    matplotlib.use("Agg")  # Fonctionne aussi sur un ordinateur sans affichage.
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator, StrMethodFormatter

    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    donnees = calculer_indicateurs(bibliotheque)
    couleurs = ("#24577A", "#2A887F", "#D19737", "#AA5555")

    def barres(ax, libelles, valeurs, titre, unite, couleurs_barres):
        positions = range(len(libelles))
        rectangles = ax.bar(positions, valeurs, color=couleurs_barres, width=0.62)
        ax.set_xticks(list(positions), libelles)
        ax.set_title(titre, fontsize=12, loc="left", pad=16, fontweight="bold")
        ax.set_ylabel(unite)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        ax.set_ylim(0, max(valeurs, default=0) * 1.25 or 1)
        ax.bar_label(rectangles, fmt="%.0f", padding=5, fontsize=10)
        ax.grid(axis="y", alpha=0.18)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)

    def dessiner(ax, numero):
        if numero == 0:
            barres(ax, ["Livres", "Revues"],
                   [donnees["titres_livres"], donnees["titres_revues"]],
                   "Titres du catalogue", "Nombre de titres", couleurs[:2])
        elif numero == 1:
            barres(ax, ["Neuf", "Bon", "Abîmé", "Détruit"],
                   list(donnees["etats"].values()),
                   "État physique des exemplaires", "Nombre d'exemplaires", couleurs)
        elif numero == 2:
            barres(ax, ["Disponibles", "Empruntés", "Abîmés ou\ndétruits"],
                   [donnees["disponibles"], donnees["empruntes"],
                    donnees["indisponibles_etat"]],
                   "Disponibilité des exemplaires", "Nombre d'exemplaires",
                   couleurs[:3])
        else:
            # 12 titres maximum pour conserver un graphique lisible.
            couples = sorted(zip(donnees["titres"], donnees["valeurs"]),
                             key=lambda couple: couple[1], reverse=True)[:12]
            libelles = [fill(titre[:45], 18) for titre, _ in couples]
            valeurs = [float(valeur) for _, valeur in couples]
            titre = "Valeur par livre hors exemplaires détruits"
            if len(donnees["titres"]) > 12:
                titre += "\nLes 12 valeurs les plus élevées"
            if not couples:
                ax.set_title(titre, loc="left", fontsize=12)
                ax.text(0.5, 0.5, "Aucun livre", ha="center", transform=ax.transAxes)
                ax.set_axis_off()
            else:
                barres(ax, libelles, valeurs, titre, "FCFA", couleurs[0])

    chemins = []
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 10}):
        fig, axes = plt.subplots(2, 2, figsize=(14, 10), layout="constrained")
        try:
            for numero, axe in enumerate(axes.flat):
                dessiner(axe, numero)
            fig.suptitle("Bibliothèque pédagogique", fontsize=20, fontweight="bold")
            chemin = dossier / "tableau_de_bord.png"
            fig.savefig(chemin, dpi=180, facecolor="white")
            chemins.append(chemin)
        finally:
            plt.close(fig)

        noms = ("catalogue", "etats", "disponibilite", "valeur")
        for numero, nom in enumerate(noms):
            fig, axe = plt.subplots(figsize=(9, 6), layout="constrained")
            try:
                dessiner(axe, numero)
                chemin = dossier / f"{nom}.png"
                fig.savefig(chemin, dpi=180, facecolor="white")
                chemins.append(chemin)
            finally:
                plt.close(fig)
    return chemins