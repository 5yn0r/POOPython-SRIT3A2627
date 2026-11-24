"""Sauvegarde JSON locale: validation stricte et remplacement atomique.
Ce module vise un poste de travail avec un seul utilisateur à la fois.
Il ne chiffre pas les fichiers et ne fournit pas d'authentification.
"""
import json
import os
import tempfile
from pathlib import Path

from modele import Auteur, Bibliotheque, Document, Editeur, Livre, Revue, valider_entier

MAX_OCTETS = 2 * 1024 * 1024


class ErreurStockage(ValueError):
    """Le fichier manque, est illisible ou ne respecte pas le format attendu."""


def _objet(valeur, champs):
    if type(valeur) is not dict or set(valeur) != set(champs.split()):
        raise ValueError("Structure JSON ou liste de champs incorrecte.")
    return valeur


def _liste(valeur):
    if type(valeur) is not list or len(valeur) > 10000:
        raise ValueError("Une liste de 10000 éléments au maximum est attendue.")
    return valeur


def _sans_doublon(paires):
    resultat = {}
    for cle, valeur in paires:
        if cle in resultat:
            raise ValueError("Une clé JSON est répétée.")
        resultat[cle] = valeur
    return resultat


def _ajouter_id(table, identifiant, objet):
    valider_entier(identifiant, "L'identifiant")
    if identifiant in table:
        raise ValueError("Un identifiant est répété dans une table.")
    table[identifiant] = objet


def _reference(table, identifiant):
    valider_entier(identifiant, "La référence")
    if identifiant not in table:
        raise ValueError("Une référence désigne un objet absent.")
    return table[identifiant]


def _decoder(data):
    _objet(data, "version editeurs auteurs livres revues")
    if type(data["version"]) is not int or data["version"] != 1:
        raise ValueError("Version de sauvegarde non prise en charge.")
    b = Bibliotheque()
    editeurs, auteurs, livres, revues, codes = {}, {}, {}, {}, set()

    for d in _liste(data["editeurs"]):
        _objet(d, "id nom adresse ville")
        e = b.ajouter_editeur(Editeur(d["nom"], d["adresse"], d["ville"]))
        _ajouter_id(editeurs, d["id"], e)

    for d in _liste(data["auteurs"]):
        _objet(d, "id nom")
        _ajouter_id(auteurs, d["id"], b.ajouter_auteur(Auteur(d["nom"])))

    def restaurer_code(document, code):
        valider_entier(code, "Le code document", maximum=None)
        if code in codes:
            raise ValueError("Deux documents portent le même code.")
        codes.add(code)
        document._restaurer_code(code)

    for d in _liste(data["livres"]):
        _objet(d, "id titre prix editeur auteurs exemplaires")
        if not isinstance(d["prix"], str):
            raise ValueError("Le prix JSON doit être une chaîne décimale.")
        refs = _liste(d["auteurs"])
        objets_auteurs = [_reference(auteurs, ref) for ref in refs]
        if len(set(refs)) != len(refs):
            raise ValueError("Le même auteur est cité deux fois pour un livre.")
        livre = Livre(d["titre"], d["prix"], _reference(editeurs, d["editeur"]),
                      objets_auteurs)
        _ajouter_id(livres, d["id"], b.ajouter_livre(livre))
        for item in _liste(d["exemplaires"]):
            _objet(item, "code etat emprunte")
            if type(item["emprunte"]) is not bool:
                raise ValueError("Le statut d'emprunt doit être un booléen.")
            ex = livre.ajouter_exemplaire(item["etat"])
            if item["emprunte"]:
                ex.emprunter()  # Refuse aussi l'emprunt d'un objet abîmé ou détruit.
            restaurer_code(ex, item["code"])

    for d in _liste(data["revues"]):
        _objet(d, "id titre periodicite numeros")
        revue = b.ajouter_revue(Revue(d["titre"], d["periodicite"]))
        _ajouter_id(revues, d["id"], revue)
        for item in _liste(d["numeros"]):
            _objet(item, "code numero sommaire")
            numero = revue.ajouter_numero(item["numero"], item["sommaire"])
            restaurer_code(numero, item["code"])
    return b


def _encoder(b):
    if not isinstance(b, Bibliotheque):
        raise TypeError("Un objet Bibliotheque est attendu.")
    codes = [d.code for d in b.documents()]
    if len(set(codes)) != len(codes):
        raise ValueError("Les codes document doivent être uniques dans le catalogue.")
    collections = [b.editeurs, b.auteurs, b.livres, b.revues]
    collections += [l.auteurs for l in b.livres] + [l.exemplaires for l in b.livres]
    collections += [r.numeros for r in b.revues]
    if any(len(collection) > 10000 for collection in collections):
        raise ValueError("Une collection dépasse la limite de 10000 éléments.")

    editeurs = {e: i for i, e in enumerate(b.editeurs, start=1)}
    auteurs = {a: i for i, a in enumerate(b.auteurs, start=1)}
    return {
        "version": 1,
        "editeurs": [{"id": i, "nom": e.nom, "adresse": e.adresse, "ville": e.ville}
                     for e, i in editeurs.items()],
        "auteurs": [{"id": i, "nom": a.nom} for a, i in auteurs.items()],
        "livres": [{"id": i, "titre": l.titre, "prix": str(l.prix_unitaire),
                    "editeur": editeurs[l.editeur],
                    "auteurs": [auteurs[a] for a in l.auteurs],
                    "exemplaires": [{"code": e.code, "etat": e.etat,
                                     "emprunte": e.emprunte} for e in l.exemplaires]}
                   for i, l in enumerate(b.livres, start=1)],
        "revues": [{"id": i, "titre": r.titre, "periodicite": r.periodicite,
                    "numeros": [{"code": n.code, "numero": n.numero,
                                 "sommaire": n.sommaire} for n in r.numeros]}
                   for i, r in enumerate(b.revues, start=1)],
    }


def charger(chemin):
    """Charger sans modifier le fichier, même s'il est incorrect."""
    ancien_compteur = Document._prochain_code
    try:
        chemin = Path(chemin)
        if chemin.is_symlink() or not chemin.is_file():
            raise ValueError(
                "Un fichier régulier existant est attendu, sans lien symbolique."
            )
        with chemin.open("rb") as fichier:
            contenu = fichier.read(MAX_OCTETS + 1)
        if len(contenu) > MAX_OCTETS:
            raise ValueError("Le fichier dépasse la limite de 2 Mio.")
        data = json.loads(contenu.decode("utf-8"), object_pairs_hook=_sans_doublon)
        return _decoder(data)
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError) as erreur:
        Document._prochain_code = ancien_compteur
        raise ErreurStockage(f"Chargement impossible : {erreur}") from erreur


def sauvegarder(bibliotheque, chemin):
    """Remplacer la sauvegarde seulement après une écriture complète réussie."""
    temporaire = None
    try:
        chemin = Path(chemin)
        if chemin.is_symlink():
            raise ValueError("Les liens symboliques ne sont pas acceptés.")
        contenu = json.dumps(_encoder(bibliotheque), ensure_ascii=False, indent=2,
                             allow_nan=False).encode("utf-8")
        if len(contenu) > MAX_OCTETS:
            raise ValueError("Le catalogue dépasse la limite de 2 Mio.")
        chemin.parent.mkdir(parents=True, exist_ok=True)
        # Même répertoire pour rester sur le même système de fichiers.
        with tempfile.NamedTemporaryFile(dir=chemin.parent, prefix=".catalogue-",
                                         suffix=".tmp", delete=False) as fichier:
            temporaire = Path(fichier.name)
            fichier.write(contenu)
            fichier.flush()
            os.fsync(fichier.fileno())
        os.replace(temporaire, chemin)
    except (OSError, ValueError, TypeError) as erreur:
        raise ErreurStockage(f"Sauvegarde impossible : {erreur}") from erreur
    finally:
        if temporaire is not None and temporaire.exists():
            try:
                temporaire.unlink()
            except OSError:
                pass  # Une erreur de nettoyage ne masque pas l'erreur d'écriture.