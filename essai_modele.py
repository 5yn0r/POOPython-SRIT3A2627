"""Premier essai autonome après avoir créé le fichier modele.py."""

from decimal import Decimal
from modele import Auteur, Bibliotheque, Document, Editeur, Livre, Ouvrage, Revue

# Construire les objets puis leurs relations, avec des données fictives.
editeur = Editeur("Éditions Exemple", ville="Abidjan")
auteur = Auteur("Awa Koné")
livre = Livre("Python pratique", Decimal("12000"), editeur, (auteur,))
premier = livre.ajouter_exemplaire("neuf")
second = livre.ajouter_exemplaire("abime")
revue = Revue("Sciences numériques", "mensuelle")
numero = revue.ajouter_numero(1, "Découvrir Python")

# Ces assertions servent à apprendre; les règles métier sont dans modele.py.
assert isinstance(livre, Ouvrage) and isinstance(revue, Ouvrage)
assert isinstance(premier, Document) and isinstance(numero, Document)
assert livre.editeur is editeur and auteur in livre.auteurs
assert livre.prix_unitaire == Decimal("12000")
assert len({premier.code, second.code, numero.code}) == 3

print("1. Création réussie : 1 livre, 2 exemplaires, 1 revue, 1 numéro.")
for ouvrage in (livre, revue):
    print(ouvrage.description())

# Vérifier un prêt, puis un refus qui protège l'exemplaire emprunté.
premier.emprunter()
assert premier.emprunte and not premier.disponible
print("2. Emprunt : le premier exemplaire devient indisponible.")

try:
    premier.detruire()
except ValueError as erreur:
    print(f"3. Destruction refusée : {erreur}")
else:
    raise AssertionError("Un exemplaire emprunté ne doit pas être détruit.")
assert premier.etat == "neuf" and premier.emprunte

premier.rendre()
assert premier.disponible and not premier.emprunte
print("4. Retour : le premier exemplaire redevient disponible.")

second.reparer()
assert second.etat == "bon" and second.disponible
print("5. Réparation : le second exemplaire passe de abime à bon.")

second.detruire()
assert second.etat == "detruit" and not second.disponible
print("6. Destruction : le second exemplaire est détruit et indisponible.")
print("Toutes les vérifications pédagogiques ont réussi.")