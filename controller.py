import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QComboBox, QPushButton, 
                            QMessageBox, QFrame, QGridLayout, QGroupBox)
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt, pyqtSignal
from MaxiMarket import MaxiMarketApp

class MagasinSelector(QWidget):
    magasin_selectionne = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.magasins_disponibles = {
            "MaxiMarket": {
                "nom": "MaxiMarket",
                "plan": "MaxiMarket/plan.jpg",
                "produits": "produits_selectionnes.json",
                "description": "Supermarché MaxiMarket - Plan principal"
            },
            "MaxiMarket_2": {
                "nom": "MaxiMarket Annexe",
                "plan": "MaxiMarket/plan2.jpg",
                "produits": "produits_selectionnes2.json",
                "description": "Supermarché MaxiMarket - Annexe"
            },
            "MaxiMarket_3": {
                "nom": "MaxiMarket Express",
                "plan": "MaxiMarket/plan3.jpg",
                "produits": "produits_selectionnes3.json",
                "description": "Supermarché MaxiMarket - Format Express"
            }
        }
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Titre
        titre = QLabel("Sélection du Magasin")
        titre.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titre)
        
        # Groupe de sélection
        groupe_selection = QGroupBox("Choisir un magasin")
        groupe_layout = QVBoxLayout()
        
        # ComboBox pour sélectionner le magasin
        self.combo_magasins = QComboBox()
        self.combo_magasins.addItem("-- Sélectionner un magasin --", "")
        
        for key, magasin in self.magasins_disponibles.items():
            self.combo_magasins.addItem(magasin["nom"], key)
        
        self.combo_magasins.currentTextChanged.connect(self.on_magasin_change)
        groupe_layout.addWidget(self.combo_magasins)
        
        # Description du magasin sélectionné
        self.label_description = QLabel("Veuillez sélectionner un magasin")
        self.label_description.setWordWrap(True)
        self.label_description.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        groupe_layout.addWidget(self.label_description)
        
        # Informations sur les fichiers
        self.label_fichiers = QLabel("")
        self.label_fichiers.setWordWrap(True)
        self.label_fichiers.setStyleSheet("padding: 5px; color: #666;")
        groupe_layout.addWidget(self.label_fichiers)
        
        groupe_selection.setLayout(groupe_layout)
        layout.addWidget(groupe_selection)
        
        # Boutons d'action
        boutons_layout = QHBoxLayout()
        
        self.btn_ouvrir = QPushButton("Ouvrir le Magasin")
        self.btn_ouvrir.setEnabled(False)
        self.btn_ouvrir.clicked.connect(self.ouvrir_magasin)
        self.btn_ouvrir.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        self.btn_actualiser = QPushButton("Actualiser")
        self.btn_actualiser.clicked.connect(self.actualiser_magasins)
        self.btn_actualiser.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        boutons_layout.addWidget(self.btn_actualiser)
        boutons_layout.addWidget(self.btn_ouvrir)
        layout.addLayout(boutons_layout)
        
        # Statut
        self.label_statut = QLabel("Prêt")
        self.label_statut.setStyleSheet("padding: 5px; background-color: #e8f5e8; border-radius: 3px;")
        layout.addWidget(self.label_statut)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def on_magasin_change(self):
        index = self.combo_magasins.currentIndex()
        if index > 0:  # Pas la première option vide
            key = self.combo_magasins.currentData()
            magasin = self.magasins_disponibles[key]
            
            self.label_description.setText(magasin["description"])
            
            # Vérifier les fichiers
            plan_existe = os.path.exists(sys.path[0] + "/" + magasin["plan"])
            produits_existe = os.path.exists(sys.path[0] + "/" + magasin["produits"])
            
            fichiers_info = f"Plan: {'✓' if plan_existe else '✗'} {magasin['plan']}\n"
            fichiers_info += f"Produits: {'✓' if produits_existe else '✗'} {magasin['produits']}"
            self.label_fichiers.setText(fichiers_info)
            
            # Activer le bouton seulement si les fichiers existent
            self.btn_ouvrir.setEnabled(plan_existe and produits_existe)
            
            if plan_existe and produits_existe:
                self.label_statut.setText("Magasin prêt à être ouvert")
                self.label_statut.setStyleSheet("padding: 5px; background-color: #e8f5e8; border-radius: 3px;")
            else:
                self.label_statut.setText("Fichiers manquants pour ce magasin")
                self.label_statut.setStyleSheet("padding: 5px; background-color: #ffe8e8; border-radius: 3px;")
        else:
            self.label_description.setText("Veuillez sélectionner un magasin")
            self.label_fichiers.setText("")
            self.btn_ouvrir.setEnabled(False)
            self.label_statut.setText("Prêt")
            self.label_statut.setStyleSheet("padding: 5px; background-color: #e8f5e8; border-radius: 3px;")
    
    def ouvrir_magasin(self):
        index = self.combo_magasins.currentIndex()
        if index > 0:
            key = self.combo_magasins.currentData()
            magasin = self.magasins_disponibles[key]
            
            try:
                # Émettre le signal avec le magasin sélectionné
                self.magasin_selectionne.emit(key)
                self.label_statut.setText(f"Ouverture de {magasin['nom']}...")
                self.label_statut.setStyleSheet("padding: 5px; background-color: #fff3cd; border-radius: 3px;")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le magasin:\n{str(e)}")
                self.label_statut.setText("Erreur lors de l'ouverture")
                self.label_statut.setStyleSheet("padding: 5px; background-color: #ffe8e8; border-radius: 3px;")
    
    def actualiser_magasins(self):
        self.label_statut.setText("Actualisation...")
        self.label_statut.setStyleSheet("padding: 5px; background-color: #fff3cd; border-radius: 3px;")
        
        # Recharger la liste (ici on pourrait scanner le dossier pour de nouveaux magasins)
        self.on_magasin_change()
        
        self.label_statut.setText("Liste actualisée")
        self.label_statut.setStyleSheet("padding: 5px; background-color: #e8f5e8; border-radius: 3px;")

class ControleurMaxiMarket(QMainWindow):
    def __init__(self):
        super().__init__()
        self.magasin_actuel = None
        self.app_magasin = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("MaxiMarket - Contrôleur")
        self.setGeometry(100, 100, 500, 400)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # En-tête
        header = QLabel("MaxiMarket - Système de Gestion")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("padding: 20px; background-color: #2196F3; color: white; border-radius: 10px;")
        layout.addWidget(header)
        
        # Sélecteur de magasin
        self.selector = MagasinSelector()
        self.selector.magasin_selectionne.connect(self.ouvrir_application_magasin)
        layout.addWidget(self.selector)
        
        central_widget.setLayout(layout)
        
        # Style de la fenêtre
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def ouvrir_application_magasin(self, magasin_key):
        try:
            # Fermer l'application précédente si elle existe
            if self.app_magasin:
                self.app_magasin.close()
            
            # Configurer l'environnement pour le magasin sélectionné
            self.configurer_magasin(magasin_key)
            
            # Ouvrir la nouvelle application
            self.app_magasin = MaxiMarketApp()
            self.app_magasin.show()
            
            # Mettre à jour le statut
            magasin_nom = self.selector.magasins_disponibles[magasin_key]["nom"]
            self.selector.label_statut.setText(f"{magasin_nom} ouvert avec succès")
            self.selector.label_statut.setStyleSheet("padding: 5px; background-color: #e8f5e8; border-radius: 3px;")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir l'application:\n{str(e)}")
    
    def configurer_magasin(self, magasin_key):
        """Configure l'environnement pour le magasin sélectionné"""
        magasin = self.selector.magasins_disponibles[magasin_key]
        
        # Ici on pourrait modifier les chemins dans maximarket.py
        # ou créer des variables d'environnement
        # Pour l'instant, on utilise les fichiers par défaut
        
        self.magasin_actuel = magasin_key
        print(f"Magasin configuré: {magasin['nom']}")
        print(f"Plan: {magasin['plan']}")
        print(f"Produits: {magasin['produits']}")

def main():
    app = QApplication(sys.argv)
    
    # Définir l'icône de l'application si disponible
    app.setApplicationName("MaxiMarket Controller")
    app.setApplicationVersion("2.0")
    
    controleur = ControleurMaxiMarket()
    controleur.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
