"""Onze ateliers autonomes. Lancer : python ateliers.py (Python >= 3.10).
Données fictives, bibliothèque standard, aucun fichier utilisateur modifié.
Les fichiers d'exercice sont créés dans un dossier temporaire puis supprimés.
"""
from abc import ABC, abstractmethod
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
import math
import random as rd
import time

REFERENCE = "catalogue"


def annoncer(numero, titre):
    print(f"\nAtelier {numero:02d} | {titre}")


def atelier_01():
    annoncer(1, "Variables et calculs")
    titre, prix, disponible = "Python", 1500, True
    prix, quantite = prix + 500, 3
    taux = 100 * 2 / quantite
    print(type(titre).__name__, type(prix).__name__, type(taux).__name__)
    print(type(disponible).__name__, int("3"), float("2.5"), str(prix))
    print(f"{titre:<12}{prix:>8,d} FCFA | {taux:.2f} %")
    print("Code", f"{7:05d}", sep=" : ", end="\n")
    print("-" * 12, titre + " pratique")
    print("Rangement :", divmod(17, 5), 17 // 5, 17 % 5)
    print("Priorités :", 2 + 3 * 4, (2 + 3) * 4, 2 ** 3)
    x = 10
    x += 2
    x -= 1
    x *= 2
    x /= 4
    print("Opérateurs combinés :", x, abs(-5), round(taux, 1))
    a, b = 1, 2
    a, b = b, a
    print("Échange :", a, b, "| Booléens :", bool("False"), bool(""))
    print("Arrondi :", math.isclose(0.1 + 0.2, 0.3))


def atelier_02():
    annoncer(2, "Chaînes et tranches")
    brut = " Python pratique "
    titre = brut.strip()
    print(repr(brut), titre[0], titre[-1], titre[:6], titre[::2], titre[::-1])
    print(titre.upper(), titre.lower(), titre.capitalize(), titre.title())
    print("-".join(titre.split()), titre.replace("pratique", "facile"))
    print(titre.find("thon"), titre.count("t"), len(titre))
    print(titre.startswith("Py"), titre.endswith("que"), "Python" in titre)
    print("123".isdigit(), "ABC".isalpha(), " ".isspace(), ord("A"), chr(65))
    print("Lettres :", sum(1 for lettre in titre if lettre.isalpha()))
    print("Ordre :", "Zèbre" < "abeille", "Zèbre".lower() < "abeille")
    print("Citation :\t\"Python\"\nNouvelle ligne")


def atelier_03():
    annoncer(3, "Conditions et boucles")
    prix, disponible, etat = 2000, True, "bon"
    if 0 < prix <= 5000 and disponible and not etat == "detruit":
        print("Sélection possible")
    elif prix < 0 or etat != "bon":
        print("À contrôler")
    else:
        print("Hors sélection")
    for code in range(1, 5):
        if code == 2:
            continue
        if code == 4:
            break
        print("Code retenu :", code)
    essais = 0
    while essais < 2:
        essais += 1
    for code in [1, 2, 3]:
        if code == 99:
            break
    else:
        print("Code 99 absent | essais :", essais)
    for choix in ["l", "v", "?"]:
        match choix:
            case "l" | "v":
                print("Voir le catalogue")
            case _:
                print("Choix inconnu")


def atelier_04():
    annoncer(4, "Listes et références")
    codes = [1, 2, 3]
    alias, copie = codes, codes.copy()
    alias.append(4)
    copie[0] = 99
    print(codes, copie, alias is codes, copie is not codes)
    copie.insert(1, 8)
    copie.extend([7, 7])
    copie.remove(7)
    retire = copie.pop()
    del copie[0]
    copie[0:1] = [6, 5]
    print("Mutations :", copie, "retiré :", retire, copie.count(5), copie.index(5))
    print("Tri renvoie :", copie.sort())
    copie.reverse()
    print(copie, sorted(copie), codes[::2], codes[::-1], codes + [5], [0] * 3)
    imbriquee = [["Python", 1500]]
    autre = imbriquee.copy()
    autre[0][1] = 2000
    print("Copie superficielle :", imbriquee)
    copie.clear()
    print("Liste vide :", copie)
    for rang, code in enumerate(codes, start=1):
        print(rang, code, end=" | ")
    print()


def atelier_05():
    annoncer(5, "Collections et statistiques")
    prix = [1500, 2000, 2500]
    print(min(prix), max(prix), sum(prix), [p for p in prix if p >= 2000])
    matrice = [[1, 2], [3, 4]]
    print("Sommes :", [sum(ligne) for ligne in matrice])
    print("Transposée :", [[ligne[i] for ligne in matrice] for i in range(2)])
    total, libres = (5, 3)
    print((total, libres), (total,), tuple(prix), 2000 in prix)
    a, b = {"Ada", "Koffi"}, {"Koffi", "Aya"}
    print(sorted(a | b), sorted(a & b), sorted(a - b))
    ensemble = set()
    ensemble.add("Ada")
    ensemble.discard("absent")
    ensemble.remove("Ada")
    fiche = {"titre": "Python", "prix": 1500}
    fiche.update(prix=2000, rayon="A")
    print(list(fiche.keys()), list(fiche.values()), list(fiche.items()))
    print(fiche.get("auteur", "Inconnu"), "auteur" not in fiche)
    del fiche["rayon"]
    print("Retiré :", fiche.pop("prix"), fiche)
    compte = {}
    for etat in ["bon", "abime", "bon"]:
        compte[etat] = compte.get(etat, 0) + 1
    print("États :", compte)


def prix_total(prix: int, quantite: int = 1) -> int:
    """Renvoie un total en FCFA entiers pour des données déjà validées."""
    return prix * quantite


def somme_prix(*montants):
    return sum(montants)


def fiche_texte(**informations):
    return "; ".join(f"{cle}={valeur}" for cle, valeur in informations.items())


def atelier_06():
    annoncer(6, "Fonctions et portée")
    reference = REFERENCE
    reference = "sélection locale"
    print(reference, REFERENCE, prix_total(1500), prix_total(1500, quantite=2))
    print(somme_prix(1500, 2000), somme_prix())
    print(fiche_texte(titre="Python", prix=1500), prix_total.__doc__)
    livres = [("Réseaux", 2500), ("Python", 1500)]
    print(sorted(livres, key=lambda livre: livre[1], reverse=True))
    resultat = annoncer(6, "Une fonction sans return renvoie None")
    print("Valeur renvoyée :", resultat)


def compter(nombres, profondeur=0):
    """Compte les entiers de listes imbriquées; au plus 10 niveaux."""
    if type(profondeur) is not int or not 0 <= profondeur <= 10:
        raise ValueError("Profondeur maximale dépassée")
    if type(nombres) is int:
        return 1
    if not isinstance(nombres, list):
        raise TypeError("Attendu : entier ou liste d'entiers")
    return sum(compter(element, profondeur + 1) for element in nombres)


def atelier_07():
    annoncer(7, "Récursivité bornée")
    print("Documents :", compter([1, [2, 3], [], [4, [5]]]), compter([]))
    try:
        boucle = []
        boucle.append(boucle)
        compter(boucle)
    except ValueError as erreur:
        print("Refus attendu :", erreur)


def atelier_08():
    annoncer(8, "Modules standards")
    hasard = rd.Random(42)
    codes = [1, 2, 3]
    print(hasard.randint(1, 6), round(hasard.random(), 3), hasard.choice(codes))
    print("Prix simulé :", round(hasard.uniform(1000, 2000), 2))
    hasard.shuffle(codes)
    print(codes, math.sqrt(16), math.floor(3.7), math.ceil(3.2))
    print(math.pi, round(math.cos(math.pi), 2), math.factorial(5), math.gcd(12, 8))
    debut = date(2026, 11, 16)
    print("Retour fictif :", (debut + timedelta(days=14)).strftime("%d/%m/%Y"))
    instant = time.perf_counter()
    sum(range(1000))
    print("Durée mesurée positive ou nulle :", time.perf_counter() - instant >= 0)


def atelier_09():
    annoncer(9, "Fichiers temporaires UTF-8")
    with TemporaryDirectory(prefix="atelier_biblio_") as dossier:
        source, copie = Path(dossier) / "titres.txt", Path(dossier) / "copie.txt"
        with source.open("w", encoding="utf-8") as fichier:
            fichier.writelines(["Python\n", "Réseaux\n"])
        with source.open("a", encoding="utf-8") as fichier:
            fichier.write("Sécurité\n")
        with source.open("r", encoding="utf-8") as fichier:
            print("read :", repr(fichier.read()))
        with source.open(encoding="utf-8") as fichier:
            print("readline :", fichier.readline().strip())
            print("readlines restantes :", fichier.readlines())
        with (
            source.open(encoding="utf-8") as entree,
            copie.open("w", encoding="utf-8") as sortie,
        ):
            for ligne in entree:
                sortie.write(ligne.upper())
        print("Copie :", copie.read_text(encoding="utf-8").splitlines())


def atelier_10():
    annoncer(10, "Exceptions précises")
    for saisie in ["3", "-1", "trois"]:
        try:
            nombre = int(saisie)
            if nombre <= 0:
                raise ValueError("Le code doit être strictement positif")
        except ValueError as erreur:
            print("Refus :", erreur)
        else:
            print("Code accepté :", nombre)
        finally:
            print("Vérification terminée")


def atelier_11():
    annoncer(11, "POO complémentaire facultative")

    class Descriptible(ABC):
        @abstractmethod
        def decrire(self):
            raise NotImplementedError

    class EtiquetteMixin:
        def etiquette(self):
            return self.decrire().upper()

    class Fiche(EtiquetteMixin, Descriptible):
        def decrire(self):
            return "Livre Python"

    class ObjetExterne:
        def decrire(self):
            return "Archive indépendante"

    print(Fiche().etiquette(), isinstance(Fiche(), Descriptible))
    print("MRO :", [classe.__name__ for classe in Fiche.__mro__])
    for objet in [Fiche(), ObjetExterne()]:
        print(objet.decrire())  # Même méthode, avec ou sans héritage commun.
    try:
        Descriptible()
    except TypeError:
        print("Une classe abstraite ne peut pas être instanciée")


if __name__ == "__main__":
    for atelier in (
        atelier_01, atelier_02, atelier_03, atelier_04, atelier_05,
        atelier_06, atelier_07, atelier_08, atelier_09, atelier_10, atelier_11,
    ):
        atelier()