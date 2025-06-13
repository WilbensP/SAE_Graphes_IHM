import sys, os
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPen, QPixmap, QColor, QBrush, QFont, QPainter, QAction, QPainterPath
from PyQt6.QtCore import Qt, QPointF, pyqtSignal

class Scene(QGraphicsScene):
    """Scène graphique pour l'affichage du plan du magasin"""
    
    produit_sous_curseur = pyqtSignal(str, QPointF)
    
    def __init__(self):
        super().__init__()
        self.nb_rangs, self.nb_rayons = 24, 47
        self.marqueurs, self.coordonnees_produits, self.lignes_chemin = {}, {}, []
        self.plan, self.image = None, None
        self.etiquette_produit, self.fond_etiquette = None, None
        self.point_depart = (28, 21)
        self.point_depart_marker = None
    
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if not self.plan: return
        
        pos = event.scenePos()
        largeur_image, hauteur_image = self.plan.width(), self.plan.height()
        hauteur_case, largeur_case = hauteur_image / self.nb_rangs, largeur_image / self.nb_rayons
        x, y = int(pos.x() / largeur_case), int(pos.y() / hauteur_case)
        coord = f"{x},{y}"
        
        if self.etiquette_produit:
            self.removeItem(self.etiquette_produit)
            self.etiquette_produit = None
        if self.fond_etiquette:
            self.removeItem(self.fond_etiquette)
            self.fond_etiquette = None
        
        if coord in self.coordonnees_produits:
            produit = self.coordonnees_produits[coord]
            self.etiquette_produit = QGraphicsTextItem(f"{produit}")
            self.etiquette_produit.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            self.etiquette_produit.setDefaultTextColor(QColor(255, 255, 255))
            
            rect = self.etiquette_produit.boundingRect()
            self.fond_etiquette = QGraphicsRectItem(rect)
            self.fond_etiquette.setBrush(QBrush(QColor(0, 0, 0, 180)))
            self.fond_etiquette.setPen(QPen(Qt.PenStyle.NoPen))
            
            # Positionner l'étiquette à l'emplacement du curseur
            self.etiquette_produit.setPos(pos.x() + 10, pos.y() - rect.height() - 10)
            self.fond_etiquette.setPos(pos.x() + 10, pos.y() - rect.height() - 10)
            
            self.addItem(self.fond_etiquette)
            self.addItem(self.etiquette_produit)
            self.produit_sous_curseur.emit(f"{produit} ({x},{y})", pos)
        else:
            self.produit_sous_curseur.emit("Aucun produit", pos)
    
    def charger_plan(self, chemin_image=None):
        if chemin_image is None: chemin_image = sys.path[0] + "/plan.jpg"
        if os.path.exists(chemin_image):
            if self.image: self.removeItem(self.image)
            self.plan = QPixmap(chemin_image)
            self.image = QGraphicsPixmapItem(self.plan)
            self.addItem(self.image)
            self.setSceneRect(0, 0, self.plan.width(), self.plan.height())
            self.creer_quadrillage()
            self.marquer_point_depart()
            return True
        return False
    
    def marquer_point_depart(self):
        """Marque le point de départ sur le plan"""
        if not self.plan: return
        
        largeur_image, hauteur_image = self.plan.width(), self.plan.height()
        largeur_case = largeur_image / self.nb_rayons
        hauteur_case = hauteur_image / self.nb_rangs
        
        x, y = self.point_depart
        centre_x = (x + 0.5) * largeur_case
        centre_y = (y + 0.5) * hauteur_case
        
        # Créer un cercle pour marquer le point de départ
        rayon = min(largeur_case, hauteur_case) * 0.4
        self.point_depart_marker = QGraphicsEllipseItem(
            centre_x - rayon, centre_y - rayon, 
            rayon * 2, rayon * 2
        )
        self.point_depart_marker.setBrush(QBrush(QColor(255, 0, 0, 150)))
        self.point_depart_marker.setPen(QPen(QColor(255, 0, 0), 3))
        self.addItem(self.point_depart_marker)
        
        # Ajouter un texte "Départ"
        texte_depart = QGraphicsTextItem("DÉPART")
        texte_depart.setDefaultTextColor(QColor(255, 0, 0))
        font = texte_depart.font()
        font.setBold(True)
        texte_depart.setFont(font)
        texte_depart.setPos(centre_x - texte_depart.boundingRect().width() / 2, 
                           centre_y - rayon - texte_depart.boundingRect().height())
        self.addItem(texte_depart)
    
    def creer_quadrillage(self):
        if not self.plan: return
        for item in self.items():
            if isinstance(item, QGraphicsLineItem): self.removeItem(item)
        
        largeur_image, hauteur_image = self.plan.width(), self.plan.height()
        hauteur_case, largeur_case = hauteur_image / self.nb_rangs, largeur_image / self.nb_rayons
        crayon_rouge = QPen(QColor(255, 0, 0))
        crayon_rouge.setWidth(1)
        
        for rang in range(self.nb_rangs + 1):
            ligne = QGraphicsLineItem(0, rang * hauteur_case, largeur_image, rang * hauteur_case)
            ligne.setPen(crayon_rouge)
            self.addItem(ligne)
        
        for rayon in range(self.nb_rayons + 1):
            ligne = QGraphicsLineItem(rayon * largeur_case, 0, rayon * largeur_case, hauteur_image)
            ligne.setPen(crayon_rouge)
            self.addItem(ligne)
    
    def afficher_emplacements(self, placements, nb_rangs=None, nb_rayons=None):
        if nb_rangs is not None: self.nb_rangs = nb_rangs
        if nb_rayons is not None: self.nb_rayons = nb_rayons
        
        for marqueur in self.marqueurs.values():
            self.removeItem(marqueur['cercle'])
            self.removeItem(marqueur['texte'])
        self.marqueurs.clear()
        self.coordonnees_produits.clear()
        
        if not self.plan: return
        
        largeur_image, hauteur_image = self.plan.width(), self.plan.height()
        hauteur_case, largeur_case = hauteur_image / self.nb_rangs, largeur_image / self.nb_rayons
        
        for coord, produit in placements.items():
            try:
                x, y = map(int, coord.split(','))
                centre_x, centre_y = (x + 0.5) * largeur_case, (y + 0.5) * hauteur_case
                rayon = min(largeur_case, hauteur_case) * 0.3
                
                cercle = QGraphicsEllipseItem(centre_x - rayon, centre_y - rayon, rayon * 2, rayon * 2)
                cercle.setBrush(QBrush(QColor(0, 200, 0, 150)))
                cercle.setPen(QPen(QColor(0, 100, 0)))
                self.addItem(cercle)
                
                texte = QGraphicsTextItem(produit)
                texte.setFont(QFont("Arial", 8))
                texte.setDefaultTextColor(QColor(0, 0, 0))
                texte.setPos(centre_x - texte.boundingRect().width() / 2, centre_y - rayon - 20)
                self.addItem(texte)
                
                self.marqueurs[coord] = {'cercle': cercle, 'texte': texte, 'produit': produit}
                self.coordonnees_produits[coord] = produit
            except Exception as e:
                print(f"Erreur lors de l'affichage du produit {produit} à {coord}: {str(e)}")
    
    def mettre_en_evidence_produit(self, produit):
        for marqueur in self.marqueurs.values():
            marqueur['cercle'].setBrush(QBrush(QColor(0, 200, 0, 150)))
            marqueur['cercle'].setPen(QPen(QColor(0, 100, 0)))
        
        for coord, marqueur in self.marqueurs.items():
            if marqueur['produit'] == produit:
                marqueur['cercle'].setBrush(QBrush(QColor(255, 0, 0, 200)))
                marqueur['cercle'].setPen(QPen(QColor(150, 0, 0), 2))
                return QPointF(marqueur['cercle'].rect().center().x() + marqueur['cercle'].pos().x(),
                              marqueur['cercle'].rect().center().y() + marqueur['cercle'].pos().y())
        return None
    
    def effacer_chemin(self):
        for ligne in self.lignes_chemin: self.removeItem(ligne)
        self.lignes_chemin.clear()
    
    def afficher_chemin(self, chemin):
        self.effacer_chemin()
        if not self.plan or not chemin: return
        
        largeur_image, hauteur_image = self.plan.width(), self.plan.height()
        hauteur_case, largeur_case = hauteur_image / self.nb_rangs, largeur_image / self.nb_rayons
        
        # Créer le chemin avec QPainterPath
        path = QPainterPath()
        
        # Point de départ
        x_depart, y_depart = self.point_depart
        depart_x = (x_depart + 0.5) * largeur_case
        depart_y = (y_depart + 0.5) * hauteur_case
        path.moveTo(depart_x, depart_y)
        
        # Ajouter les points du chemin
        for _, (x, y) in chemin:
            centre_x = (x + 0.5) * largeur_case
            centre_y = (y + 0.5) * hauteur_case
            path.lineTo(centre_x, centre_y)
        
        # Créer l'item de chemin
        chemin_item = QGraphicsPathItem(path)
        crayon_bleu = QPen(QColor(0, 0, 255))
        crayon_bleu.setWidth(3)
        crayon_bleu.setStyle(Qt.PenStyle.DashLine)
        chemin_item.setPen(crayon_bleu)
        self.addItem(chemin_item)
        self.lignes_chemin.append(chemin_item)
        
        # Ajouter des numéros pour chaque étape du chemin
        for i, (produit, (x, y)) in enumerate(chemin):
            centre_x = (x + 0.5) * largeur_case
            centre_y = (y + 0.5) * hauteur_case
            
            # Cercle pour le numéro
            rayon = min(largeur_case, hauteur_case) * 0.2
            cercle = QGraphicsEllipseItem(centre_x - rayon, centre_y - rayon, rayon * 2, rayon * 2)
            cercle.setBrush(QBrush(QColor(0, 0, 255, 150)))
            cercle.setPen(QPen(QColor(0, 0, 150)))
            self.addItem(cercle)
            self.lignes_chemin.append(cercle)
            
            # Numéro
            numero = QGraphicsTextItem(str(i + 1))
            numero.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            numero.setDefaultTextColor(QColor(255, 255, 255))
            numero.setPos(centre_x - numero.boundingRect().width() / 2, 
                         centre_y - numero.boundingRect().height() / 2)
            self.addItem(numero)
            self.lignes_chemin.append(numero)

class Rendu(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(Scene())
        self.setMouseTracking(True)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene() and self.scene().sceneRect().width() > 0:
            self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    def centrer_sur_point(self, point):
        if point: self.centerOn(point)
    
    def wheelEvent(self, event):
        self.scale(1.1 if event.angleDelta().y() > 0 else 0.9, 1.1 if event.angleDelta().y() > 0 else 0.9)

class MaxiMarketMainWindow(QMainWindow):
    ouvrir_projet_demande = pyqtSignal()
    produit_selectionne = pyqtSignal(str)
    ajouter_produit_demande = pyqtSignal(str, int)
    produit_liste_selectionne = pyqtSignal(str)
    generer_liste_demande = pyqtSignal()
    reinitialiser_liste_demande = pyqtSignal()
    enregistrer_liste_demande = pyqtSignal()
    calculer_chemin_demande = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MaxiMarket - Plan du magasin")
        self.resize(1400, 800)
        self.setup_ui()
        self.setup_menu()
        self.connecter_signaux()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        
        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Rendu du plan (panneau gauche)
        self.rendu = Rendu()
        splitter.addWidget(self.rendu)
        
        # Panneau latéral (droite)
        side_panel = QWidget()
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(2, 2, 2, 2)
        side_layout.setSpacing(2)
        
        # Sélection du projet
        projet_group = QGroupBox("Projet")
        projet_layout = QVBoxLayout(projet_group)
        projet_layout.setContentsMargins(2, 5, 2, 2)
        projet_layout.setSpacing(2)
        
        self.projet_combo = QComboBox()
        projet_layout.addWidget(self.projet_combo)
        
        side_layout.addWidget(projet_group)
        
        # Groupe pour la gestion des produits
        produits_group = QGroupBox("Produits")
        produits_layout = QVBoxLayout(produits_group)
        produits_layout.setContentsMargins(2, 5, 2, 2)
        produits_layout.setSpacing(2)
        
        self.produit_menu = QComboBox()
        self.produit_menu.setMaximumHeight(22)
        produits_layout.addWidget(self.produit_menu)
        
        self.ajouter_produit_btn = QPushButton("Ajouter")
        self.ajouter_produit_btn.setMaximumHeight(22)
        self.ajouter_produit_btn.setEnabled(False)
        produits_layout.addWidget(self.ajouter_produit_btn)
        
        side_layout.addWidget(produits_group)
        
        # Groupe pour la liste de courses
        liste_group = QGroupBox("Liste de courses")
        liste_layout = QVBoxLayout(liste_group)
        liste_layout.setContentsMargins(2, 5, 2, 2)
        liste_layout.setSpacing(2)
        
        self.liste_widget = QListWidget()
        self.liste_widget.setMinimumHeight(100)
        self.liste_widget.setMaximumHeight(120)
        self.liste_widget.setFont(QFont("Arial", 10))
        liste_layout.addWidget(self.liste_widget)
        
        # Boutons sur des lignes séparées
        self.generer_btn = QPushButton("Générer liste")
        self.generer_btn.setMaximumHeight(25)
        liste_layout.addWidget(self.generer_btn)
        
        self.reinitialiser_btn = QPushButton("Réinitialiser")
        self.reinitialiser_btn.setMaximumHeight(25)
        liste_layout.addWidget(self.reinitialiser_btn)
        
        self.enregistrer_btn = QPushButton("Enregistrer")
        self.enregistrer_btn.setMaximumHeight(25)
        liste_layout.addWidget(self.enregistrer_btn)
        
        self.calculer_chemin_btn = QPushButton("Calculer chemin")
        self.calculer_chemin_btn.setMaximumHeight(25)
        liste_layout.addWidget(self.calculer_chemin_btn)
        
        side_layout.addWidget(liste_group)
        
        # Groupe pour l'ordre de passage
        ordre_group = QGroupBox("Ordre de passage")
        ordre_layout = QVBoxLayout(ordre_group)
        ordre_layout.setContentsMargins(2, 5, 2, 2)
        ordre_layout.setSpacing(2)
        
        # Table pour l'ordre de passage
        self.table_chemin = QTableWidget()
        self.table_chemin.setColumnCount(3)
        self.table_chemin.setHorizontalHeaderLabels(["Ordre", "Produit", "Position"])
        self.table_chemin.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        ordre_layout.addWidget(self.table_chemin)
        
        side_layout.addWidget(ordre_group)
        
        # Étiquette pour afficher le produit sous le curseur
        self.info_curseur_label = QLabel("Produit: Aucun")
        self.info_curseur_label.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        self.info_curseur_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_curseur_label.setMaximumHeight(30)
        self.info_curseur_label.setFont(QFont("Arial", 12))
        side_layout.addWidget(self.info_curseur_label)
        
        # Ajouter le panneau latéral au splitter
        splitter.addWidget(side_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([750, 250])
        
        # Ajouter le splitter au layout principal
        main_layout.addWidget(splitter)
    
    def setup_menu(self):
        menu_fichier = self.menuBar().addMenu("Fichier")
        action_ouvrir = QAction("Ouvrir projet", self)
        action_ouvrir.triggered.connect(self.ouvrir_projet_demande.emit)
        menu_fichier.addAction(action_ouvrir)
        menu_fichier.addSeparator()
        action_quitter = QAction("Quitter", self)
        action_quitter.triggered.connect(self.close)
        menu_fichier.addAction(action_quitter)
    
    def connecter_signaux(self):
        self.projet_combo.currentIndexChanged.connect(self.on_projet_selectionne)
        self.produit_menu.currentIndexChanged.connect(lambda: self.produit_selectionne.emit(self.produit_menu.currentText()))
        self.ajouter_produit_btn.clicked.connect(self.ajouter_produit)
        self.liste_widget.currentItemChanged.connect(self.selection_liste_changee)
        self.generer_btn.clicked.connect(self.generer_liste_demande.emit)
        self.reinitialiser_btn.clicked.connect(self.reinitialiser_liste_demande.emit)
        self.enregistrer_btn.clicked.connect(self.enregistrer_liste_demande.emit)
        self.calculer_chemin_btn.clicked.connect(self.calculer_chemin_demande.emit)
        self.rendu.scene().produit_sous_curseur.connect(self.afficher_produit_sous_curseur)
    
    def on_projet_selectionne(self):
        index = self.projet_combo.currentIndex()
        if index >= 0:
            fichier = self.projet_combo.itemData(index)
            self.ouvrir_projet_demande.emit()
    
    def ajouter_produit(self):
        produit = self.produit_menu.currentText()
        if produit: self.ajouter_produit_demande.emit(produit, 1)
    
    def selection_liste_changee(self, current, previous):
        if current: self.produit_liste_selectionne.emit(current.text())
    
    def afficher_produit_sous_curseur(self, info, position):
        self.info_curseur_label.setText(info)
    
    # Méthodes pour mettre à jour l'interface depuis le contrôleur
    def mettre_a_jour_titre(self, titre): self.setWindowTitle(titre)
    
    def mettre_a_jour_projets(self, projets):
        self.projet_combo.clear()
        for projet in projets:
            self.projet_combo.addItem(f"{projet['nom_projet']} - {projet['nom_magasin']}", projet['fichier'])
    
    def mettre_a_jour_produits(self, produits):
        self.produit_menu.clear()
        self.produit_menu.addItems(produits)
        self.ajouter_produit_btn.setEnabled(False)
    
    def mettre_a_jour_produit_selectionne(self, produit):
        if produit:
            self.ajouter_produit_btn.setEnabled(True)
        else:
            self.ajouter_produit_btn.setEnabled(False)
    
    def ajouter_item_liste(self, produit): self.liste_widget.addItem(produit)
    def vider_liste(self): self.liste_widget.clear()
    
    def mettre_a_jour_table_chemin(self, chemin):
        self.table_chemin.setRowCount(len(chemin))
        for i, (produit, (x, y)) in enumerate(chemin):
            self.table_chemin.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table_chemin.setItem(i, 1, QTableWidgetItem(produit))
            self.table_chemin.setItem(i, 2, QTableWidgetItem(f"({x}, {y})"))
    
    def vider_table_chemin(self):
        self.table_chemin.setRowCount(0)
    
    def get_rendu(self): return self.rendu
    
    def afficher_message(self, titre, message, type_message="information"):
        if type_message == "information": QMessageBox.information(self, titre, message)
        elif type_message == "warning": QMessageBox.warning(self, titre, message)
        elif type_message == "error": QMessageBox.critical(self, titre, message)
    
    def demander_fichier_ouvrir(self, titre, dossier, filtre):
        fichier, _ = QFileDialog.getOpenFileName(self, titre, dossier, filtre)
        return fichier
    
    def demander_fichier_sauvegarder(self, titre, dossier, filtre):
        fichier, _ = QFileDialog.getSaveFileName(self, titre, dossier, filtre)
        return fichier
