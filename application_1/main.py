import sys
from PyQt6.QtWidgets import QApplication
from controleur import ControleurMaxiMarket

def main():
    app = QApplication(sys.argv)
    
    # Créer le contrôleur 
    controleur = ControleurMaxiMarket()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
