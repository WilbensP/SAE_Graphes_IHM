import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

#  charger l image
chemin_image = "plan.jpg"
plan_magasin = mpimg.imread(chemin_image)

# dimension image quadrillage
nb_rangs, nb_rayons = 24, 47
hauteur_image, largeur_image = plan_magasin.shape[0], plan_magasin.shape[1]
hauteur_case = hauteur_image / nb_rangs
largeur_case = largeur_image / nb_rayons

# quadrillage rouge par dessus l image
fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
ax.imshow(plan_magasin)

# quadrillage rouge
for rang in range(nb_rangs + 1):
    y = rang * hauteur_case
    ax.plot([0, largeur_image], [y, y], color='red', linewidth=0.5)

for rayon in range(nb_rayons + 1):
    x = rayon * largeur_case
    ax.plot([x, x], [0, hauteur_image], color='red', linewidth=0.5)

# on a retirer les axes
ax.set_xticks([])
ax.set_yticks([])
plt.tight_layout()
plt.show()
