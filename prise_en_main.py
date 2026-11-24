"""Premier parcours guidé : objets, relations, états, fichiers et contrôles."""
from pathlib import Path
from tempfile import TemporaryDirectory

from modele import Auteur, Bibliotheque, Document, Editeur, Livre, Ouvrage, Revue
from stockage import charger, sauvegarder


def main():
    # 1. Construire un catalogue avec un éditeur, un auteur et un livre.
    bibliotheque = Bibliotheque()
    editeur = bibliotheque.ajouter_editeur(Editeur("Éditions Campus", ville="Abidjan"))
    auteur = bibliotheque.ajouter_auteur(Auteur("Awa Koné"))
    livre = bibliotheque.ajouter_livre(
        Livre("Python pour débuter", "12500", editeur, (auteur,))
    )
    print(livre)
    print("Même livre chez l'auteur :", auteur.livres[0] is livre)
    assert livre.editeur is editeur
    assert auteur.livres[0] is livre

    # 2. Créer deux exemplaires rattachés au même titre.
    premier = livre.ajouter_exemplaire()
    second = livre.ajouter_exemplaire("abime")
    assert premier.livre is second.livre
    assert premier.code != second.code
    print("Deux exemplaires, un titre :", len(livre.exemplaires), livre.titre)

    # 3. Observer les changements d'état contrôlés.
    premier.emprunter()
    print("Disponible après prêt :", premier.disponible)
    premier.rendre()
    second.reparer()
    print("Après retour et réparation :", premier.disponible, second.disponible)
    assert premier.disponible and second.disponible

    try:
        livre.prix_unitaire = "-100"
    except ValueError as erreur:
        print("Prix refusé :", erreur)
    assert livre.prix_unitaire == 12500

    # 4. Séparer une revue de ses numéros et vérifier les héritages.
    revue = bibliotheque.ajouter_revue(Revue("Science au campus", "mensuelle"))
    numero = revue.ajouter_numero(1, "Python et programmation")
    assert isinstance(livre, Ouvrage)
    assert not isinstance(livre, Document)
    assert isinstance(numero, Document)
    assert not isinstance(numero, Revue)
    for ouvrage in (livre, revue):
        print(ouvrage.description())
    for document in bibliotheque.documents():
        print(document.description())

    # 5. Sauvegarder puis relire sans toucher aux données du menu.
    with TemporaryDirectory() as dossier:
        fichier = Path(dossier) / "essai.json"
        sauvegarder(bibliotheque, fichier)
        copie = charger(fichier)
        assert len(copie.documents()) == 3
        assert copie.livres[0].exemplaires[0].code == premier.code
        print("Rechargement vérifié : 1 livre, 1 revue, 3 documents.")

    print("Parcours terminé : toutes les vérifications ont réussi.")


if __name__ == "__main__":
    main()