from pathlib import Path

import matplotlib  # type: ignore[reportMissingModuleSource]
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # type: ignore[reportMissingModuleSource]

from modele import Bibliotheque

bibliotheque = Bibliotheque.demo()
libelles = ["Livres", "Revues"]
effectifs = [len(bibliotheque.livres), len(bibliotheque.revues)]

fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
ax.bar(libelles, effectifs)
ax.set_title("Titres du catalogue")
ax.set_ylabel("Nombre de titres")
ax.set_ylim(bottom=0)

dossier = Path(__file__).resolve().parent / "sorties"
dossier.mkdir(exist_ok=True)
fig.savefig(dossier / "premier_graphique.png", dpi=150)
plt.close(fig)