from PyQt6.QtWidgets import QMessageBox
from modele2 import ModeleApp2
from vue2 import VueApp2

class ControleurApp2:
    """Classe du contrôleur pour l'application 2"""
    def __init__(self):
        # Initialiser le modèle et la vue
        self.modele = ModeleApp2()
        self.vue = VueApp2()
        
        # Connecter les signaux de la vue aux méthodes du contrôleur
        self.connecter_signaux()
        
        # Charger les données initiales
        self.charger_projets_disponibles()
    
    def connecter_signaux(self):
        """Connecte les signaux de la vue aux méthodes du contrôleur"""
        self.vue.signal_charger_magasin.connect(self.charger_magasin)
        self.vue.signal_ajouter_produit.connect(self.ajouter_produit)
        self.vue.signal_supprimer_produit.connect(self.supprimer_produit)
        self.vue.signal_vider_liste.connect(self.vider_liste)
        self.vue.signal_calculer_chemin.connect(self.calculer_chemin)
        self.vue.signal_sauvegarder_liste.connect(self.sauvegarder_liste)
        self.vue.signal_charger_liste.connect(self.charger_liste)
    
    def charger_projets_disponibles(self):
        """Charge la liste des projets disponibles"""
        projets = self.modele.get_projets_disponibles()
        self.vue.mettre_a_jour_projets(projets)
    
    def charger_magasin(self, fichier):
        """Charge un magasin depuis un fichier de projet"""
        try:
            success = self.modele.charger_magasin(fichier)
            if success:
                # Mettre à jour la vue
                self.vue.mettre_a_jour_info_magasin(
                    self.modele.magasin.nom,
                    self.modele.magasin.adresse
                )
                
                # Afficher le plan
                self.vue.afficher_plan(
                    self.modele.magasin.pixmap,
                    self.modele.magasin.nb_rangs,
                    self.modele.magasin.nb_rayons
                )
                
                # Afficher les produits
                self.vue.afficher_produits(self.modele.magasin.produits_places)
                
                # Mettre à jour la liste des produits disponibles
                produits_disponibles = self.modele.magasin.get_produits_disponibles()
                self.vue.mettre_a_jour_produits_disponibles(produits_disponibles)
                
                self.vue.show_message("Succès", "Magasin chargé avec succès.")
            else:
                self.vue.show_error("Erreur", "Impossible de charger le magasin.")
        except Exception as e:
            self.vue.show_error("Erreur", f"Erreur lors du chargement du magasin: {str(e)}")
    
    def ajouter_produit(self, produit):
        """Ajoute un produit à la liste de courses"""
        success = self.modele.ajouter_produit_liste(produit)
        if success:
            # Mettre à jour la liste de courses
            self.vue.mettre_a_jour_liste_courses(self.modele.liste_courses.produits)
    
    def supprimer_produit(self, produit):
        """Supprime un produit de la liste de courses"""
        success = self.modele.supprimer_produit_liste(produit)
        if success:
            # Mettre à jour la liste de courses
            self.vue.mettre_a_jour_liste_courses(self.modele.liste_courses.produits)
            
            # Recalculer le chemin si nécessaire
            if hasattr(self, 'chemin_courant') and self.chemin_courant:
                self.calculer_chemin()
    
    def vider_liste(self):
        """Vide la liste de courses"""
        self.modele.vider_liste_courses()
        self.vue.mettre_a_jour_liste_courses([])
        
        # Effacer le chemin
        self.vue.afficher_chemin([])
        self.vue.mettre_a_jour_table_chemin([])
    
    def calculer_chemin(self):
        """Calcule le chemin optimal pour la liste de courses"""
        if not self.modele.liste_courses.produits:
            self.vue.show_message("Information", "La liste de courses est vide.")
            return
        
        chemin = self.modele.calculer_chemin_optimal()
        self.chemin_courant = chemin
        
        if chemin:
            # Afficher le chemin sur le plan
            self.vue.afficher_chemin(chemin)
            
            # Mettre à jour la table des informations
            self.vue.mettre_a_jour_table_chemin(chemin)
        else:
            self.vue.show_error("Erreur", "Impossible de calculer le chemin.")
    
    def sauvegarder_liste(self):
        """Sauvegarde la liste de courses"""
        if not self.modele.liste_courses.produits:
            self.vue.show_message("Information", "La liste de courses est vide.")
            return
        
        # Demander le nom de la liste
        result, nom = self.vue.show_dialog_nom_liste()
        if result and nom:
            self.modele.liste_courses.nom = nom
            
            # Demander le fichier de sauvegarde
            fichier, _ = self.vue.show_file_dialog_save()
            if fichier:
                success = self.modele.sauvegarder_liste(fichier)
                if success:
                    self.vue.show_message("Succès", "Liste sauvegardée avec succès.")
                else:
                    self.vue.show_error("Erreur", "Impossible de sauvegarder la liste.")
    
    def charger_liste(self):
        """Charge une liste de courses"""
        fichier, _ = self.vue.show_file_dialog_open()
        if fichier:
            success = self.modele.charger_liste(fichier)
            if success:
                # Mettre à jour la liste de courses
                self.vue.mettre_a_jour_liste_courses(self.modele.liste_courses.produits)
                self.vue.show_message("Succès", "Liste chargée avec succès.")
            else:
                self.vue.show_error("Erreur", "Impossible de charger la liste.")
    
    def show(self):
        """Affiche la vue principale"""
        self.vue.show()

# Test du contrôleur
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    controleur = ControleurApp2()
    controleur.show()
    
    sys.exit(app.exec())
