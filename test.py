import sys
import os
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsPixmapItem, QGraphicsLineItem
from PyQt6.QtGui import QPen, QPixmap, QColor
from PyQt6.QtCore import Qt

class Scene(QGraphicsScene):

    def __init__(self):
        super().__init__()
        
        #  valeurs du fichier original
        self.nb_rangs = 24
        self.nb_rayons = 47
        
        self.charger_plan()
    
    def charger_plan(self):
        chemin_image = sys.path[0] + "/MaxiMarket/plan.jpg"
        if os.path.exists(chemin_image):
            # Charger l'image
            self.plan = QPixmap(chemin_image)
            self.image = QGraphicsPixmapItem(self.plan)
            self.addItem(self.image)
            self.setSceneRect(0, 0, self.plan.width(), self.plan.height())
            
            # Créer le quadrillage
            self.creer_quadrillage()
    
    def creer_quadrillage(self):
        # Calculs 
        largeur_image = self.plan.width()
        hauteur_image = self.plan.height()
        hauteur_case = hauteur_image / self.nb_rangs
        largeur_case = largeur_image / self.nb_rayons
        
        #  quadrillage
        crayon_rouge = QPen(QColor(255, 0, 0))
        crayon_rouge.setWidth(1)
        
        # Lignes horizontales
        for rang in range(self.nb_rangs + 1):
            y_line = rang * hauteur_case
            ligne = QGraphicsLineItem(0, y_line, largeur_image, y_line)
            ligne.setPen(crayon_rouge)
            self.addItem(ligne)
        
        # Lignes verticales
        for rayon in range(self.nb_rayons + 1):
            x_line = rayon * largeur_case
            ligne = QGraphicsLineItem(x_line, 0, x_line, hauteur_image)
            ligne.setPen(crayon_rouge)
            self.addItem(ligne)

class Rendu(QGraphicsView):

    def __init__(self):
        super().__init__()
        
        scene = Scene()
        self.setScene(scene)
        # Ajuster la vue pour voir toute la scène
        self.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

class MaxiMarketApp(QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("MaxiMarket")
        self.resize(800, 600)
        
        # Créer le rendu graphique
        self.rendu = Rendu()
        self.setCentralWidget(self.rendu)

def main():
    app = QApplication(sys.argv)
    window = MaxiMarketApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
