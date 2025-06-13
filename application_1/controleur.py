import sys
import os
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from modele import ModeleMaxiMarket
from vue import VueMaxiMarket

# -----------------------------------------------------------------------------
# --- class ControleurMaxiMarket
# -----------------------------------------------------------------------------
class ControleurMaxiMarket:
    def __init__(self):
        # Création du modèle et de la vue
        self.modele = ModeleMaxiMarket()
        self.vue = VueMaxiMarket()
        
        # Affichage de la vue
        self.vue.show()
        
        # Mise à jour initiale de la vue
        self.maj_vue()
        
        # Connexion des signaux de la vue vers les slots du contrôleur
        self.vue.signal_nouveau_projet.connect(self.nouveau_projet)
        self.vue.signal_ouvrir_projet.connect(self.ouvrir_projet)
        self.vue.signal_sauvegarder_projet.connect(self.sauvegarder_projet)
        self.vue.signal_charger_plan.connect(self.charger_plan)
        self.vue.signal_selectionner_produits.connect(self.selectionner_produits)
        self.vue.signal_quadrillage_change.connect(self.quadrillage_change)
        self.vue.signal_produit_selectionne_placement.connect(self.produit_selectionne_placement)
        self.vue.signal_produit_place.connect(self.produit_place)
        self.vue.signal_supprimer_projet.connect(self.supprimer_projet)

    
    def maj_vue(self):
        # Afficher le plan
        plan = self.modele.get_plan()
        pixmap = plan.get_pixmap()
        if pixmap:
            self.vue.afficher_plan(pixmap, plan.get_nb_rangs(), plan.get_nb_rayons())
            
        
        # Mettre à jour les informations du projet
        projet = self.modele.get_projet()
        if not projet.est_vide():
            info = f"Projet: {projet.get_nom_projet()} | Auteur: {projet.get_auteur()} | Magasin: {projet.get_nom_magasin()}"
            self.vue.mettre_a_jour_projet_info(info)
        
        # Mettre à jour les produits et placements
        produits = self.modele.get_produits()
        produits_magasin = produits.get_produits_magasin()
        placements = produits.get_placements()
        
        self.vue.mettre_a_jour_produits(produits_magasin, placements)
        self.vue.mettre_a_jour_table_placements(placements)
        self.vue.afficher_placements(placements)
        
        # Mettre à jour les valeurs du quadrillage
        self.vue.set_quadrillage_values(plan.get_nb_rangs(), plan.get_nb_rayons())
    
    # Slots du contrôleur
    def nouveau_projet(self):
        result, data = self.vue.show_dialog_nouveau_projet()
        
        if result and data and all(data.values()):
            self.modele.nouveau_projet(
                data['nom_projet'],
                data['auteur'],
                data['nom_magasin'],
                data['adresse_magasin']
            )
            
            # Mettre à jour la vue
            self.maj_vue()
            
            QMessageBox.information(
                self.vue,
                "Succès",
                "Projet créé avec succès."
            )
        elif result:
            QMessageBox.warning(
                self.vue,
                "Erreur",
                "Tous les champs sont obligatoires."
            )
    
    def ouvrir_projet(self):
        fichier, _ = QFileDialog.getOpenFileName(
            self.vue,
            "Ouvrir un projet",
            "",
            "Fichiers JSON (*.json)"
        )
        
        if fichier:
            try:
                success = self.modele.charger_projet(fichier)
                if success:
                    self.maj_vue()
                    
                    # Mettre à jour l'info du plan
                    plan = self.modele.get_plan()
                    if plan.get_pixmap():
                        chemin = plan.get_chemin()
                        nom_fichier = os.path.basename(chemin) if chemin else "Plan chargé"
                        self.vue.mettre_a_jour_plan_info(f"Plan: {nom_fichier}")
                    
                    QMessageBox.information(
                        self.vue,
                        "Succès",
                        "Projet ouvert avec succès."
                    )
                else:
                    QMessageBox.critical(
                        self.vue,
                        "Erreur",
                        "Impossible d'ouvrir le projet."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self.vue,
                    "Erreur",
                    f"Erreur lors de l'ouverture du projet:\n{str(e)}"
                )
    
    def sauvegarder_projet(self):
        projet = self.modele.get_projet()
        
        if projet.est_vide():
            QMessageBox.warning(
                self.vue,
                "Avertissement",
                "Aucun projet à sauvegarder. Créez d'abord un projet."
            )
            return
        
        try:
            success = self.modele.sauvegarder_projet()
            if success:
                QMessageBox.information(
                    self.vue,
                    "Succès",
                    "Projet sauvegardé avec succès."
                )
            else:
                QMessageBox.critical(
                    self.vue,
                    "Erreur",
                    "Impossible de sauvegarder le projet."
                )
        except Exception as e:
            QMessageBox.critical(
                self.vue,
                "Erreur",
                f"Erreur lors de la sauvegarde:\n{str(e)}"
            )
    
    def charger_plan(self):
        projet = self.modele.get_projet()
        
        if projet.est_vide():
            QMessageBox.warning(
                self.vue,
                "Avertissement",
                "Créez d'abord un projet avant de charger un plan."
            )
            return
        
        fichier, _ = QFileDialog.getOpenFileName(
            self.vue,
            "Charger un plan",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if fichier:
            try:
                success = self.modele.charger_plan(fichier)
                if success:
                    # Mettre à jour la vue
                    plan = self.modele.get_plan()
                    self.vue.afficher_plan(plan.get_pixmap(), plan.get_nb_rangs(), plan.get_nb_rayons())
                    self.vue.mettre_a_jour_plan_info(f"Plan: {os.path.basename(fichier)}")
                    
                    # Réafficher les placements
                    placements = self.modele.get_produits().get_placements()
                    self.vue.afficher_placements(placements)
                else:
                    QMessageBox.critical(
                        self.vue,
                        "Erreur",
                        "Impossible de charger l'image."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self.vue,
                    "Erreur",
                    f"Erreur lors du chargement du plan:\n{str(e)}"
                )
    
    def selectionner_produits(self):
        projet = self.modele.get_projet()
        
        if projet.est_vide():
            QMessageBox.warning(
                self.vue,
                "Avertissement",
                "Créez d'abord un projet avant de sélectionner les produits."
            )
            return
        
        # Obtenir les catégories de produits disponibles
        produits = self.modele.get_produits()
        categories = produits.get_tous_produits_disponibles()
        
        result, produits_selectionnes = self.vue.show_dialog_selection_produits(categories)
        
        if result and produits_selectionnes:
            # Mettre à jour le modèle
            produits.set_produits_magasin(produits_selectionnes)
            
            # Mettre à jour la vue
            placements = produits.get_placements()
            self.vue.mettre_a_jour_produits(produits_selectionnes, placements)
            self.vue.mettre_a_jour_table_placements(placements)
    
    def quadrillage_change(self, nb_rangs, nb_rayons):
        plan = self.modele.get_plan()
        plan.set_nb_rangs(nb_rangs)
        plan.set_nb_rayons(nb_rayons)
        
        # Mettre à jour l'affichage
        if plan.get_pixmap():
            self.vue.afficher_plan(plan.get_pixmap(), nb_rangs, nb_rayons)
            
            # Réafficher les placements
            placements = self.modele.get_produits().get_placements()
            self.vue.afficher_placements(placements)
    
    def produit_selectionne_placement(self, produit):
        self.vue.set_produit_a_placer(produit)
        QMessageBox.information(
            self.vue,
            "Placement",
            f"Cliquez sur le plan pour placer '{produit}'."
        )
    
    def produit_place(self, produit, x, y):
        # Mettre à jour le modèle
        produits = self.modele.get_produits()
        produits.placer_produit(produit, x, y)
        
        # Mettre à jour la vue
        produits_magasin = produits.get_produits_magasin()
        placements = produits.get_placements()
        
        self.vue.mettre_a_jour_produits(produits_magasin, placements)
        self.vue.mettre_a_jour_table_placements(placements)
        self.vue.afficher_placements(placements)
        
        QMessageBox.information(
            self.vue,
            "Succès",
            f"'{produit}' placé en position ({x}, {y})."
        )


    def supprimer_projet(self):
        projet = self.modele.get_projet()
        
        if projet.est_vide():
            QMessageBox.warning(
                self.vue,
                "Avertissement",
                "Aucun projet à supprimer. Ouvrez d'abord un projet."
            )
            return
        
        nom_projet = projet.get_nom_projet()
        reply = QMessageBox.question(
            self.vue,
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer le projet '{nom_projet}' ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            fichier = projet.get_fichier_sauvegarde()
            if os.path.exists(fichier):
                try:
                    os.remove(fichier)
                    
                    self.modele = ModeleMaxiMarket()
                    
                    self.vue.mettre_a_jour_projet_info("Aucun projet ouvert")
                    self.vue.mettre_a_jour_plan_info("Aucun plan chargé")
                    self.vue.mettre_a_jour_produits([], {})
                    self.vue.mettre_a_jour_table_placements({})
                    self.vue.afficher_plan(None, 24, 47)
                    
                    QMessageBox.information(
                        self.vue,
                        "Succès",
                        f"Le projet '{nom_projet}' a été supprimé avec succès."
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self.vue,
                        "Erreur",
                        f"Erreur lors de la suppression du projet:\n{str(e)}"
                    )

# Programme principal : test du contrôleur ------------------------------------
if __name__ == "__main__":
    print('TEST: class ControleurMaxiMarket')
    
    app = QApplication(sys.argv)
    
    controleur = ControleurMaxiMarket()
    
    sys.exit(app.exec())
