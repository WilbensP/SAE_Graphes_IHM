import sys
import os
import json
from PyQt6.QtGui import QPixmap

# -----------------------------------------------------------------------------
#  class plan
# -----------------------------------------------------------------------------
class Plan:
    def __init__(self, chemin_plan: str = ""):
        self.__chemin_plan = chemin_plan
        self.__pixmap = None
        self.__nb_rangs = 24
        self.__nb_rayons = 47
        if chemin_plan:
            self.charger_plan()
    
    def charger_plan(self, chemin_plan: str = ""):
        if chemin_plan:
            self.__chemin_plan = chemin_plan
        
        if os.path.exists(self.__chemin_plan):
            self.__pixmap = QPixmap(self.__chemin_plan)
            return True
        return False
    
    def get_pixmap(self):
        return self.__pixmap
    
    def get_chemin(self):
        return self.__chemin_plan
    
    def get_dimensions(self):
        if self.__pixmap:
            return self.__pixmap.width(), self.__pixmap.height()
        return 0, 0
    
    def get_nb_rangs(self):
        return self.__nb_rangs
    
    def get_nb_rayons(self):
        return self.__nb_rayons
    
    def set_nb_rangs(self, nb_rangs):
        self.__nb_rangs = nb_rangs
    
    def set_nb_rayons(self, nb_rayons):
        self.__nb_rayons = nb_rayons
    
    def get_taille_case(self):
        largeur, hauteur = self.get_dimensions()
        if largeur > 0 and hauteur > 0:
            largeur_case = largeur / self.__nb_rayons
            hauteur_case = hauteur / self.__nb_rangs
            return largeur_case, hauteur_case
        return 0, 0

# -----------------------------------------------------------------------------
#  class produit
# -----------------------------------------------------------------------------
class Produits:
    def __init__(self):
        self.__produits_disponibles = {}
        self.__produits_magasin = []
        self.__placements = {} 
        
        # charger les  produits de la liste de course
        self.charger_depuis_fichier("Ressources/produits_selectionnes.json")
    
    def charger_depuis_fichier(self, chemin_fichier: str) -> bool:
        try:
            if os.path.exists(chemin_fichier):
                with open(chemin_fichier, "r", encoding="utf-8") as f:
                    self.__produits_disponibles = json.load(f)
                return True
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
        return False
    
    def get_categories(self) -> list:
        return list(self.__produits_disponibles.keys())
    
    def get_produits_categorie(self, categorie: str) -> list:
        return self.__produits_disponibles.get(categorie, [])
    
    def get_tous_produits_disponibles(self) -> dict:
        return self.__produits_disponibles.copy()
    
    def set_produits_magasin(self, produits_selectionnes: list):
        self.__produits_magasin = produits_selectionnes.copy()
        # reinitialiser le placement des produit
        self.__placements.clear()
    
    def get_produits_magasin(self) -> list:
        return self.__produits_magasin.copy()
    
    def placer_produit(self, produit: str, x: int, y: int):
        if produit in self.__produits_magasin:
            self.__placements[(x, y)] = produit
    
    def supprimer_placement(self, x: int, y: int):
        if (x, y) in self.__placements:
            del self.__placements[(x, y)]
    
    def get_placements(self) -> dict:
        return self.__placements.copy()
    
    def get_produit_a_position(self, x: int, y: int) -> str:
        return self.__placements.get((x, y), "")
    
    def get_position_produit(self, produit: str) -> tuple:
        for (x, y), p in self.__placements.items():
            if p == produit:
                return (x, y)
        return None
    
    def est_produit_place(self, produit: str) -> bool:
        return produit in self.__placements.values()

# -----------------------------------------------------------------------------
# class projet
# -----------------------------------------------------------------------------
class Projet:
    def __init__(self):
        self.__nom_projet = ""
        self.__auteur = ""
        self.__date_creation = ""
        self.__nom_magasin = ""
        self.__adresse_magasin = ""
        self.__fichier_sauvegarde = ""
    
    def creer_projet(self, nom_projet: str, auteur: str, nom_magasin: str, adresse_magasin: str):
        from datetime import datetime
        self.__nom_projet = nom_projet
        self.__auteur = auteur
        self.__date_creation = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.__nom_magasin = nom_magasin
        self.__adresse_magasin = adresse_magasin
        self.__fichier_sauvegarde = f"{nom_projet}.json"
    
    def charger_projet(self, chemin_fichier: str) -> bool:
        try:
            if os.path.exists(chemin_fichier):
                with open(chemin_fichier, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.__nom_projet = data.get("nom_projet", "")
                self.__auteur = data.get("auteur", "")
                self.__date_creation = data.get("date_creation", "")
                self.__nom_magasin = data.get("nom_magasin", "")
                self.__adresse_magasin = data.get("adresse_magasin", "")
                self.__fichier_sauvegarde = chemin_fichier
                
                return True
        except Exception as e:
            print(f"Erreur lors du chargement du projet : {e}")
        return False
    
    def sauvegarder_projet(self, plan: Plan, produits: Produits) -> bool:
        try:
            data = {
                "nom_projet": self.__nom_projet,
                "auteur": self.__auteur,
                "date_creation": self.__date_creation,
                "nom_magasin": self.__nom_magasin,
                "adresse_magasin": self.__adresse_magasin,
                "chemin_plan": plan.get_chemin(),
                "nb_rangs": plan.get_nb_rangs(),
                "nb_rayons": plan.get_nb_rayons(),
                "produits_magasin": produits.get_produits_magasin(),
                "placements": {f"{x},{y}": produit for (x, y), produit in produits.get_placements().items()}
            }
            
            with open(self.__fichier_sauvegarde, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")
        return False
    
    def charger_donnees_projet(self, chemin_fichier: str) -> dict:
        try:
            if os.path.exists(chemin_fichier):
                with open(chemin_fichier, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des données : {e}")
        return {}
    
    #mettre nom au projet
    def get_nom_projet(self):
        return self.__nom_projet
    
    # mettre nom auteur du projet
    def get_auteur(self):
        return self.__auteur
    
    #mettre date creation du projet
    def get_date_creation(self):
        return self.__date_creation
    
    #mettre nom au magasin
    def get_nom_magasin(self):
        return self.__nom_magasin
    
    #mettre adresse du magasin
    def get_adresse_magasin(self):
        return self.__adresse_magasin
    
    def get_fichier_sauvegarde(self):
        return self.__fichier_sauvegarde
    
    def set_fichier_sauvegarde(self, chemin: str):
        self.__fichier_sauvegarde = chemin
    
    def est_vide(self) -> bool:
        return self.__nom_projet == ""

# -----------------------------------------------------------------------------
#  class modele MaxiMarket
# -----------------------------------------------------------------------------
class ModeleMaxiMarket:
    def __init__(self):
        self.plan = Plan()
        self.produits = Produits()
        self.projet = Projet()
    #permet de creer un nouveau projet du magasin ( nouveau nom / nouvelle disposition des produit / etc)
    def nouveau_projet(self, nom_projet: str, auteur: str, nom_magasin: str, adresse_magasin: str):
        self.projet.creer_projet(nom_projet, auteur, nom_magasin, adresse_magasin)
        self.plan = Plan()
        self.produits = Produits()
    
    # permet d'utiliser un projet deja existant (plan du magasin / disposition des produits)
    def charger_projet(self, chemin_fichier: str) -> bool:
        if self.projet.charger_projet(chemin_fichier):
            data = self.projet.charger_donnees_projet(chemin_fichier)
            
            if data:
                chemin_plan = data.get("chemin_plan", "")
                if chemin_plan:
                    self.plan.charger_plan(chemin_plan)
                
                self.plan.set_nb_rangs(data.get("nb_rangs", 24))
                self.plan.set_nb_rayons(data.get("nb_rayons", 47))
                
                # Restaurer les produits
                produits_magasin = data.get("produits_magasin", [])
                self.produits.set_produits_magasin(produits_magasin)
                
                # Restaurer les placements
                placements_data = data.get("placements", {})
                for pos_str, produit in placements_data.items():
                    x, y = map(int, pos_str.split(","))
                    self.produits.placer_produit(produit, x, y)
                
                return True
        return False
    
    #permet de sauvegarder les modifs faites sur le projet
    def sauvegarder_projet(self) -> bool:
        return self.projet.sauvegarder_projet(self.plan, self.produits)
    
    # permet de charger un plan de magasin pour un projet
    def charger_plan(self, chemin_plan: str) -> bool:
        return self.plan.charger_plan(chemin_plan)
    
    #permet de chager une liste de produit present dans le magasin que l'on creer
    def charger_produits_depuis_fichier(self, chemin_json: str) -> bool:
        return self.produits.charger_depuis_fichier(chemin_json)
    
    def get_plan(self):
        return self.plan
    
    def get_produits(self):
        return self.produits
    
    def get_projet(self):
        return self.projet

# Programme principal : test du modele
if __name__ == "__main__":
    print('TEST: class ModeleMaxiMarket\n')
    
    modele = ModeleMaxiMarket()
    
    # test creation projet
    modele.nouveau_projet("Test Magasin", "Développeur", "SuperMarché", "123 Rue Test")
    print(f"Projet créé: {modele.projet.get_nom_projet()}")
    
    # test produits
    print(f"Catégories: {modele.produits.get_categories()}")
