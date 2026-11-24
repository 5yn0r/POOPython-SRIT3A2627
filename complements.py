"""Compléments du cours. Lancer : python complements.py.
Exemples fictifs en mémoire ; aucun fichier n'est créé ou modifié.
"""
import keyword

from modele import Editeur, Livre, Ouvrage


def statistiques(valeurs):
    """Renvoie (minimum, maximum, moyenne) pour des entiers non vides."""
    if not isinstance(valeurs, (list, tuple)):
        raise TypeError("Une liste ou un tuple d'entiers est attendu.")
    if not valeurs:
        raise ValueError("Impossible de calculer sur une collection vide.")
    if any(type(valeur) is not int for valeur in valeurs):
        raise TypeError("Chaque valeur doit être un entier, hors booléen.")
    return min(valeurs), max(valeurs), sum(valeurs) / len(valeurs)


class Selection:
    """Une sélection possède sa propre liste interne de codes positifs."""

    def __init__(self, codes=None):
        self.__codes = []
        if codes is not None:
            for code in codes:
                self.ajouter(code)

    def ajouter(self, code):
        if type(code) is not int or code < 1:
            raise ValueError("Un code entier strictement positif est attendu.")
        self.__codes.append(code)

    @property
    def codes(self):
        return tuple(self.__codes)

    def __len__(self):
        return len(self.__codes)


def schemas_boucles():
    """Comparer les schémas élémentaires avec les fonctions intégrées."""
    prix = [1500, 2000, 2500]
    total, nombre, maximum, trouve = 0, 0, prix[0], False
    for valeur in prix:
        total += valeur
        nombre += 1
        if valeur > maximum:
            maximum = valeur
        if valeur == 2000:
            trouve = True
    produit = 1
    for facteur in [1, 2, 3]:
        produit *= facteur
    print("Boucles :", total, nombre, maximum, trouve, produit)


def main():
    print("Pas négatif :", list(range(6, 0, -2)))
    mini, maxi, moyenne = statistiques([1500, 2000, 2500])
    print("Statistiques :", mini, maxi, moyenne)
    print("Moyenne : {:.2f} FCFA".format(moyenne))
    schemas_boucles()

    premiere, seconde = Selection(), Selection()
    premiere.ajouter(7)
    print("Indépendance :", premiere.codes, seconde.codes)
    print("Longueurs :", len(premiere), len(seconde))

    origine = [1, 2]
    selection = Selection(origine)
    origine.append(3)
    print("Liste reçue copiée :", selection.codes, origine)

    livre = Livre("Python", 1500, Editeur("Éditeur fictif"))
    print("Objet et héritage :", isinstance(livre, Ouvrage), issubclass(Livre, Ouvrage))
    print("Mots réservés :", keyword.iskeyword("class"), keyword.iskeyword("livre"))
    print("Booléen et entier :", isinstance(True, int), type(True) is int)

    try:
        statistiques([])
    except ValueError as erreur:
        print("ValueError attendue :", erreur)
    try:
        {"titre": "Python"}["auteur"]
    except KeyError:
        print("KeyError attendue : la clé auteur est absente.")
    try:
        print(selection.__codes)
    except AttributeError:
        print("AttributeError attendue : __codes est renommé par Python.")
    print("Le renommage __codes ne constitue pas une protection de confidentialité.")


if __name__ == "__main__":
    main()