import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox

class ChoisirMagasin(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.magasins = ["Selectionner un magasin","Magasin Maxi Market"]
        self.magasin_choisi = None
        
        self.combo_magasin = QComboBox()
        self.combo_magasin.addItems(self.magasins)
        self.combo_magasin.currentTextChanged.connect(self.choisir_magasin)
        
        self.setCentralWidget(self.combo_magasin)
        self.show()
    
    def choisir_magasin(self):
        self.magasin_choisi = self.combo_magasin.currentText()
        print(f"Magasin choisi: {self.magasin_choisi}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    fenetre = ChoisirMagasin()
    sys.exit(app.exec())