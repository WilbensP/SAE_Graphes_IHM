import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

# Charger l'image
chemin_image = chemin_image = "plan.jpg"
plan_magasin = mpimg.imread(chemin_image)

# Dimensions du quadrillage
nb_rangs, nb_rayons = 24, 47
hauteur_image, largeur_image = plan_magasin.shape[0], plan_magasin.shape[1]
hauteur_case = hauteur_image / nb_rangs
largeur_case = largeur_image / nb_rayons

# Charger les produits
chemin_produits = "produits_selectionnes.json"
with open(chemin_produits, encoding="utf-8") as f:
    import json  # import uniquement ici pour charger le JSON
    data = json.load(f)

# Mapping des catégories vers des zones précises du plan
zones_categories = {
    "Légumes": [(6, 5), (6, 6)],
    "Fruits": [(7, 5), (7, 6)],
    "Viandes": [(2, 13), (2, 14), (2, 15)],
    "Épicerie": [(12, 10), (12, 11), (13, 10), (13, 11)],
    "Épicerie sucrée": [(14, 10)],
    "Rayon frais": [(5, 9), (5, 10)],
    "Crèmerie": [(3, 4), (3, 5)],
    "Conserves": [(14, 11)],
    "Boissons": [(15, 1), (15, 2)]
}

# Associer produits aux cases du plan selon leur catégorie
cases = {}
for categorie, produits in data.items():
    positions = zones_categories.get(categorie, [])
    index = 0
    for position in positions:
        i, j = position
        cases[(i, j)] = produits[index:index + 3]
        index += 3
        if index >= len(produits):
            break

# Affichage
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(plan_magasin)

# Quadrillage rouge
for rang in range(nb_rangs + 1):
    y = rang * hauteur_case
    ax.plot([0, largeur_image], [y, y], color='red', linewidth=0.5)

for rayon in range(nb_rayons + 1):
    x = rayon * largeur_case
    ax.plot([x, x], [0, hauteur_image], color='red', linewidth=0.5)

# Désactiver les axes
ax.set_xticks([])
ax.set_yticks([])
plt.tight_layout()

# Infobulle au survol
annot = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def survol(event):
    if event.inaxes == ax and event.xdata and event.ydata:
        i = int(event.ydata // hauteur_case)
        j = int(event.xdata // largeur_case)
        produits_case = cases.get((i, j))
        if produits_case:
            annot.xy = (event.xdata, event.ydata)
            annot.set_text(", ".join(produits_case))
            annot.set_visible(True)
        else:
            annot.set_visible(False)
        fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", survol)

plt.show()
