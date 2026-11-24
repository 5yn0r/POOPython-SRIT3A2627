"""Modèle métier du projet de bibliothèque, compatible Python 3.10+.
Les prix sont des montants entiers en FCFA. Les données d'exemple sont fictives.
Un catalogue rechargé conserve ses codes; les nouvelles allocations avancent.
Les attributs précédés de _ sont internes, sans constituer une barrière de sécurité.
"""
from decimal import Decimal, InvalidOperation


def valider_texte(valeur, champ, maximum=200, vide=False):
    """Valider un texte avant de l'afficher ou de le conserver."""
    if not isinstance(valeur, str):
        raise TypeError(f"{champ} doit être un texte.")
    if any(not caractere.isprintable() for caractere in valeur):
        raise ValueError(f"{champ} contient un caractère de contrôle.")
    valeur = valeur.strip()
    if (not valeur and not vide) or len(valeur) > maximum:
        raise ValueError(f"{champ} doit contenir de 1 à {maximum} caractères.")
    return valeur


def valider_entier(valeur, champ, maximum=1_000_000_000):
    # bool est une sous-classe de int: le test exact exclut True et False.
    if (type(valeur) is not int or valeur < 1
            or (maximum is not None and valeur > maximum)):
        borne = f" entre 1 et {maximum}" if maximum is not None else " positif"
        raise ValueError(f"{champ} doit être un entier{borne}.")
    return valeur

#Ajout de notre fonction titre en prêt

def livre_emprunt(bibliotheque, auteur):
    for livre in bibliotheque.livres:
        if auteur in livre.auteurs and any(e.emprunte for e in livre.examplaires):
            yield livre

def titres_en_pret(bibliotheque: Bibliotheque, auteur: Auteur) -> list[str]:
    titres= {livre.titre for livre in livre_emprunt(bibliotheque, auteur)}
    return sorted(titres)
#Fin de notre fonction titre en prêt


class Editeur:
    def __init__(self, nom, adresse="", ville=""):
        self._nom = valider_texte(nom, "Le nom de l'éditeur", 150)
        self._adresse = valider_texte(adresse, "L'adresse", 250, vide=True)
        self._ville = valider_texte(ville, "La ville", 100, vide=True)
        self._livres = []

    def __str__(self):
        return self.nom

    @property
    def nom(self):
        return self._nom

    @property
    def adresse(self):
        return self._adresse

    @property
    def ville(self):
        return self._ville

    @property
    def livres(self):
        return tuple(self._livres)


class Auteur:
    def __init__(self, nom):
        self._nom = valider_texte(nom, "Le nom de l'auteur", 150)
        self._livres = []

    def __str__(self):
        return self.nom

    @property
    def nom(self):
        return self._nom

    @property
    def livres(self):
        return tuple(self._livres)


class Ouvrage:
    """Un titre intellectuel, distinct de ses documents physiques."""

    def __init__(self, titre):
        self._titre = valider_texte(titre, "Le titre")

    @property
    def titre(self):
        return self._titre

    def description(self):
        return self.titre

    def __str__(self):
        return self.description()


class Document:
    """Ancêtre commun des exemplaires et des numéros de revue."""

    _prochain_code = 1  # Un compteur commun, pas un compteur par sous-classe.

    def __init__(self):
        self._code = Document.reserver_code()

    @classmethod
    def reserver_code(cls):
        code = valider_entier(Document._prochain_code, "Le prochain code", maximum=None)
        Document._prochain_code += 1
        return code

    def _restaurer_code(self, code):
        # Réservé au chargeur qui a vérifié l'unicité dans le catalogue.
        self._code = valider_entier(code, "Le code", maximum=None)
        Document._prochain_code = max(Document._prochain_code, code + 1)

    @property
    def code(self):
        return self._code

    def get_code(self):
        return self.code

    def description(self):
        return f"Document {self.code}"

    def __str__(self):
        return self.description()


class Livre(Ouvrage):
    def __init__(self, titre, prix, editeur, auteurs=()):
        super().__init__(titre)
        self._prix_unitaire = self.valider_prix(prix)
        if not isinstance(editeur, Editeur):
            raise TypeError("Un livre doit avoir un éditeur.")
        auteurs = tuple(auteurs)
        if any(not isinstance(auteur, Auteur) for auteur in auteurs):
            raise TypeError("Chaque auteur doit être un objet Auteur.")
        self._editeur = editeur
        self._auteurs = []
        self._exemplaires = []
        editeur._livres.append(self)
        for auteur in auteurs:
            self.ajouter_auteur(auteur)

    @staticmethod
    def valider_prix(prix):
        """Decimal évite les approximations binaires; les FCFA sont entiers."""
        if isinstance(prix, bool) or not isinstance(prix, (str, int, Decimal)):
            raise TypeError("Le prix doit être un texte, un entier ou Decimal.")
        if len(str(prix)) > 60:
            raise ValueError("Le prix est trop long.")
        try:
            montant = Decimal(str(prix))
            if (not montant.is_finite() or montant < 0
                    or montant > 1_000_000_000
                    or montant != montant.to_integral_value()):
                raise ValueError(
                    "Le prix doit être entier, entre 0 et 1 milliard de FCFA."
                )
            return montant.quantize(Decimal("1"))
        except InvalidOperation as erreur:
            raise ValueError("Le prix est invalide.") from erreur

    @property
    def prix_unitaire(self):
        return self._prix_unitaire

    @prix_unitaire.setter
    def prix_unitaire(self, prix):
        self._prix_unitaire = self.valider_prix(prix)

    @property
    def editeur(self):
        return self._editeur

    @property
    def auteurs(self):
        return tuple(self._auteurs)

    @property
    def exemplaires(self):
        return tuple(self._exemplaires)

    def get_livre(self):
        return self  # Méthode conservée pour correspondre au sujet.

    def set_prix_unitaire(self, prix):
        self.prix_unitaire = prix

    def ajouter_auteur(self, auteur):
        if not isinstance(auteur, Auteur):
            raise TypeError("Un objet Auteur est attendu.")
        if auteur not in self._auteurs:
            self._auteurs.append(auteur)
            auteur._livres.append(self)
        return auteur

    def ajouter_exemplaire(self, etat="neuf"):
        return Exemplaire(self, etat)

    def description(self):
        return f"Livre : {self.titre} - {self.prix_unitaire} FCFA"


class Revue(Ouvrage):
    def __init__(self, titre, periodicite):
        super().__init__(titre)
        self._periodicite = valider_texte(periodicite, "La périodicité", 100)
        self._numeros = []

    @property
    def periodicite(self):
        return self._periodicite

    @property
    def numeros(self):
        return tuple(self._numeros)

    def ajouter_numero(self, numero, sommaire=""):
        return NumeroRevue(self, numero, sommaire)

    def description(self):
        return f"Revue : {self.titre} - {self.periodicite}"


class Exemplaire(Document):
    ETATS = ("neuf", "bon", "abime", "detruit")

    def __init__(self, livre, etat="neuf"):
        if not isinstance(livre, Livre):
            raise TypeError("Un exemplaire appartient à un Livre.")
        if etat not in self.ETATS:
            raise ValueError("État inconnu.")
        super().__init__()
        self._livre = livre
        self._etat = etat
        self._emprunte = False
        livre._exemplaires.append(self)

    @property
    def livre(self):
        return self._livre

    @property
    def etat(self):
        return self._etat

    @property
    def emprunte(self):
        return self._emprunte

    @property
    def disponible(self):
        return self.etat in ("neuf", "bon") and not self.emprunte

    def emprunter(self):
        if not self.disponible:
            raise ValueError("Cet exemplaire n'est pas disponible.")
        self._emprunte = True

    def rendre(self):
        if not self.emprunte:
            raise ValueError("Cet exemplaire n'est pas emprunté.")
        self._emprunte = False

    def set_etat_exemplaire(self, etat):
        if etat not in self.ETATS:
            raise ValueError("État inconnu.")
        if self.etat == "detruit":
            raise ValueError("La destruction est irréversible.")
        if self.emprunte:
            raise ValueError("Rendre l'exemplaire avant de modifier son état.")
        self._etat = etat

    def reparer(self):
        if self.etat != "abime":
            raise ValueError("Seul un exemplaire abîmé peut être réparé.")
        self.set_etat_exemplaire("bon")

    def detruire(self):
        self.set_etat_exemplaire("detruit")

    def get_disponible(self):
        return self.disponible

    def get_etat_exemplaire(self):
        return self.etat

    def set_disponible(self, disponible):
        if type(disponible) is not bool:
            raise TypeError("La disponibilité doit être un booléen.")
        if disponible:
            if self.emprunte:
                self.rendre()
            elif not self.disponible:
                raise ValueError("Réparer l'exemplaire avant de le rendre disponible.")
        elif self.disponible:
            self.emprunter()

    def description(self):
        statut = "disponible" if self.disponible else "indisponible"
        return f"Exemplaire {self.code} : {self.livre.titre} - {self.etat}, {statut}"


class NumeroRevue(Document):
    def __init__(self, revue, numero, sommaire=""):
        if not isinstance(revue, Revue):
            raise TypeError("Un numéro appartient à une Revue.")
        numero = valider_entier(numero, "Le numéro de revue")
        if any(existant.numero == numero for existant in revue.numeros):
            raise ValueError("Ce numéro existe déjà pour cette revue.")
        sommaire = valider_texte(sommaire, "Le sommaire", 2000, vide=True)
        super().__init__()
        self._revue = revue
        self._numero = numero
        self._sommaire = sommaire
        revue._numeros.append(self)

    @property
    def revue(self):
        return self._revue

    @property
    def numero(self):
        return self._numero

    @property
    def sommaire(self):
        return self._sommaire

    def description(self):
        return f"Numéro {self.numero} de {self.revue.titre} - code {self.code}"


class Bibliotheque:
    """Extension du sujet: rassemble les objets d'un catalogue local."""

    def __init__(self):
        self._editeurs, self._auteurs = [], []
        self._livres, self._revues = [], []
    
    #_adama attribut protegé
    #__adama attribut privé
    #adama attribut public
    #__init__


    @property
    def editeurs(self):
        return tuple(dict.fromkeys(self._editeurs + [l.editeur for l in self.livres]))

    @property
    def auteurs(self):
        lies = [a for livre in self.livres for a in livre.auteurs]
        return tuple(dict.fromkeys(self._auteurs + lies))

    @property
    def livres(self):
        return tuple(self._livres)

    @property
    def revues(self):
        return tuple(self._revues)

    def _ajouter(self, objet, classe, collection):
        if not isinstance(objet, classe):
            raise TypeError(f"Un objet {classe.__name__} est attendu.")
        if objet not in collection:
            nouveaux = ()
            if isinstance(objet, Livre):
                nouveaux = objet.exemplaires
            elif isinstance(objet, Revue):
                nouveaux = objet.numeros
            codes = {d.code for d in self.documents()}
            if any(d.code in codes for d in nouveaux):
                raise ValueError("Un code document existe déjà dans ce catalogue.")
            collection.append(objet)
        return objet

    def ajouter_editeur(self, editeur):
        return self._ajouter(editeur, Editeur, self._editeurs)

    def ajouter_auteur(self, auteur):
        return self._ajouter(auteur, Auteur, self._auteurs)

    def ajouter_livre(self, livre):
        return self._ajouter(livre, Livre, self._livres)

    def ajouter_revue(self, revue):
        return self._ajouter(revue, Revue, self._revues)

    def rechercher_livres(self, texte):
        terme = valider_texte(texte, "La recherche").casefold()
        return [livre for livre in self.livres if terme in livre.titre.casefold()]

    def documents(self):
        copies = [e for livre in self.livres for e in livre.exemplaires]
        numeros = [n for revue in self.revues for n in revue.numeros]
        return tuple(copies + numeros)

    @classmethod
    def demo(cls):
        """Construire un jeu pédagogique fictif reproductible."""
        b = cls()
        e1 = b.ajouter_editeur(Editeur("ESATIC Press", ville="Abidjan"))
        e2 = b.ajouter_editeur(Editeur("Savoir Afrique", ville="Grand-Bassam"))
        a1, a2, a3 = (Auteur(n) for n in ("Awa Koné", "Yao Kouassi", "Binta Touré"))
        donnees = [
            ("Python pratique", 12000, e1, (a1, a2), ("neuf", "bon", "abime")),
            ("Réseaux IP", 18000, e1, (a2,), ("neuf", "bon", "bon")),
            ("Algorithmique", 15000, e2, (a1, a3), ("bon", "detruit")),
            ("Sécurité numérique", 20000, e2, (a3,), ("neuf", "abime")),
        ]
        for titre, prix, editeur, auteurs, etats in donnees:
            livre = b.ajouter_livre(Livre(titre, prix, editeur, auteurs))
            for etat in etats:
                livre.ajouter_exemplaire(etat)
        b.livres[0].exemplaires[1].emprunter()
        b.livres[1].exemplaires[2].emprunter()
        r1 = b.ajouter_revue(Revue("Science et numérique", "mensuelle"))
        r2 = b.ajouter_revue(Revue("Réseaux et société", "trimestrielle"))
        r1.ajouter_numero(1, "Python et données")
        r1.ajouter_numero(2, "Objets et bibliothèques")
        r2.ajouter_numero(1, "Connectivité et sécurité")
        return b

# Opération 02 : valeur des exemplaires en prêt
def valeur_en_pret(bibliotheque, auteur):
    """Somme en FCFA des prix des exemplaires empruntés des livres de cet auteur.

    Chaque exemplaire emprunté compte une fois : deux exemplaires empruntés
    du même livre comptent donc deux fois. Renvoie Decimal("0") si aucun.
    """
    # Sécurité : refuser tout objet qui n'est pas du bon type.
    if not isinstance(bibliotheque, Bibliotheque):
        raise TypeError("Un objet Bibliotheque est attendu.")
    if not isinstance(auteur, Auteur):
        raise TypeError("Un objet Auteur est attendu.")

    total = Decimal("0")  # Decimal : pas d'erreur d'arrondi sur les montants.
    for livre in bibliotheque.livres:
        if auteur not in livre.auteurs:  # Comparaison par objet, pas par nom.
            continue
        for exemplaire in livre.exemplaires:
            if exemplaire.emprunte:
                total += livre.prix_unitaire
    return total
