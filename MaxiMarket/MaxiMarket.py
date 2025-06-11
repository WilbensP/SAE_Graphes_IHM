import sys
import os
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsLineItem, QPushButton, QListWidget
from PyQt6.QtGui import QPen, QPixmap, QColor
from PyQt6.QtCore import Qt

class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        
        # Valeurs du quadrillage
        self.nb_rangs = 24
        self.nb_rayons = 47
        
        self.charger_plan()
    
    def charger_plan(self):
        chemin_image = sys.path[0] + "/MaxiMarket/plan.jpg"
        if os.path.exists(chemin_image):
            self.plan = QPixmap(chemin_image)
            self.image = QGraphicsPixmapItem(self.plan)
            self.addItem(self.image)
            self.setSceneRect(0, 0, self.plan.width(), self.plan.height())
            
            # Créer le quadrillage
            self.creer_quadrillage()
    
    def creer_quadrillage(self):
        largeur_image = self.plan.width()
        hauteur_image = self.plan.height()
        hauteur_case = hauteur_image / self.nb_rangs
        largeur_case = largeur_image / self.nb_rayons
        
        # Crayon pour quadrillage
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
        self.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene():
            self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

class MaxiMarketApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("MaxiMarket - Plan du magasin")
        self.resize(1200, 700)

        # Layout principal 
        main_layout = QHBoxLayout()
        self.rendu = Rendu()
        main_layout.addWidget(self.rendu, stretch=3)

        # === WIDGETS INTERFACE  ===
        # Widget pour afficher la liste des produits
        self.liste_widget = QListWidget()
        
        # Boutons pour la gestion des listes de produits
        self.generer_btn = QPushButton("Générer une liste")
        self.reinitialiser_btn = QPushButton("Réinitialiser")
        self.enregistrer_btn = QPushButton("Enregistrer la liste")

        # Layout vertical 
        side_layout = QVBoxLayout()
        side_layout.addWidget(self.generer_btn)
        side_layout.addWidget(self.liste_widget)
        side_layout.addWidget(self.reinitialiser_btn)
        side_layout.addWidget(self.enregistrer_btn)

        central_widget = QWidget()
        main_layout.addLayout(side_layout, stretch=1)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

def main():
    app = QApplication(sys.argv)
    window = MaxiMarketApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()