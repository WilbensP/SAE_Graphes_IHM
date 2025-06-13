import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsLineItem, 
                            QGraphicsRectItem, QPushButton, QListWidget, QComboBox, QLabel, 
                            QSpinBox, QDialog, QFormLayout, QLineEdit, QTextEdit, QCheckBox, 
                            QGroupBox, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, 
                            QMessageBox, QSplitter, QFrame)
from PyQt6.QtGui import QPen, QColor, QBrush, QFont, QIcon, QPixmap, QPalette, QLinearGradient
from PyQt6.QtCore import Qt, pyqtSignal, QSize

# -----------------------------------------------------------------------------
# --- class SceneGraphique
# -----------------------------------------------------------------------------
class SceneGraphique(QGraphicsScene):
    produit_place = pyqtSignal(str, int, int)  
    
    def __init__(self):
        super().__init__()
        self.plan_item = None
        self.lignes_quadrillage = []
        self.rectangles_produits = []
        self.produit_a_placer = None
        self.nb_rangs = 24
        self.nb_rayons = 47
    
    def afficher_plan(self, pixmap, nb_rangs, nb_rayons):
        self.clear()
        self.lignes_quadrillage.clear()
        self.rectangles_produits.clear()
        
        self.nb_rangs = nb_rangs
        self.nb_rayons = nb_rayons
        
        if pixmap:
            self.plan_item = QGraphicsPixmapItem(pixmap)
            self.addItem(self.plan_item)
            self.setSceneRect(0, 0, pixmap.width(), pixmap.height())
            self.creer_quadrillage(pixmap.width(), pixmap.height(), nb_rangs, nb_rayons)
    
    def creer_quadrillage(self, largeur, hauteur, nb_rangs, nb_rayons):
        hauteur_case = hauteur / nb_rangs
        largeur_case = largeur / nb_rayons
        
        # Utiliser un crayon semi-transparent pour le quadrillage
        crayon_quadrillage = QPen(QColor(70, 130, 180, 150))  # Bleu acier semi-transparent
        crayon_quadrillage.setWidth(1)
        
        # Lignes horizontales
        for rang in range(nb_rangs + 1):
            y_line = rang * hauteur_case
            ligne = QGraphicsLineItem(0, y_line, largeur, y_line)
            ligne.setPen(crayon_quadrillage)
            self.addItem(ligne)
            self.lignes_quadrillage.append(ligne)
        
        # Lignes verticales
        for rayon in range(nb_rayons + 1):
            x_line = rayon * largeur_case
            ligne = QGraphicsLineItem(x_line, 0, x_line, hauteur)
            ligne.setPen(crayon_quadrillage)
            self.addItem(ligne)
            self.lignes_quadrillage.append(ligne)
    
    def afficher_placements(self, placements):
        for rect in self.rectangles_produits:
            self.removeItem(rect)
        self.rectangles_produits.clear()
        
        if not self.plan_item:
            return
        
        largeur = self.plan_item.pixmap().width()
        hauteur = self.plan_item.pixmap().height()
        largeur_case = largeur / self.nb_rayons
        hauteur_case = hauteur / self.nb_rangs
        
        # Ajouter les nouveaux rectangles avec un style amélioré
        for (x, y), produit in placements.items():
            rect_x = x * largeur_case
            rect_y = y * hauteur_case
            
            rect = QGraphicsRectItem(rect_x, rect_y, largeur_case, hauteur_case)
            
            # Utiliser une couleur différente selon le produit (basée sur le hash du nom)
            hue = hash(produit) % 360
            rect.setBrush(QBrush(QColor.fromHsv(hue, 120, 230, 150)))  # Couleur semi-transparente
            rect.setPen(QPen(QColor.fromHsv(hue, 200, 255), 2))
            
            self.addItem(rect)
            self.rectangles_produits.append(rect)
    
    def set_produit_a_placer(self, produit):
        self.produit_a_placer = produit
    
    def mousePressEvent(self, event):
        if not self.produit_a_placer or not self.plan_item:
            return
        
        # Calculer la position dans la grille
        pos = event.scenePos()
        largeur = self.plan_item.pixmap().width()
        hauteur = self.plan_item.pixmap().height()
        
        largeur_case = largeur / self.nb_rayons
        hauteur_case = hauteur / self.nb_rangs
        
        x = int(pos.x() // largeur_case)
        y = int(pos.y() // hauteur_case)
        
        # Vérifier les limites
        if 0 <= x < self.nb_rayons and 0 <= y < self.nb_rangs:
            self.produit_place.emit(self.produit_a_placer, x, y)
            self.produit_a_placer = None

# -----------------------------------------------------------------------------
# --- class VueGraphique
# -----------------------------------------------------------------------------
class VueGraphique(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene_graphique = SceneGraphique()
        self.setScene(self.scene_graphique)
        
        # Améliorer l'apparence de la vue graphique
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        
        # Ajouter un fond agréable
        self.setBackgroundBrush(QBrush(QColor(240, 240, 245)))
        
        # Ajouter une bordure
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setLineWidth(1)
    
    def afficher_plan(self, pixmap, nb_rangs, nb_rayons):
        self.scene_graphique.afficher_plan(pixmap, nb_rangs, nb_rayons)
        self.fitInView(self.scene_graphique.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def afficher_placements(self, placements):
        self.scene_graphique.afficher_placements(placements)
    
    def set_produit_a_placer(self, produit):
        self.scene_graphique.set_produit_a_placer(produit)
        
        # Changer le curseur pour indiquer le mode placement
        if produit:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene_graphique.sceneRect():
            self.fitInView(self.scene_graphique.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

# -----------------------------------------------------------------------------
# --- class DialogNouveauProjet
# -----------------------------------------------------------------------------
class DialogNouveauProjet(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouveau Projet")
        self.setModal(True)
        self.resize(450, 350)
        
        # Appliquer un style moderne
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f7;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                background-color: #4a86e8;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
            QLabel {
                font-weight: bold;
            }
        """)
        
        layout = QFormLayout()
        
        # Titre du dialogue
        titre = QLabel("Créer un nouveau projet")
        titre.setStyleSheet("font-size: 16pt; margin-bottom: 15px; color: #333;")
        layout.addRow(titre)
        
        self.nom_projet = QLineEdit()
        self.auteur = QLineEdit()
        self.nom_magasin = QLineEdit()
        self.adresse_magasin = QTextEdit()
        self.adresse_magasin.setMaximumHeight(80)
        
        layout.addRow("Nom du projet:", self.nom_projet)
        layout.addRow("Auteur:", self.auteur)
        layout.addRow("Nom du magasin:", self.nom_magasin)
        layout.addRow("Adresse du magasin:", self.adresse_magasin)
        
        # Boutons
        boutons_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Créer")
        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.setStyleSheet("background-color: #f0f0f0; color: #333;")
        
        boutons_layout.addWidget(self.btn_annuler)
        boutons_layout.addWidget(self.btn_ok)
        
        layout.addRow(boutons_layout)
        self.setLayout(layout)
        
        # Connexions
        self.btn_ok.clicked.connect(self.accept)
        self.btn_annuler.clicked.connect(self.reject)
    
    def get_data(self):
        return {
            'nom_projet': self.nom_projet.text(),
            'auteur': self.auteur.text(),
            'nom_magasin': self.nom_magasin.text(),
            'adresse_magasin': self.adresse_magasin.toPlainText()
        }

# -----------------------------------------------------------------------------
# --- class DialogSelectionProduits
# -----------------------------------------------------------------------------
class DialogSelectionProduits(QDialog):
    def __init__(self, categories_produits, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sélection des produits du magasin")
        self.setModal(True)
        self.resize(650, 550)
        
        # Style moderne
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f7;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #4a86e8;
            }
            QCheckBox {
                padding: 4px;
            }
            QCheckBox:hover {
                background-color: #f0f0f0;
                border-radius: 3px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                background-color: #4a86e8;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
        """)
        
        self.categories_produits = categories_produits
        self.checkboxes = {}
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Instructions
        label = QLabel("Sélectionnez les produits vendus dans ce magasin :")
        label.setStyleSheet("font-size: 14pt; margin-bottom: 10px; color: #333;")
        layout.addWidget(label)
        
        # Zone de défilement
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(10)
        
        # Créer les groupes par catégorie
        for categorie, produits in self.categories_produits.items():
            group = QGroupBox(categorie)
            group_layout = QVBoxLayout()
            
            # Ajouter un bouton pour tout sélectionner/désélectionner
            select_all_layout = QHBoxLayout()
            select_all = QPushButton("Tout sélectionner")
            select_all.setStyleSheet("padding: 4px 8px; font-size: 9pt; background-color: #e0e0e0; color: #333;")
            select_all.setFixedWidth(120)
            select_none = QPushButton("Tout désélectionner")
            select_none.setStyleSheet("padding: 4px 8px; font-size: 9pt; background-color: #e0e0e0; color: #333;")
            select_none.setFixedWidth(120)
            
            select_all_layout.addWidget(select_all)
            select_all_layout.addWidget(select_none)
            select_all_layout.addStretch()
            group_layout.addLayout(select_all_layout)
            
            # Cases à cocher produit
            for produit in produits:
                cb = QCheckBox(produit)
                self.checkboxes[produit] = cb
                group_layout.addWidget(cb)
            
            group.setLayout(group_layout)
            scroll_layout.addWidget(group)
            
            # Connecter les boutons de sélection
            select_all.clicked.connect(lambda checked, cat=categorie: self.toggle_categorie(cat, True))
            select_none.clicked.connect(lambda checked, cat=categorie: self.toggle_categorie(cat, False))
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Boutons
        boutons_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Valider")
        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.setStyleSheet("background-color: #f0f0f0; color: #333;")
        
        boutons_layout.addWidget(self.btn_annuler)
        boutons_layout.addWidget(self.btn_ok)
        
        layout.addLayout(boutons_layout)
        self.setLayout(layout)
        
        # Connexions
        self.btn_ok.clicked.connect(self.accept)
        self.btn_annuler.clicked.connect(self.reject)
    
    def toggle_categorie(self, categorie, state):
        for produit in self.categories_produits[categorie]:
            if produit in self.checkboxes:
                self.checkboxes[produit].setChecked(state)
    
    def get_produits_selectionnes(self):
        return [produit for produit, cb in self.checkboxes.items() if cb.isChecked()]

# -----------------------------------------------------------------------------
# --- class StyledButton
# -----------------------------------------------------------------------------
class StyledButton(QPushButton):
    def __init__(self, text, icon_name=None, color="#4a86e8"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 12px;
                border-radius: 4px;
                background-color: {color};
                color: white;
                font-weight: bold;
                text-align: left;
                padding-left: 36px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color, 10)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 20)};
            }}
        """)
        
        if icon_name:
            self.setIcon(QIcon(f"icons/{icon_name}.png"))
            self.setIconSize(QSize(20, 20))
    
    def darken_color(self, hex_color, percent):
        """Assombrir une couleur hex d'un pourcentage donné"""
        # Convertir hex en RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Assombrir
        factor = 1 - percent/100
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))
        
        # Reconvertir en hex
        return f"#{r:02x}{g:02x}{b:02x}"

# -----------------------------------------------------------------------------
# --- class PanneauControle
# -----------------------------------------------------------------------------
class PanneauControle(QWidget):
    # Signaux
    signal_nouveau_projet = pyqtSignal()
    signal_ouvrir_projet = pyqtSignal()
    signal_sauvegarder_projet = pyqtSignal()
    signal_supprimer_projet = pyqtSignal()
    signal_charger_plan = pyqtSignal()
    signal_selectionner_produits = pyqtSignal()
    signal_quadrillage_change = pyqtSignal(int, int)
    signal_produit_selectionne_placement = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Appliquer un style global
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #4a86e8;
            }
            QLabel {
                color: #333;
            }
            QSpinBox {
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QListWidget, QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            QListWidget::item:selected, QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #333;
            }
            QListWidget::item:hover, QTableWidget::item:hover {
                background-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Gestion du projet
        projet_group = QGroupBox("Projet")
        projet_layout = QVBoxLayout()
        
        self.btn_nouveau_projet = StyledButton("Nouveau Projet", "new", "#4CAF50")
        self.btn_ouvrir_projet = StyledButton("Ouvrir Projet", "open", "#2196F3")
        self.btn_sauvegarder_projet = StyledButton("Sauvegarder Projet", "save", "#FF9800")
        self.btn_supprimer_projet = StyledButton("Supprimer Projet", "delete", "#F44336")
        
        self.btn_nouveau_projet.clicked.connect(self.signal_nouveau_projet.emit)
        self.btn_ouvrir_projet.clicked.connect(self.signal_ouvrir_projet.emit)
        self.btn_sauvegarder_projet.clicked.connect(self.signal_sauvegarder_projet.emit)
        self.btn_supprimer_projet.clicked.connect(self.signal_supprimer_projet.emit)
        
        projet_layout.addWidget(self.btn_nouveau_projet)
        projet_layout.addWidget(self.btn_ouvrir_projet)
        projet_layout.addWidget(self.btn_sauvegarder_projet)
        projet_layout.addWidget(self.btn_supprimer_projet)
        
        projet_group.setLayout(projet_layout)
        layout.addWidget(projet_group)
        
        # Informations du projet
        self.label_projet_info = QLabel("Aucun projet ouvert")
        self.label_projet_info.setStyleSheet("""
            font-weight: bold; 
            padding: 10px; 
            background-color: #e3f2fd; 
            border-radius: 4px;
            border-left: 4px solid #2196F3;
        """)
        layout.addWidget(self.label_projet_info)
        
        # Gestion du plan
        plan_group = QGroupBox("Plan du Magasin")
        plan_layout = QVBoxLayout()
        
        self.btn_charger_plan = StyledButton("Charger Plan", "map", "#673AB7")
        self.btn_charger_plan.clicked.connect(self.signal_charger_plan.emit)
        plan_layout.addWidget(self.btn_charger_plan)
        
        self.label_plan_info = QLabel("Aucun plan chargé")
        self.label_plan_info.setStyleSheet("""
            padding: 8px; 
            background-color: #f3e5f5; 
            border-radius: 4px;
            border-left: 4px solid #9C27B0;
        """)
        plan_layout.addWidget(self.label_plan_info)
        
        # Contrôles du quadrillage
        quad_group = QGroupBox("Paramètres du quadrillage")
        quad_layout = QHBoxLayout()
        
        quad_layout.addWidget(QLabel("Rangs:"))
        self.spin_rangs = QSpinBox()
        self.spin_rangs.setRange(10, 50)
        self.spin_rangs.setValue(24)
        self.spin_rangs.valueChanged.connect(self.on_quadrillage_change)
        quad_layout.addWidget(self.spin_rangs)
        
        quad_layout.addWidget(QLabel("Rayons:"))
        self.spin_rayons = QSpinBox()
        self.spin_rayons.setRange(10, 100)
        self.spin_rayons.setValue(47)
        self.spin_rayons.valueChanged.connect(self.on_quadrillage_change)
        quad_layout.addWidget(self.spin_rayons)
        
        quad_group.setLayout(quad_layout)
        plan_layout.addWidget(quad_group)
        
        plan_group.setLayout(plan_layout)
        layout.addWidget(plan_group)
        
        # Gestion des produits
        produits_group = QGroupBox("Produits du Magasin")
        produits_layout = QVBoxLayout()
        
        self.btn_selectionner_produits = StyledButton("Sélectionner Produits", "products", "#009688")
        self.btn_selectionner_produits.clicked.connect(self.signal_selectionner_produits.emit)
        produits_layout.addWidget(self.btn_selectionner_produits)
        
        # Ajouter une étiquette d'instruction
        instruction = QLabel("Cliquez sur un produit non placé pour le positionner sur le plan")
        instruction.setStyleSheet("font-style: italic; color: #666; margin-top: 5px;")
        produits_layout.addWidget(instruction)
        
        self.liste_produits = QListWidget()
        self.liste_produits.setAlternatingRowColors(True)
        self.liste_produits.itemClicked.connect(self.on_produit_selectionne)
        produits_layout.addWidget(self.liste_produits)
        
        produits_group.setLayout(produits_layout)
        layout.addWidget(produits_group)
        
        # Table des placements
        placement_group = QGroupBox("Produits Placés")
        placement_layout = QVBoxLayout()
        
        self.table_placements = QTableWidget()
        self.table_placements.setColumnCount(3)
        self.table_placements.setHorizontalHeaderLabels(["Produit", "X", "Y"])
        self.table_placements.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_placements.setAlternatingRowColors(True)
        
        placement_layout.addWidget(self.table_placements)
        placement_group.setLayout(placement_layout)
        layout.addWidget(placement_group)
        
        self.setLayout(layout)
    
    def on_quadrillage_change(self):
        self.signal_quadrillage_change.emit(self.spin_rangs.value(), self.spin_rayons.value())
    
    def on_produit_selectionne(self, item):
        texte = item.text()
        if "(non placé)" in texte:
            produit = texte.replace(" (non placé)", "")
            self.signal_produit_selectionne_placement.emit(produit)
            item.setBackground(QColor("#e8f5e9"))  # Mettre en évidence l'élément sélectionné
    
    # Méthodes de mise à jour
    def mettre_a_jour_projet_info(self, info):
        self.label_projet_info.setText(info)
    
    def mettre_a_jour_plan_info(self, info):
        self.label_plan_info.setText(info)
    
    def mettre_a_jour_produits(self, produits_magasin, placements):
        self.liste_produits.clear()
        for produit in produits_magasin:
            est_place = any(p == produit for p in placements.values())
            item = QListWidgetItem()
            
            if est_place:
                pos = next((f"({x},{y})" for (x, y), p in placements.items() if p == produit), "")
                item.setText(f"{produit} {pos}")
                item.setIcon(QIcon("icons/check.png"))
                item.setBackground(QColor("#e3f2fd"))  # Bleu clair pour les produits placés
            else:
                item.setText(f"{produit} (non placé)")
                item.setIcon(QIcon("icons/add.png"))
                item.setBackground(QColor("#fff8e1"))  # Jaune clair pour les produits non placés
            
            self.liste_produits.addItem(item)
    
    def mettre_a_jour_table_placements(self, placements):
        self.table_placements.setRowCount(len(placements))
        for i, ((x, y), produit) in enumerate(placements.items()):
            self.table_placements.setItem(i, 0, QTableWidgetItem(produit))
            self.table_placements.setItem(i, 1, QTableWidgetItem(str(x)))
            self.table_placements.setItem(i, 2, QTableWidgetItem(str(y)))
            
            # Colorer les lignes selon le produit (basé sur le hash du nom)
            hue = hash(produit) % 360
            color = QColor.fromHsv(hue, 40, 255)  # Couleur légère
            
            for j in range(3):
                self.table_placements.item(i, j).setBackground(color)
    
    def set_quadrillage_values(self, rangs, rayons):
        self.spin_rangs.setValue(rangs)
        self.spin_rayons.setValue(rayons)

# -----------------------------------------------------------------------------
# --- class VueMaxiMarket
# -----------------------------------------------------------------------------
class VueMaxiMarket(QMainWindow):
    # Signaux vers l'extérieur
    signal_nouveau_projet = pyqtSignal()
    signal_ouvrir_projet = pyqtSignal()
    signal_sauvegarder_projet = pyqtSignal()
    signal_charger_plan = pyqtSignal()
    signal_selectionner_produits = pyqtSignal()
    signal_quadrillage_change = pyqtSignal(int, int)
    signal_produit_selectionne_placement = pyqtSignal(str)
    signal_produit_place = pyqtSignal(str, int, int)
    signal_supprimer_projet = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Créer les dossiers nécessaires pour les icônes
        import os
        if not os.path.exists("icons"):
            os.makedirs("icons")
            
        # Créer des icônes simples pour les boutons
        self.create_simple_icons()
        
        self.init_ui()
    
    def create_simple_icons(self):
        """Crée des icônes simples pour les boutons"""
        icons = {
            "new": (QColor(76, 175, 80), "N"),
            "open": (QColor(33, 150, 243), "O"),
            "save": (QColor(255, 152, 0), "S"),
            "delete": (QColor(244, 67, 54), "D"),
            "map": (QColor(103, 58, 183), "M"),
            "products": (QColor(0, 150, 136), "P"),
            "check": (QColor(76, 175, 80), "✓"),
            "add": (QColor(255, 193, 7), "+")
        }
        
        for name, (color, text) in icons.items():
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Dessiner un cercle de fond
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawEllipse(2, 2, 20, 20)
            
            # Dessiner le texte
            painter.setPen(Qt.GlobalColor.white)
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
            
            painter.end()
            
            # Sauvegarder l'icône
            pixmap.save(f"icons/{name}.png")
    
    def init_ui(self):
        self.setWindowTitle("MaxiMarket - Gestionnaire de Projets")
        self.resize(1400, 800)
        
        # Appliquer un style global à la fenêtre principale
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
            }
            QSplitter::handle {
                background-color: #ddd;
            }
            QStatusBar {
                background-color: #4a86e8;
                color: white;
                font-weight: bold;
            }
        """)
        
        # Widget central avec splitter
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Vue graphique dans un cadre
        vue_frame = QFrame()
        vue_frame.setFrameShape(QFrame.Shape.StyledPanel)
        vue_frame.setFrameShadow(QFrame.Shadow.Raised)
        vue_layout = QVBoxLayout(vue_frame)
        
        # Titre de la vue
        titre_plan = QLabel("Plan du Magasin")
        titre_plan.setStyleSheet("font-size: 14pt; font-weight: bold; color: #333; margin-bottom: 5px;")
        vue_layout.addWidget(titre_plan)
        
        # Vue graphique
        self.vue_graphique = VueGraphique()
        vue_layout.addWidget(self.vue_graphique)
        
        # Panneau de contrôle
        self.panneau_controle = PanneauControle()
        
        # Ajouter les widgets au splitter
        splitter.addWidget(vue_frame)
        splitter.addWidget(self.panneau_controle)
        
        # Définir les tailles relatives des widgets dans le splitter
        splitter.setSizes([700, 300])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Barre d'état
        self.statusBar().showMessage("Prêt")
        
        # Connexion des signaux
        self.panneau_controle.signal_nouveau_projet.connect(self.signal_nouveau_projet.emit)
        self.panneau_controle.signal_ouvrir_projet.connect(self.signal_ouvrir_projet.emit)
        self.panneau_controle.signal_sauvegarder_projet.connect(self.signal_sauvegarder_projet.emit)
        self.panneau_controle.signal_charger_plan.connect(self.signal_charger_plan.emit)
        self.panneau_controle.signal_selectionner_produits.connect(self.signal_selectionner_produits.emit)
        self.panneau_controle.signal_quadrillage_change.connect(self.signal_quadrillage_change.emit)
        self.panneau_controle.signal_produit_selectionne_placement.connect(self.signal_produit_selectionne_placement.emit)
        self.panneau_controle.signal_supprimer_projet.connect(self.signal_supprimer_projet.emit)
        self.vue_graphique.scene_graphique.produit_place.connect(self.on_produit_place)
    
    def on_produit_place(self, produit, x, y):
        self.signal_produit_place.emit(produit, x, y)
        self.statusBar().showMessage(f"Produit '{produit}' placé en position ({x}, {y})", 3000)
    
    # Méthodes de mise à jour de la vue
    def afficher_plan(self, pixmap, nb_rangs, nb_rayons):
        self.vue_graphique.afficher_plan(pixmap, nb_rangs, nb_rayons)
        if pixmap:
            self.statusBar().showMessage("Plan chargé avec succès", 3000)
    
    def afficher_placements(self, placements):
        self.vue_graphique.afficher_placements(placements)
    
    def set_produit_a_placer(self, produit):
        self.vue_graphique.set_produit_a_placer(produit)
        if produit:
            self.statusBar().showMessage(f"Cliquez sur le plan pour placer '{produit}'", 3000)
    
    def mettre_a_jour_projet_info(self, info):
        self.panneau_controle.mettre_a_jour_projet_info(info)
        if "Aucun projet" not in info:
            self.setWindowTitle(f"MaxiMarket - {info}")
        else:
            self.setWindowTitle("MaxiMarket - Gestionnaire de Projets")
    
    def mettre_a_jour_plan_info(self, info):
        self.panneau_controle.mettre_a_jour_plan_info(info)
    
    def mettre_a_jour_produits(self, produits_magasin, placements):
        self.panneau_controle.mettre_a_jour_produits(produits_magasin, placements)
    
    def mettre_a_jour_table_placements(self, placements):
        self.panneau_controle.mettre_a_jour_table_placements(placements)
    
    def set_quadrillage_values(self, rangs, rayons):
        self.panneau_controle.set_quadrillage_values(rangs, rayons)
    
    def show_dialog_nouveau_projet(self):
        dialog = DialogNouveauProjet(self)
        return dialog.exec(), dialog.get_data() if dialog.result() else None
    
    def show_dialog_selection_produits(self, categories_produits):
        dialog = DialogSelectionProduits(categories_produits, self)
        return dialog.exec(), dialog.get_produits_selectionnes() if dialog.result() else None

# Ajouter la classe QPainter qui était manquante
from PyQt6.QtGui import QPainter

# Programme principal : test de la vue ---------------------------------------
if __name__ == "__main__":
    print(f' --- main --- ')
    app = QApplication(sys.argv)
    
    fenetre = VueMaxiMarket()
    fenetre.show()
    
    sys.exit(app.exec())
