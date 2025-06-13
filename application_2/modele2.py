import os
import json
import math
from PyQt6.QtGui import QPixmap

class Magasin:
    """Classe représentant un magasin avec son plan et ses produits"""
    def __init__(self):
        self.nom = ""
        self.adresse = ""
        self.chemin_plan = ""
        self.nb_rangs = 24
        self.nb_rayons = 47
        self.pixmap = None
        self.produits_places = {}  # {(x, y): nom_produit}
    
    def charger_depuis_fichier(self, chemin_fichier):
        """Charge les données d'un magasin depuis un fichier de projet"""
        try:
            if os.path.exists(chemin_fichier):
                with open(chemin_fichier, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.nom = data.get("nom_magasin", "")
                self.adresse = data.get("adresse_magasin", "")
                self.chemin_plan = data.get("chemin_plan", "")
                self.nb_rangs = data.get("nb_rangs", 24)
                self.nb_rayons = data.get("nb_rayons", 47)
                
                # Charger le plan
                if self.chemin_plan and os.path.exists(self.chemin_plan):
                    self.pixmap = QPixmap(self.chemin_plan)
                
                # Charger les placements de produits
                placements_data = data.get("placements", {})
                self.produits_places = {}
                for pos_str, produit in placements_data.items():
                    x, y = map(int, pos_str.split(","))
                    self.produits_places[(x, y)] = produit
                
                return True
        except Exception as e:
            print(f"Erreur lors du chargement du magasin: {e}")
        return False
    
    def get_produits_disponibles(self):
        """Retourne la liste des produits disponibles dans le magasin"""
        return list(set(self.produits_places.values()))
    
    def get_position_produit(self, produit):
        """Retourne la position d'un produit dans le magasin"""
        for pos, nom in self.produits_places.items():
            if nom == produit:
                return pos
        return None

class ListeCourses:
    """Classe représentant une liste de courses"""
    def __init__(self):
        self.nom = "Nouvelle liste"
        self.produits = []  # Liste des produits à acheter
    
    def ajouter_produit(self, produit):
        """Ajoute un produit à la liste de courses"""
        if produit not in self.produits:
            self.produits.append(produit)
            return True
        return False
    
    def supprimer_produit(self, produit):
        """Supprime un produit de la liste de courses"""
        if produit in self.produits:
            self.produits.remove(produit)
            return True
        return False
    
    def vider_liste(self):
        """Vide la liste de courses"""
        self.produits = []
    
    def sauvegarder(self, chemin_fichier):
        """Sauvegarde la liste de courses dans un fichier JSON"""
        try:
            data = {
                "nom": self.nom,
                "produits": self.produits
            }
            
            with open(chemin_fichier, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la liste: {e}")
            return False
    
    def charger(self, chemin_fichier):
        """Charge une liste de courses depuis un fichier JSON"""
        try:
            if os.path.exists(chemin_fichier):
                with open(chemin_fichier, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.nom = data.get("nom", "Liste chargée")
                self.produits = data.get("produits", [])
                
                return True
        except Exception as e:
            print(f"Erreur lors du chargement de la liste: {e}")
        return False

class CalculChemin:
    """Classe pour calculer le chemin optimal entre les produits"""
    def __init__(self, magasin):
        self.magasin = magasin
    
    def calculer_distance(self, pos1, pos2):
        """Calcule la distance euclidienne entre deux positions"""
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def calculer_chemin_optimal(self, liste_courses, position_depart=(0, 0)):
        """Calcule le chemin optimal pour récupérer tous les produits de la liste
        
        Utilise l'algorithme du plus proche voisin (greedy)
        """
        # Récupérer les positions des produits de la liste
        positions = {}
        for produit in liste_courses.produits:
            pos = self.magasin.get_position_produit(produit)
            if pos:
                positions[produit] = pos
        
        if not positions:
            return []
        
        # Algorithme du plus proche voisin
        chemin = []
        produits_restants = list(positions.keys())
        position_courante = position_depart
        
        while produits_restants:
            # Trouver le produit le plus proche
            produit_plus_proche = None
            distance_min = float('inf')
            
            for produit in produits_restants:
                pos = positions[produit]
                distance = self.calculer_distance(position_courante, pos)
                
                if distance < distance_min:
                    distance_min = distance
                    produit_plus_proche = produit
            
            # Ajouter le produit au chemin
            if produit_plus_proche:
                chemin.append((produit_plus_proche, positions[produit_plus_proche]))
                position_courante = positions[produit_plus_proche]
                produits_restants.remove(produit_plus_proche)
        
        return chemin

class ModeleApp2:
    """Classe principale du modèle pour l'application 2"""
    def __init__(self):
        self.magasin = Magasin()
        self.liste_courses = ListeCourses()
        self.calcul_chemin = None
    
    def charger_magasin(self, chemin_fichier):
        """Charge un magasin depuis un fichier de projet"""
        success = self.magasin.charger_depuis_fichier(chemin_fichier)
        if success:
            self.calcul_chemin = CalculChemin(self.magasin)
        return success
    
    def get_projets_disponibles(self):
        """Retourne la liste des projets disponibles"""
        projets = []
        
        # Chercher les fichiers .json dans le répertoire courant
        for fichier in os.listdir('.'):
            if fichier.endswith('.json') and fichier != 'produits_selectionnes.json':
                try:
                    with open(fichier, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'nom_projet' in data and 'nom_magasin' in data:
                            projets.append({
                                'fichier': fichier,
                                'nom_projet': data['nom_projet'],
                                'nom_magasin': data['nom_magasin']
                            })
                except:
                    pass
        
        return projets
    
    def ajouter_produit_liste(self, produit):
        """Ajoute un produit à la liste de courses"""
        return self.liste_courses.ajouter_produit(produit)
    
    def supprimer_produit_liste(self, produit):
        """Supprime un produit de la liste de courses"""
        return self.liste_courses.supprimer_produit(produit)
    
    def vider_liste_courses(self):
        """Vide la liste de courses"""
        self.liste_courses.vider_liste()
    
    def calculer_chemin_optimal(self):
        """Calcule le chemin optimal pour la liste de courses actuelle"""
        if self.calcul_chemin:
            return self.calcul_chemin.calculer_chemin_optimal(self.liste_courses)
        return []
    
    def sauvegarder_liste(self, chemin_fichier):
        """Sauvegarde la liste de courses"""
        return self.liste_courses.sauvegarder(chemin_fichier)
    
    def charger_liste(self, chemin_fichier):
        """Charge une liste de courses"""
        return self.liste_courses.charger(chemin_fichier)

# Test du modèle
if __name__ == "__main__":
    modele = ModeleApp2()
    projets = modele.get_projets_disponibles()
    print(f"Projets disponibles: {projets}")
    
    if projets:
        modele.charger_magasin(projets[0]['fichier'])
        print(f"Magasin chargé: {modele.magasin.nom}")
        print(f"Produits disponibles: {modele.magasin.get_produits_disponibles()}")
