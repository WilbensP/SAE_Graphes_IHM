import os
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QMessageBox
from modele import ProjetModel, ProduitsModel, CalculChemin
from vue import MaxiMarketMainWindow

class MaxiMarketController(QObject):
    
    def __init__(self):
        super().__init__()
        
        # créations des modeles
        self.projet_model = ProjetModel()
        self.produits_model = ProduitsModel()
        self.calcul_chemin = CalculChemin(point_depart=(29, 3))  # on met le point de depart a l'entree
        
        # creation de la fenetre 
        self.view = MaxiMarketMainWindow()
        
        # connection des signaux
        self.connecter_signaux()
        
        # variables pour stocker les donnees
        self.tous_produits = []
        self.chemin_courant = []
        
        # on charge un projet automatiquement au demarrage
        self.charger_projet_defaut()
    
    def connecter_signaux(self):

        # signaux 
        self.view.produit_selectionne.connect(self.selection_produit)
        self.view.ajouter_produit_demande.connect(self.ajouter_produit_liste)
        self.view.produit_liste_selectionne.connect(self.produit_liste_selectionne)
        self.view.generer_liste_demande.connect(self.generer_liste_aleatoire)
        self.view.reinitialiser_liste_demande.connect(self.reinitialiser_liste)
        self.view.enregistrer_liste_demande.connect(self.enregistrer_liste)
        self.view.calculer_chemin_demande.connect(self.calculer_chemin)
        
        # signaux 
        self.projet_model.projet_charge.connect(self.projet_charge)
        self.projet_model.erreur.connect(self.afficher_erreur)
        self.produits_model.produits_charges.connect(self.produits_charges)
        self.produits_model.liste_generee.connect(self.liste_generee)
    
    def charger_projet_defaut(self):
        # on cherche d'abord dans le dossier projets
        dossier_projets = self.projet_model.dossier_projets
        if os.path.exists(dossier_projets):
            for fichier in os.listdir(dossier_projets):
                if fichier.endswith('.json'):
                    chemin_fichier = os.path.join(dossier_projets, fichier)
                    self.charger_projet(chemin_fichier)
                    return
        
        # si rien trouve, on cherche dans le dossier courant
        for fichier in os.listdir('.'):
            if fichier.endswith('.json'):
                self.charger_projet(fichier)
                return
        
        # on affiche un message d'erreur
        self.view.afficher_message("Erreur", "Aucun fichier de projet (.json) trouvé. Veuillez placer un fichier de projet dans le dossier de l'application ou dans le sous-dossier 'projets'.", "error")
    
    def charger_projet(self, fichier):
        try:
            import json
            # on lit le fichier json
            with open(fichier, "r", encoding="utf-8") as f:
                projet = json.load(f)
            
            # on verifie que le plan existe
            dossier_projet = os.path.dirname(fichier)
            chemin_plan = os.path.join(dossier_projet, projet["chemin_plan"])
            
            if not os.path.exists(chemin_plan):
                # si le plan n'existe pas, on demande a l'utilisateur
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
            
            # on charge le projet
            self.projet_model.charger_projet(fichier)
            
        except Exception as e:
            self.view.afficher_message("Erreur", f"Impossible de charger le projet:\n{str(e)}", "error")
    
    def projet_charge(self, projet):
        
        # on met a jour le titre de la fenetre
        nom_magasin = projet.get('nom_magasin', 'Plan du magasin')
        self.view.mettre_a_jour_titre(f"MaxiMarket - {nom_magasin}")
        
        # on charge le plan dans la vue
        chemin_plan = projet.get("chemin_plan_absolu")
        if chemin_plan and os.path.exists(chemin_plan):
            scene = self.view.get_rendu().scene()
            if scene.charger_plan(chemin_plan):
                scene.nb_rangs = projet.get("nb_rangs", 24)
                scene.nb_rayons = projet.get("nb_rayons", 40)
                scene.creer_quadrillage()
                
                # on affiche les emplacements des produits
                if "placements" in projet:
                    scene.afficher_emplacements(
                        projet["placements"],
                        projet.get("nb_rangs", 24),
                        projet.get("nb_rayons", 40)
                    )
                
                self.view.get_rendu().fitInView(scene.sceneRect())
        
        # on charge les produits
        if "produits_magasin" in projet:
            self.produits_model.charger_produits(projet["produits_magasin"])
        
        # on vide la liste de courses et le chemin
        self.view.vider_liste()
        self.view.vider_table_chemin()
        self.chemin_courant = []
    
    def afficher_erreur(self, message):
        self.view.afficher_message("Erreur", message, "error")
    
    def selection_produit(self, produit):
        self.view.mettre_a_jour_produit_selectionne(produit)
        if produit:
            # on met le produit sur le plan
            scene = self.view.get_rendu().scene()
            point_central = scene.mettre_en_evidence_produit(produit)
            self.view.get_rendu().centrer_sur_point(point_central)
    
    def ajouter_produit_liste(self, produit, quantite):
        if self.produits_model.ajouter_produit_liste(produit):
            self.view.ajouter_item_liste(produit)
    
    def produit_liste_selectionne(self, produit):
        # on met le produit sur le plan
        scene = self.view.get_rendu().scene()
        point_central = scene.mettre_en_evidence_produit(produit)
        self.view.get_rendu().centrer_sur_point(point_central)
    
    def generer_liste_aleatoire(self):
        if not self.tous_produits:
            self.view.afficher_message("Avertissement", "Aucun produit disponible.", "warning")
            return
        
        # on genere une liste aleatoire
        self.produits_model.generer_liste_aleatoire()
    
    def liste_generee(self, produits):
        # on met a jour la liste dans la vue
        self.view.vider_liste()
        for produit in produits:
            self.view.ajouter_item_liste(produit)
        
        # on vide le chemin car la liste a change
        scene = self.view.get_rendu().scene()
        scene.effacer_chemin()
        self.view.vider_table_chemin()
        self.chemin_courant = []
    
    def reinitialiser_liste(self):
        self.produits_model.reinitialiser_liste()
        self.view.vider_liste()
        
        # on efface le chemin
        scene = self.view.get_rendu().scene()
        scene.effacer_chemin()
        self.view.vider_table_chemin()
        self.chemin_courant = []
    
    def enregistrer_liste(self):
        liste_courses = self.produits_model.get_liste_courses()
        if not liste_courses:
            self.view.afficher_message("Info", "La liste est vide, rien à enregistrer.")
            return
        
        # on demande ou sauvegarder le fichier
        fichier = self.view.demander_fichier_sauvegarder(
            "Enregistrer la liste", "", "Fichiers texte (*.txt)"
        )
        
        if fichier:
            projet = self.projet_model.get_projet_actuel()
            nom_magasin = projet.get('nom_magasin', 'MaxiMarket') if projet else 'MaxiMarket'
            
            # on sauvegarde la liste
            if self.produits_model.sauvegarder_liste(fichier, nom_magasin):
                self.view.afficher_message("Succès", "Liste enregistrée avec succès.")
            else:
                self.view.afficher_message("Erreur", "Impossible d'enregistrer la liste.", "error")
    
    def calculer_chemin(self):
        liste_courses = self.produits_model.get_liste_courses()
        if not liste_courses:
            self.view.afficher_message("Info", "La liste est vide, impossible de calculer un chemin.")
            return
        
        # on recupere les coordonnees des produits
        scene = self.view.get_rendu().scene()
        placements = scene.coordonnees_produits
        
        # on calcule le chemin optimal
        self.chemin_courant = self.calcul_chemin.calculer_chemin_optimal(liste_courses, placements)
        
        if self.chemin_courant:
            # on affiche le chemin sur le plan
            scene.afficher_chemin(self.chemin_courant)
            
            # on met a jour la table des informations
            self.view.mettre_a_jour_table_chemin(self.chemin_courant)
            
            self.view.afficher_message(
                "Chemin calculé",
                f"Le chemin a été calculé pour {len(self.chemin_courant)} produits."
            )
        else:
            self.view.afficher_message("Info", "Impossible de calculer un chemin avec les produits sélectionnés.")
    
    def get_view(self):
        return self.view
