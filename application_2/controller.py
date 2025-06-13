import os
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QMessageBox
from modele import ProjetModel, ProduitsModel, CalculChemin
from vue import MaxiMarketMainWindow

class MaxiMarketController(QObject):
    """Contrôleur principal de l'application MaxiMarket"""
    
    def __init__(self):
        super().__init__()
        
        # Icreation modeles
        self.projet_model = ProjetModel()
        self.produits_model = ProduitsModel()
        self.calcul_chemin = CalculChemin()
        
        # creation vue
        self.view = MaxiMarketMainWindow()
        
        # signaux
        self.connecter_signaux()
        
        # Variables
        self.tous_produits = []
        self.chemin_courant = []
        
        # Charger projets 
        self.charger_projets_disponibles()
    
    def connecter_signaux(self):
        """Connecte tous les signaux entre les modèles et la vue"""
        
        # Signaux controleur
        self.view.ouvrir_projet_demande.connect(self.ouvrir_projet)
        self.view.produit_selectionne.connect(self.selection_produit)
        self.view.ajouter_produit_demande.connect(self.ajouter_produit_liste)
        self.view.produit_liste_selectionne.connect(self.produit_liste_selectionne)
        self.view.generer_liste_demande.connect(self.generer_liste_aleatoire)
        self.view.reinitialiser_liste_demande.connect(self.reinitialiser_liste)
        self.view.enregistrer_liste_demande.connect(self.enregistrer_liste)
        self.view.calculer_chemin_demande.connect(self.calculer_chemin)
        
        # Signaux controleur
        self.projet_model.projet_charge.connect(self.projet_charge)
        self.projet_model.erreur.connect(self.afficher_erreur)
        self.produits_model.produits_charges.connect(self.produits_charges)
        self.produits_model.liste_generee.connect(self.liste_generee)
    
    def charger_projets_disponibles(self):
        """Charge la liste des projets disponibles"""
        projets = self.projet_model.get_projets_disponibles()
        self.view.mettre_a_jour_projets(projets)
    
    def ouvrir_projet(self):
        """Gère l'ouverture d'un projet existant"""
        index = self.view.projet_combo.currentIndex()
        if index >= 0:
            fichier = self.view.projet_combo.itemData(index)
            if fichier:
                self.charger_projet(fichier)
    
    def charger_projet(self, fichier):
        """Charge un projet depuis un fichier"""
        try:
            import json
            with open(fichier, "r", encoding="utf-8") as f:
                projet = json.load(f)
            
            dossier_projet = os.path.dirname(fichier)
            chemin_plan = os.path.join(dossier_projet, projet["chemin_plan"])
            
            if not os.path.exists(chemin_plan):
                reponse = QMessageBox.question(
                    self.view, "Plan manquant",
                    f"Le plan '{projet['chemin_plan']}' est introuvable. Voulez-vous sélectionner un autre plan ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reponse == QMessageBox.StandardButton.Yes:
                    nouveau_plan = self.view.demander_fichier_ouvrir(
                        "Sélectionner un plan", "", "Images (*.jpg *.png)"
                    )
                    if nouveau_plan:
                        from modele import copier_fichier
                        copier_fichier(nouveau_plan, chemin_plan)
                    else:
                        return
                else:
                    return
            
            self.projet_model.charger_projet(fichier)
            
        except Exception as e:
            self.view.afficher_message("Erreur", f"Impossible de charger le projet:\n{str(e)}", "error")
    
    def projet_charge(self, projet):
        """Callback appelé quand un projet est chargé"""
        # fenetre
        nom_magasin = projet.get('nom_magasin', 'Plan du magasin')
        self.view.mettre_a_jour_titre(f"MaxiMarket - {nom_magasin}")
        
        # Charger plan
        chemin_plan = projet.get("chemin_plan_absolu")
        if chemin_plan and os.path.exists(chemin_plan):
            scene = self.view.get_rendu().scene()
            if scene.charger_plan(chemin_plan):
                scene.nb_rangs = projet.get("nb_rangs", 24)
                scene.nb_rayons = projet.get("nb_rayons", 40)
                scene.creer_quadrillage()
                
                if "placements" in projet:
                    scene.afficher_emplacements(
                        projet["placements"],
                        projet.get("nb_rangs", 24),
                        projet.get("nb_rayons", 40)
                    )
                
                self.view.get_rendu().fitInView(scene.sceneRect())
        
        # Charger produits
        if "produits_magasin" in projet:
            self.produits_model.charger_produits(projet["produits_magasin"])
        
        # Vider liste de courses et chemin
        self.view.vider_liste()
        self.view.vider_table_chemin()
        self.chemin_courant = []
    
    def afficher_erreur(self, message):
        """Affiche un message d'erreur"""
        self.view.afficher_message("Erreur", message, "error")
    
    def produits_charges(self, produits):
        """Callback appelé quand les produits sont chargés"""
        self.tous_produits = produits
        self.view.mettre_a_jour_produits(produits)
    
    def selection_produit(self, produit):
        """Gère la sélection d'un produit"""
        self.view.mettre_a_jour_produit_selectionne(produit)
        if produit:
            scene = self.view.get_rendu().scene()
            point_central = scene.mettre_en_evidence_produit(produit)
            self.view.get_rendu().centrer_sur_point(point_central)
    
    def ajouter_produit_liste(self, produit, quantite):
        """Ajoute un produit à la liste de courses"""
        if self.produits_model.ajouter_produit_liste(produit):
            self.view.ajouter_item_liste(produit)
    
    def produit_liste_selectionne(self, produit):
        """Gère la sélection d'un produit dans la liste"""
        scene = self.view.get_rendu().scene()
        point_central = scene.mettre_en_evidence_produit(produit)
        self.view.get_rendu().centrer_sur_point(point_central)
    
    def generer_liste_aleatoire(self):
        """Génère une liste aléatoire de produits"""
        if not self.tous_produits:
            self.view.afficher_message("Avertissement", "Aucun produit disponible.", "warning")
            return
        
        self.produits_model.generer_liste_aleatoire()
    
    def liste_generee(self, produits):
        """Callback appelé quand une liste est générée"""
        self.view.vider_liste()
        for produit in produits:
            self.view.ajouter_item_liste(produit)
        
        # Vider chemin
        scene = self.view.get_rendu().scene()
        scene.effacer_chemin()
        self.view.vider_table_chemin()
        self.chemin_courant = []
    
    def reinitialiser_liste(self):
        """Remet à zéro la liste de courses"""
        self.produits_model.reinitialiser_liste()
        self.view.vider_liste()
        
        # Effacer chemin
        scene = self.view.get_rendu().scene()
        scene.effacer_chemin()
        self.view.vider_table_chemin()
        self.chemin_courant = []
    
    def enregistrer_liste(self):
        """Enregistre la liste de courses"""
        liste_courses = self.produits_model.get_liste_courses()
        if not liste_courses:
            self.view.afficher_message("Info", "La liste est vide, rien à enregistrer.")
            return
        
        fichier = self.view.demander_fichier_sauvegarder(
            "Enregistrer la liste", "", "Fichiers texte (*.txt)"
        )
        
        if fichier:
            projet = self.projet_model.get_projet_actuel()
            nom_magasin = projet.get('nom_magasin', 'MaxiMarket') if projet else 'MaxiMarket'
            
            if self.produits_model.sauvegarder_liste(fichier, nom_magasin):
                self.view.afficher_message("Succès", "Liste enregistrée avec succès.")
            else:
                self.view.afficher_message("Erreur", "Impossible d'enregistrer la liste.", "error")
    
    def calculer_chemin(self):
        """Calcule et affiche le chemin optimal"""
        liste_courses = self.produits_model.get_liste_courses()
        if not liste_courses:
            self.view.afficher_message("Info", "La liste est vide, impossible de calculer un chemin.")
            return
        
        # Recuperer placements produits
        scene = self.view.get_rendu().scene()
        placements = scene.coordonnees_produits
        
        # chemin optimal
        self.chemin_courant = self.calcul_chemin.calculer_chemin_optimal(liste_courses, placements)
        
        if self.chemin_courant:
            # Afficher chemin 
            scene.afficher_chemin(self.chemin_courant)
            
            # table 
            self.view.mettre_a_jour_table_chemin(self.chemin_courant)
            
            self.view.afficher_message(
                "Chemin calculé",
                f"Le chemin a été calculé pour {len(self.chemin_courant)} produits."
            )
        else:
            self.view.afficher_message("Info", "Impossible de calculer un chemin avec les produits sélectionnés.")
    
    def get_view(self):
        """Retourne la vue principale"""
        return self.view
