"""Vérifier les contrats du projet : python -m unittest -v.
Chaque test crée ses propres objets et fichiers temporaires. La sauvegarde
personnelle de l'étudiant n'est jamais ouverte ni modifiée par cette suite.
"""
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import stockage
from modele import (
    Auteur, Bibliotheque, Document, Editeur, Exemplaire,
    Livre, NumeroRevue, Ouvrage, Revue,
)
from stockage import ErreurStockage, charger, sauvegarder


class TestBibliotheque(unittest.TestCase):
    """Tests métier et tests des entrées à la frontière du programme."""

    def setUp(self):
        self.dossier = tempfile.TemporaryDirectory()
        self.addCleanup(self.dossier.cleanup)
        self.chemin = Path(self.dossier.name) / "catalogue.json"
        self.editeur = Editeur("Éditions ESATIC", "Rue des écoles", "Abidjan")
        self.auteur = Auteur("Awa Koné")
        self.livre = Livre("Python pratique", "12000", self.editeur,
                           (self.auteur,))
        self.revue = Revue("Science Afrique", "mensuelle")
        self.bib = Bibliotheque()
        self.bib.ajouter_livre(self.livre)
        self.bib.ajouter_revue(self.revue)

    def lire_json(self):
        sauvegarder(self.bib, self.chemin)
        return json.loads(self.chemin.read_text(encoding="utf-8"))

    def ecrire_json(self, donnees):
        self.chemin.write_text(json.dumps(donnees), encoding="utf-8")

    def verifier_rejet(self, donnees):
        self.ecrire_json(donnees)
        avant = self.chemin.read_bytes()
        with self.assertRaises(ErreurStockage):
            charger(self.chemin)
        self.assertEqual(self.chemin.read_bytes(), avant)

    def test_01_heritages_du_sujet(self):
        self.assertTrue(issubclass(Livre, Ouvrage))
        self.assertTrue(issubclass(Revue, Ouvrage))
        self.assertTrue(issubclass(Exemplaire, Document))
        self.assertTrue(issubclass(NumeroRevue, Document))
        self.assertFalse(issubclass(Livre, Document))
        self.assertFalse(issubclass(NumeroRevue, Revue))

    def test_02_relations_inverses(self):
        autre = Livre("Réseaux", "8000", self.editeur, (self.auteur,))
        self.bib.ajouter_livre(autre)
        self.assertIn(self.livre, self.editeur.livres)
        self.assertIn(autre, self.editeur.livres)
        self.assertIn(self.livre, self.auteur.livres)
        self.assertIn(autre, self.auteur.livres)
        self.assertIs(self.livre.editeur, autre.editeur)
        self.assertIs(self.livre.auteurs[0], autre.auteurs[0])
        self.livre.ajouter_auteur(self.auteur)
        self.assertEqual(self.livre.auteurs.count(self.auteur), 1)
        self.assertEqual(self.auteur.livres.count(self.livre), 1)

    def test_03_composition_et_collections_protegees(self):
        exemplaire = self.livre.ajouter_exemplaire()
        numero = self.revue.ajouter_numero(1, "Dossier Python")
        self.assertIs(exemplaire.livre, self.livre)
        self.assertIs(numero.revue, self.revue)
        self.assertIn(exemplaire, self.livre.exemplaires)
        self.assertIn(numero, self.revue.numeros)
        for collection in (self.livre.auteurs, self.livre.exemplaires,
                           self.auteur.livres, self.editeur.livres,
                           self.revue.numeros, self.bib.livres):
            self.assertIsInstance(collection, tuple)
        with self.assertRaises(AttributeError):
            exemplaire.livre = Livre("Autre", "1", self.editeur)

    def test_04_prix_decimaux_et_prix_invalides(self):
        self.assertEqual(self.livre.prix_unitaire, Decimal("12000"))
        gratuit = Livre("Domaine public", "0", self.editeur)
        self.assertEqual(gratuit.prix_unitaire, Decimal("0"))
        for prix in ("-1", "NaN", "Infinity", "-Infinity", True,
                     "0.50", 12000.0, "1000000001", "abc"):
            with self.subTest(prix=prix):
                with self.assertRaises((ValueError, TypeError)):
                    Livre("Invalide", prix, self.editeur)
        with self.assertRaises(ValueError):
            self.livre.prix_unitaire = "-5"
        self.assertEqual(self.livre.prix_unitaire, Decimal("12000"))
        self.livre.set_prix_unitaire("9000")
        self.assertEqual(self.livre.prix_unitaire, Decimal("9000"))

    def test_05_entrees_textuelles_et_types(self):
        for titre in ("", " ", None, 12):
            with self.subTest(titre=titre):
                with self.assertRaises((ValueError, TypeError)):
                    Livre(titre, "10", self.editeur)
        with self.assertRaises((ValueError, TypeError)):
            Livre("Invalide", "10", "un nom ne remplace pas un éditeur")
        with self.assertRaises((ValueError, TypeError)):
            self.livre.ajouter_exemplaire("inconnu")

    def test_06_codes_communs_aux_documents(self):
        documents = [self.livre.ajouter_exemplaire(),
                     self.revue.ajouter_numero(1),
                     self.livre.ajouter_exemplaire()]
        codes = [document.code for document in documents]
        self.assertEqual(len(codes), len(set(codes)))
        self.assertTrue(all(type(code) is int and code > 0 for code in codes))
        with self.assertRaises(AttributeError):
            documents[0].code = documents[1].code

    def test_07_numerotation_dans_chaque_revue(self):
        self.revue.ajouter_numero(1)
        with self.assertRaises(ValueError):
            self.revue.ajouter_numero(1)
        for numero in (0, -1, True, 1.5, "2"):
            with self.subTest(numero=numero):
                with self.assertRaises((ValueError, TypeError)):
                    self.revue.ajouter_numero(numero)
        autre = Revue("Autre revue", "annuelle")
        self.assertEqual(autre.ajouter_numero(1).numero, 1)

    def test_08_emprunt_et_retour(self):
        exemplaire = self.livre.ajouter_exemplaire()
        self.assertTrue(exemplaire.disponible)
        exemplaire.emprunter()
        self.assertFalse(exemplaire.disponible)
        self.assertTrue(exemplaire.emprunte)
        with self.assertRaises(ValueError):
            exemplaire.emprunter()
        exemplaire.rendre()
        self.assertTrue(exemplaire.disponible)
        self.assertFalse(exemplaire.emprunte)
        with self.assertRaises(ValueError):
            exemplaire.rendre()

    def test_09_exemplaire_abime_et_reparation(self):
        exemplaire = self.livre.ajouter_exemplaire("abime")
        self.assertFalse(exemplaire.disponible)
        with self.assertRaises(ValueError):
            exemplaire.emprunter()
        with self.assertRaises(ValueError):
            exemplaire.set_disponible(True)
        exemplaire.reparer()
        self.assertEqual(exemplaire.etat, "bon")
        self.assertTrue(exemplaire.disponible)

    def test_10_destruction_irreversible(self):
        exemplaire = self.livre.ajouter_exemplaire()
        exemplaire.detruire()
        self.assertEqual(exemplaire.etat, "detruit")
        self.assertFalse(exemplaire.disponible)
        for operation in (exemplaire.reparer, exemplaire.emprunter,
                          exemplaire.rendre,
                          lambda: exemplaire.set_etat_exemplaire("bon"),
                          lambda: exemplaire.set_disponible(True)):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(ValueError):
                    operation()
        self.assertEqual(exemplaire.etat, "detruit")

    def test_11_etat_non_modifiable_pendant_emprunt(self):
        exemplaire = self.livre.ajouter_exemplaire()
        exemplaire.emprunter()
        for operation in (exemplaire.reparer, exemplaire.detruire,
                          lambda: exemplaire.set_etat_exemplaire("abime")):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(ValueError):
                    operation()
        self.assertTrue(exemplaire.emprunte)
        self.assertFalse(exemplaire.disponible)
        exemplaire.rendre()
        exemplaire.set_etat_exemplaire("abime")
        self.assertFalse(exemplaire.disponible)

    def test_12_sauvegarde_recharge_les_relations(self):
        autre = Livre("Réseaux", "8000", self.editeur, (self.auteur,))
        self.bib.ajouter_livre(autre)
        emprunte = self.livre.ajouter_exemplaire("bon")
        emprunte.emprunter()
        autre.ajouter_exemplaire("abime")
        numero = self.revue.ajouter_numero(1, "Algorithmes et données")
        sauvegarder(self.bib, self.chemin)
        copie = charger(self.chemin)
        self.assertEqual(len(copie.livres), 2)
        self.assertEqual(len(copie.revues), 1)
        self.assertIs(copie.livres[0].editeur, copie.livres[1].editeur)
        self.assertIs(copie.livres[0].auteurs[0], copie.livres[1].auteurs[0])
        self.assertIs(copie.livres[0].exemplaires[0].livre, copie.livres[0])
        self.assertIs(copie.revues[0].numeros[0].revue, copie.revues[0])
        self.assertEqual(copie.livres[0].prix_unitaire, Decimal("12000"))
        self.assertTrue(copie.livres[0].exemplaires[0].emprunte)
        self.assertEqual(copie.revues[0].numeros[0].code, numero.code)
        self.assertEqual(copie.livres[0].titre, "Python pratique")

    def test_13_allocation_apres_rechargement(self):
        self.livre.ajouter_exemplaire()
        self.revue.ajouter_numero(1)
        sauvegarder(self.bib, self.chemin)
        copie = charger(self.chemin)
        anciens = {document.code for document in copie.documents()}
        nouveau = copie.livres[0].ajouter_exemplaire()
        self.assertGreater(nouveau.code, max(anciens))
        self.assertNotIn(nouveau.code, anciens)

    def test_14_fichier_invalide_ou_schema_inconnu(self):
        with self.assertRaises((ErreurStockage, FileNotFoundError)):
            charger(self.chemin)
        for contenu in ('{"version":', '[]', 'null', '"texte"'):
            with self.subTest(contenu=contenu):
                self.chemin.write_text(contenu, encoding="utf-8")
                with self.assertRaises(ErreurStockage):
                    charger(self.chemin)
                self.assertEqual(self.chemin.read_text(encoding="utf-8"), contenu)
        for version in (True, 999, "1"):
            with self.subTest(version=version):
                donnees = self.lire_json()
                donnees["version"] = version
                self.verifier_rejet(donnees)

    def test_15_types_et_etats_invalides_dans_json(self):
        self.livre.ajouter_exemplaire()
        modifications = (
            lambda d: d["livres"][0].update(prix="NaN"),
            lambda d: d["livres"][0].update(auteurs="1"),
            lambda d: d["editeurs"][0].update(id=True),
            lambda d: d["livres"][0]["exemplaires"][0].update(emprunte="non"),
            lambda d: d["livres"][0]["exemplaires"][0].update(
                etat="detruit", emprunte=True),
            lambda d: d.update(champ_non_prevu="interdit"),
        )
        for indice, modifier in enumerate(modifications):
            with self.subTest(cas=indice):
                donnees = self.lire_json()
                modifier(donnees)
                self.verifier_rejet(donnees)

    def test_16_doublons_et_references_inconnues(self):
        self.livre.ajouter_exemplaire()
        self.revue.ajouter_numero(1)
        modifications = (
            lambda d: d["editeurs"].append(dict(d["editeurs"][0])),
            lambda d: d["livres"][0].update(editeur=999999),
            lambda d: d["livres"][0].update(auteurs=[999999]),
            lambda d: d["revues"][0]["numeros"][0].update(
                code=d["livres"][0]["exemplaires"][0]["code"]),
        )
        for indice, modifier in enumerate(modifications):
            with self.subTest(cas=indice):
                donnees = self.lire_json()
                modifier(donnees)
                self.verifier_rejet(donnees)

    def test_17_fichier_trop_volumineux_inchange(self):
        contenu = b" " * (2 * 1024 * 1024 + 1)
        self.chemin.write_bytes(contenu)
        with self.assertRaises(ErreurStockage):
            charger(self.chemin)
        self.assertEqual(self.chemin.read_bytes(), contenu)

    def test_18_echec_ecriture_preserve_sauvegarde(self):
        sauvegarder(self.bib, self.chemin)
        avant = self.chemin.read_bytes()
        self.livre.ajouter_exemplaire()
        with patch("stockage.os.replace", side_effect=OSError("échec simulé")):
            with self.assertRaises((ErreurStockage, OSError)):
                sauvegarder(self.bib, self.chemin)
        self.assertEqual(self.chemin.read_bytes(), avant)
        self.assertEqual(list(self.chemin.parent.iterdir()), [self.chemin])

    def test_19_chargement_refuse_ne_consomme_pas_les_codes(self):
        premier = self.livre.ajouter_exemplaire()
        dernier = self.revue.ajouter_numero(1)
        donnees = self.lire_json()
        # Un premier document est restauré avant l'erreur du document suivant.
        donnees["livres"][0]["exemplaires"][0]["code"] = 10 ** 30
        donnees["revues"][0]["numeros"][0]["numero"] = 0
        self.verifier_rejet(donnees)
        nouveau = self.livre.ajouter_exemplaire()
        self.assertEqual(nouveau.code, dernier.code + 1)
        self.assertNotEqual(nouveau.code, premier.code)

    def test_20_fusion_refuse_les_collisions_de_codes(self):
        self.livre.ajouter_exemplaire()
        self.revue.ajouter_numero(1)
        sauvegarder(self.bib, self.chemin)
        copie = charger(self.chemin)
        with self.assertRaises(ValueError):
            self.bib.ajouter_livre(copie.livres[0])
        with self.assertRaises(ValueError):
            self.bib.ajouter_revue(copie.revues[0])
        self.assertEqual(len(self.bib.livres), 1)
        self.assertEqual(len(self.bib.revues), 1)


if __name__ == "__main__":
    unittest.main()
