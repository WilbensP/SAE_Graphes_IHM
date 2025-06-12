import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsLineItem, QGraphicsRectItem, QPushButton, QListWidget, QComboBox, QLabel, QSpinBox, QDialog, QFormLayout, QLineEdit, QTextEdit, QCheckBox, QGroupBox, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt6.QtGui import QPen, QColor, QBrush
from PyQt6.QtCore import Qt, pyqtSignal

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
        
        crayon_rouge = QPen(QColor(255, 0, 0))
        crayon_rouge.setWidth(1)
        
        # Lignes horizontales
        for rang in range(nb_rangs + 1):
            y_line = rang * hauteur_case
            ligne = QGraphicsLineItem(0, y_line, largeur, y_line)
            ligne.setPen(crayon_rouge)
            self.addItem(ligne)
            self.lignes_quadrillage.append(ligne)
        
        # Lignes verticales
        for rayon in range(nb_rayons + 1):
            x_line = rayon * largeur_case
            ligne = QGraphicsLineItem(x_line, 0, x_line, hauteur)
            ligne.setPen(crayon_rouge)
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
        
        # Ajouter les nouveaux rectangles
        for (x, y), produit in placements.items():
            rect_x = x * largeur_case
            rect_y = y * hauteur_case
            
            rect = QGraphicsRectItem(rect_x, rect_y, largeur_case, hauteur_case)
            rect.setBrush(QBrush(QColor(0, 255, 0, 100)))  
            rect.setPen(QPen(QColor(0, 255, 0), 2))
            
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
    
    def afficher_plan(self, pixmap, nb_rangs, nb_rayons):
        self.scene_graphique.afficher_plan(pixmap, nb_rangs, nb_rayons)
        self.fitInView(self.scene_graphique.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def afficher_placements(self, placements):
        self.scene_graphique.afficher_placements(placements)
    
    def set_produit_a_placer(self, produit):
        self.scene_graphique.set_produit_a_placer(produit)
    
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
        self.resize(400, 300)
        
        layout = QFormLayout()
        
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
        
        boutons_layout.addWidget(self.btn_ok)
        boutons_layout.addWidget(self.btn_annuler)
        
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
        self.resize(600, 500)
        
        self.categories_produits = categories_produits
        self.checkboxes = {}
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Instructions
        label = QLabel("Sélectionnez les produits vendus dans ce magasin :")
        layout.addWidget(label)
        
        # Zone de défilement
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Créer les groupes par catégorie
        for categorie, produits in self.categories_produits.items():
            group = QGroupBox(categorie)
            group_layout = QVBoxLayout()
            
            # Cases cocher produit
            for produit in produits:
                cb = QCheckBox(produit)
                self.checkboxes[produit] = cb
                group_layout.addWidget(cb)
            
            group.setLayout(group_layout)
            scroll_layout.addWidget(group)
        
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Boutons
        boutons_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Valider")
        self.btn_annuler = QPushButton("Annuler")
        
        boutons_layout.addWidget(self.btn_ok)
        boutons_layout.addWidget(self.btn_annuler)
        
        layout.addLayout(boutons_layout)
        self.setLayout(layout)
        
        # Connexions
        self.btn_ok.clicked.connect(self.accept)
        self.btn_annuler.clicked.connect(self.reject)
    
    def toggle_categorie(self, categorie, state):
        for produit in self.categories_produits[categorie]:
            if produit in self.checkboxes:
                self.checkboxes[produit].setChecked(state == Qt.CheckState.Checked)
    
    def get_produits_selectionnes(self):
        return [produit for produit, cb in self.checkboxes.items() if cb.isChecked()]

# -----------------------------------------------------------------------------
# --- class PanneauControle
# -----------------------------------------------------------------------------
class PanneauControle(QWidget):
    # Signaux
    signal_nouveau_projet = pyqtSignal()
    signal_ouvrir_projet = pyqtSignal()
    signal_sauvegarder_projet = pyqtSignal()
    signal_charger_plan = pyqtSignal()
    signal_selectionner_produits = pyqtSignal()
    signal_quadrillage_change = pyqtSignal(int, int)
    signal_produit_selectionne_placement = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Gestion du projet
        projet_group = QGroupBox("Projet")
        projet_layout = QVBoxLayout()
        
        self.btn_nouveau_projet = QPushButton("Nouveau Projet")
        self.btn_ouvrir_projet = QPushButton("Ouvrir Projet")
        self.btn_sauvegarder_projet = QPushButton("Sauvegarder Projet")
        
        self.btn_nouveau_projet.clicked.connect(self.signal_nouveau_projet.emit)
        self.btn_ouvrir_projet.clicked.connect(self.signal_ouvrir_projet.emit)
        self.btn_sauvegarder_projet.clicked.connect(self.signal_sauvegarder_projet.emit)
        
        projet_layout.addWidget(self.btn_nouveau_projet)
        projet_layout.addWidget(self.btn_ouvrir_projet)
        projet_layout.addWidget(self.btn_sauvegarder_projet)
        
        projet_group.setLayout(projet_layout)
        layout.addWidget(projet_group)
        
        # Informations du projet
        self.label_projet_info = QLabel("Aucun projet ouvert")
        self.label_projet_info.setStyleSheet("font-weight: bold; padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.label_projet_info)
        
        # Gestion du plan
        plan_group = QGroupBox("Plan du Magasin")
        plan_layout = QVBoxLayout()
        
        self.btn_charger_plan = QPushButton("Charger Plan")
        self.btn_charger_plan.clicked.connect(self.signal_charger_plan.emit)
        plan_layout.addWidget(self.btn_charger_plan)
        
        self.label_plan_info = QLabel("Aucun plan chargé")
        plan_layout.addWidget(self.label_plan_info)
        
        # Contrôles du quadrillage
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
        
        plan_layout.addLayout(quad_layout)
        plan_group.setLayout(plan_layout)
        layout.addWidget(plan_group)
        
        # Gestion des produits
        produits_group = QGroupBox("Produits du Magasin")
        produits_layout = QVBoxLayout()
        
        self.btn_selectionner_produits = QPushButton("Sélectionner Produits")
        self.btn_selectionner_produits.clicked.connect(self.signal_selectionner_produits.emit)
        produits_layout.addWidget(self.btn_selectionner_produits)
        
        self.liste_produits = QListWidget()
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
    
    # Méthodes de mise à jour
    def mettre_a_jour_projet_info(self, info):
        self.label_projet_info.setText(info)
    
    def mettre_a_jour_plan_info(self, info):
        self.label_plan_info.setText(info)
    
    def mettre_a_jour_produits(self, produits_magasin, placements):
        self.liste_produits.clear()
        for produit in produits_magasin:
            est_place = any(p == produit for p in placements.values())
            if est_place:
                pos = next((f"({x},{y})" for (x, y), p in placements.items() if p == produit), "")
                self.liste_produits.addItem(f"{produit} {pos}")
            else:
                self.liste_produits.addItem(f"{produit} (non placé)")
    
    def mettre_a_jour_table_placements(self, placements):
        self.table_placements.setRowCount(len(placements))
        for i, ((x, y), produit) in enumerate(placements.items()):
            self.table_placements.setItem(i, 0, QTableWidgetItem(produit))
            self.table_placements.setItem(i, 1, QTableWidgetItem(str(x)))
            self.table_placements.setItem(i, 2, QTableWidgetItem(str(y)))
    
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
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("MaxiMarket - Gestionnaire de Projets")
        self.resize(1400, 800)
        
        # Widget central
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # plan
        self.vue_graphique = VueGraphique()
        main_layout.addWidget(self.vue_graphique, stretch=3)
        
        # Panneau de contrôle
        self.panneau_controle = PanneauControle()
        main_layout.addWidget(self.panneau_controle, stretch=1)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Connexion des signaux
        self.panneau_controle.signal_nouveau_projet.connect(self.signal_nouveau_projet.emit)
        self.panneau_controle.signal_ouvrir_projet.connect(self.signal_ouvrir_projet.emit)
        self.panneau_controle.signal_sauvegarder_projet.connect(self.signal_sauvegarder_projet.emit)
        self.panneau_controle.signal_charger_plan.connect(self.signal_charger_plan.emit)
        self.panneau_controle.signal_selectionner_produits.connect(self.signal_selectionner_produits.emit)
        self.panneau_controle.signal_quadrillage_change.connect(self.signal_quadrillage_change.emit)
        self.panneau_controle.signal_produit_selectionne_placement.connect(self.signal_produit_selectionne_placement.emit)
        self.vue_graphique.scene_graphique.produit_place.connect(self.signal_produit_place.emit)
    
    # Méthodes de mise à jour de la vue
    def afficher_plan(self, pixmap, nb_rangs, nb_rayons):
        self.vue_graphique.afficher_plan(pixmap, nb_rangs, nb_rayons)
    
    def afficher_placements(self, placements):
        self.vue_graphique.afficher_placements(placements)
    
    def set_produit_a_placer(self, produit):
        self.vue_graphique.set_produit_a_placer(produit)
    
    def mettre_a_jour_projet_info(self, info):
        self.panneau_controle.mettre_a_jour_projet_info(info)
    
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

## Programme principal : test de la vue ---------------------------------------
if __name__ == "__main__":
    print(f' --- main --- ')
    app = QApplication(sys.argv)
    
    fenetre = VueMaxiMarket()
    fenetre.show()
    
    sys.exit(app.exec())
