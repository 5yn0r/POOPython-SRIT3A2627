"""Menu local. Lancer : python application.py ou python application.py --demo."""
import argparse
from pathlib import Path

from modele import Auteur, Bibliotheque, Editeur, Exemplaire, Livre, Revue
from stockage import ErreurStockage, charger, sauvegarder
from graphiques import calculer_indicateurs, generer_graphiques

BASE = Path(__file__).resolve().parent
FICHIER = BASE / "donnees" / "catalogue.json"


def lire_entier(message, minimum=1, maximum=10000):
    """Recommencer une saisie invalide sans interpréter de code Python."""
    while True:
        texte = input(message).strip()
        if len(texte) > 10:
            print("Saisie trop longue.")
            continue
        try:
            nombre = int(texte)
        except ValueError:
            print("Saisissez un nombre entier.")
            continue
        if minimum <= nombre <= maximum:
            return nombre
        print(f"Valeur attendue : de {minimum} à {maximum}.")


def choisir(objets, nom):
    """Sélectionner un objet dans une collection non vide."""
    if not objets:
        raise ValueError(f"Aucun {nom} enregistré.")
    for position, objet in enumerate(objets, start=1):
        print(f"{position}. {objet}")
    position = lire_entier("Numéro de la ligne : ", 1, len(objets))
    return objets[position - 1]


def afficher(bibliotheque):
    print("\nCATALOGUE")
    for ouvrage in (*bibliotheque.livres, *bibliotheque.revues):
        print(ouvrage.description())  # Même appel, méthodes différentes.
    print("\nDOCUMENTS PHYSIQUES")
    for document in bibliotheque.documents():
        print(document.description())
    bilan = calculer_indicateurs(bibliotheque)
    print(f"Exemplaires : {bilan['exemplaires']}")
    print(f"Disponibles : {bilan['disponibles']} ; empruntés : {bilan['empruntes']}")
    print(f"Abîmés ou détruits : {bilan['indisponibles_etat']}")
    print(f"Valeur hors détruits : {bilan['valeur_totale']} FCFA")


def ajouter_livre(bibliotheque):
    if not bibliotheque.editeurs:
        raise ValueError("Créez d'abord un éditeur avec l'option 2.")
    titre = input("Titre du livre : ")
    prix = input("Prix en FCFA entiers : ")  # Garder str pour Decimal.
    editeur = choisir(bibliotheque.editeurs, "éditeur")
    auteurs = []
    if bibliotheque.auteurs:
        print("Auteur facultatif : 0 = aucun, 1 = choisir un auteur.")
        if lire_entier("Choix : ", 0, 1):
            auteurs.append(choisir(bibliotheque.auteurs, "auteur"))
    livre = Livre(titre, prix, editeur, auteurs)
    bibliotheque.ajouter_livre(livre)
    print("Livre ajouté. L'option 6 ajoute ses exemplaires.")


def agir_sur_exemplaire(bibliotheque):
    objets = [d for d in bibliotheque.documents() if isinstance(d, Exemplaire)]
    exemplaire = choisir(objets, "exemplaire")
    print("1 Emprunter | 2 Rendre | 3 Abîmer | 4 Réparer | 5 Détruire")
    match lire_entier("Action : ", 1, 5):
        case 1:
            exemplaire.emprunter()
        case 2:
            exemplaire.rendre()
        case 3:
            exemplaire.set_etat_exemplaire("abime")
        case 4:
            exemplaire.reparer()
        case 5:
            if input("Écrire DETRUIRE pour confirmer : ").strip() != "DETRUIRE":
                print("Action annulée.")
                return
            exemplaire.detruire()
    print(exemplaire.description())


def executer_action(choix, bibliotheque):
    """Exécuter une action ; renvoyer True si une sauvegarde est nécessaire."""
    match choix:
        case "1":
            afficher(bibliotheque)
        case "2":
            nom = input("Nom de l'éditeur : ")
            adresse = input("Adresse facultative : ")
            ville = input("Ville facultative : ")
            bibliotheque.ajouter_editeur(Editeur(nom, adresse, ville))
        case "3":
            bibliotheque.ajouter_auteur(Auteur(input("Nom de l'auteur : ")))
        case "4":
            ajouter_livre(bibliotheque)
        case "5":
            titre = input("Titre de la revue : ")
            periodicite = input("Périodicité (ex. mensuelle) : ")
            bibliotheque.ajouter_revue(Revue(titre, periodicite))
        case "6":
            livre = choisir(bibliotheque.livres, "livre")
            livre.ajouter_exemplaire()
        case "7":
            revue = choisir(bibliotheque.revues, "revue")
            numero = lire_entier("Numéro de la revue : ")
            revue.ajouter_numero(numero, input("Sommaire : "))
        case "8":
            agir_sur_exemplaire(bibliotheque)
        case "9":
            livre = choisir(bibliotheque.livres, "livre")
            livre.set_prix_unitaire(input("Nouveau prix en FCFA entiers : "))
        case "10":
            livres = bibliotheque.rechercher_livres(input("Titre recherché : "))
            for livre in livres:
                print(livre.description())
            print(f"{len(livres)} résultat(s).")
        case "11":
            for chemin in generer_graphiques(bibliotheque, BASE / "sorties"):
                print(chemin)
        case "12":
            pass  # La sauvegarde est effectuée par la boucle principale.
        case "13":
            livre = choisir(bibliotheque.livres, "livre")
            livre.ajouter_auteur(choisir(bibliotheque.auteurs, "auteur"))
        case _:
            print("Choix inconnu.")
            return False
    return choix in {"2", "3", "4", "5", "6", "7", "8", "9", "12", "13"}


def main():
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--demo", action="store_true", help="Démonstration fictive autonome"
    )
    arguments = analyseur.parse_args()

    if arguments.demo:
        bibliotheque = Bibliotheque.demo()
        afficher(bibliotheque)
        dossier = BASE / "sorties" / "demo"
        sauvegarder(bibliotheque, dossier / "catalogue_demo.json")
        for chemin in generer_graphiques(bibliotheque, dossier):
            print(chemin)
        return 0

    try:
        bibliotheque = charger(FICHIER) if FICHIER.exists() else Bibliotheque()
    except (ErreurStockage, OSError) as erreur:
        print(f"Chargement refusé : {erreur}")
        print("Le fichier existant est conservé. Corrigez-le ou restaurez une copie.")
        return 2

    while True:
        print("\n1 Afficher | 2 Éditeur | 3 Auteur | 4 Livre | 5 Revue")
        print("6 Exemplaire | 7 Numéro de revue | 8 État ou prêt | 9 Prix")
        print(
            "10 Rechercher | 11 Graphiques | 12 Sauvegarder "
            "| 13 Ajouter un auteur au livre"
        )
        print("0 Sauvegarder et quitter")
        try:
            choix = input("Choix : ").strip()
            if choix == "0":
                sauvegarder(bibliotheque, FICHIER)
                print("Catalogue sauvegardé. Au revoir.")
                break
            if executer_action(choix, bibliotheque):
                sauvegarder(bibliotheque, FICHIER)
                print("Catalogue sauvegardé.")
        except ErreurStockage as erreur:
            print(f"Sauvegarde impossible : {erreur}")
            print("Les modifications restent en mémoire. Gardez le programme ouvert.")
            print("Corrigez le problème puis utilisez l'option 12 pour réessayer.")
        except (ValueError, TypeError) as erreur:
            print(f"Opération refusée : {erreur}")
        except OSError as erreur:
            print(f"Écriture impossible : {erreur}")
            print("Gardez le programme ouvert ; l'option 12 permet de réessayer.")
        except ImportError:
            print("Installez Matplotlib : python -m pip install -r requirements.txt")
        except (EOFError, KeyboardInterrupt):
            print("\nInterruption. Les opérations déjà sauvegardées sont conservées.")
            break
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ErreurStockage, OSError, ImportError) as erreur:
        print(f"Exécution arrêtée : {erreur}")
        raise SystemExit(2)