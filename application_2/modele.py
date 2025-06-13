import json
import os
import numpy as np
import math
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPixmap

def copier_fichier(source, destination):
    """Copie un fichier de la source vers la destination"""
    try:
        with open(source, 'rb') as fsrc:
            with open(destination, 'wb') as fdst:
                fdst.write(fsrc.read())
        return True
    except Exception as e:
        print(f"Erreur lors de la copie du fichier: {str(e)}")
        return False

class ProjetModel(QObject):
    """Modèle pour la gestion des projets MaxiMarket"""
    
    projet_charge = pyqtSignal(dict)
    erreur = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.projet_actuel = None
        self.chemin_projet_actuel = None
        self.dossier_projets = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projets")
        if not os.path.exists(self.dossier_projets):
            os.makedirs(self.dossier_projets)
        self.pixmap = None
    
    def charger_projet(self, chemin_json, projet=None):
        """Charge un projet depuis un fichier JSON"""
        try:
            if projet is None:
                with open(chemin_json, "r", encoding="utf-8") as f:
                    projet = json.load(f)
            
            # Validation du format
            if not all(key in projet for key in ["nom_projet", "chemin_plan"]):
                self.erreur.emit("Le fichier JSON ne contient pas les données attendues.")
                return False
            
            # Vérification du plan
            dossier_projet = os.path.dirname(chemin_json)
            chemin_plan = os.path.join(dossier_projet, projet["chemin_plan"])
            
            if os.path.exists(chemin_plan):
                projet["chemin_plan_absolu"] = chemin_plan
                self.pixmap = QPixmap(chemin_plan)
            
            self.chemin_projet_actuel = chemin_json
            self.projet_actuel = projet
            self.projet_charge.emit(projet)
            return True
            
        except Exception as e:
            self.erreur.emit(f"Impossible de charger le projet: {str(e)}")
            return False
    
    def get_projet_actuel(self):
        """Retourne le projet actuellement chargé"""
        return self.projet_actuel
    
    def get_chemin_projet_actuel(self):
        """Retourne le chemin du projet actuellement chargé"""
        return self.chemin_projet_actuel
    
    def get_projets_disponibles(self):
        """Retourne la liste des projets disponibles"""
        projets = []
        
        # Chercher les fichiers .json dans le répertoire courant et le dossier projets
        dossiers = ['.', self.dossier_projets]
        for dossier in dossiers:
            if os.path.exists(dossier):
                for fichier in os.listdir(dossier):
                    chemin_fichier = os.path.join(dossier, fichier)
                    if fichier.endswith('.json') and os.path.isfile(chemin_fichier):
                        try:
                            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if 'nom_projet' in data and 'nom_magasin' in data:
                                    projets.append({
                                        'fichier': chemin_fichier,
                                        'nom_projet': data['nom_projet'],
                                        'nom_magasin': data['nom_magasin']
                                    })
                        except:
                            pass
        
        return projets

class ProduitsModel(QObject):
    """Modèle pour la gestion des produits et listes de courses"""
    
    produits_charges = pyqtSignal(list)
    liste_generee = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.tous_produits = []
        self.liste_courses = []
    
    def charger_produits(self, produits):
        """Charge la liste des produits"""
        self.tous_produits = sorted(produits)
        self.produits_charges.emit(self.tous_produits)
        return self.tous_produits
    
    def generer_liste_aleatoire(self, nombre_produits=10):
        """Génère une liste aléatoire de produits"""
        if not self.tous_produits:
            return []
        
        n = min(nombre_produits, len(self.tous_produits))
        choix = np.random.choice(self.tous_produits, n, replace=False).tolist()
        self.liste_courses = choix
        self.liste_generee.emit(choix)
        return choix
    
    def ajouter_produit_liste(self, produit):
        """Ajoute un produit à la liste de courses"""
        if produit not in self.liste_courses:
            self.liste_courses.append(produit)
            return True
        return False
    
    def supprimer_produit_liste(self, produit):
        """Supprime un produit de la liste de courses"""
        if produit in self.liste_courses:
            self.liste_courses.remove(produit)
            return True
        return False
    
    def reinitialiser_liste(self):
        """Remet à zéro la liste de courses"""
        self.liste_courses = []
    
    def get_tous_produits(self):
        """Retourne tous les produits"""
        return self.tous_produits
    
    def get_liste_courses(self):
        """Retourne la liste de courses actuelle"""
        return self.liste_courses
    
    def sauvegarder_liste(self, chemin_fichier, nom_magasin="MaxiMarket"):
        """Sauvegarde la liste de courses dans un fichier"""
        try:
            with open(chemin_fichier, "w", encoding="utf-8") as f:
                f.write(f"Liste de courses - {nom_magasin}\n")
                f.write("-" * 40 + "\n")
                for produit in self.liste_courses:
                    f.write(produit + "\n")
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {str(e)}")
            return False

class CalculChemin:
    """Classe pour calculer le chemin optimal entre les produits"""
    def __init__(self, point_depart=(28, 21)):
        self.point_depart = point_depart
    
    def calculer_distance(self, pos1, pos2):
        """Calcule la distance euclidienne entre deux positions"""
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def calculer_chemin_optimal(self, produits, positions):
        """Calcule le chemin optimal pour récupérer tous les produits
        
        Utilise l'algorithme du plus proche voisin (greedy)
        """
        if not produits or not positions:
            return []
        
        # Algorithme du plus proche voisin
        chemin = []
        produits_restants = list(produits)
        position_courante = self.point_depart
        
        while produits_restants:
            # Trouver le produit le plus proche
            produit_plus_proche = None
            distance_min = float('inf')
            
            for produit in produits_restants:
                for coord, nom in positions.items():
                    if nom == produit:
                        x, y = map(int, coord.split(','))
                        pos = (x, y)
                        distance = self.calculer_distance(position_courante, pos)
                        
                        if distance < distance_min:
                            distance_min = distance
                            produit_plus_proche = produit
                            position_plus_proche = pos
            
            # Ajouter le produit au chemin
            if produit_plus_proche:
                chemin.append((produit_plus_proche, position_plus_proche))
                position_courante = position_plus_proche
                produits_restants.remove(produit_plus_proche)
        
        return chemin
