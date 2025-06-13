import sys
from PyQt6.QtWidgets import QApplication
from controleur import ControleurMaxiMarket

def main():
    app = QApplication(sys.argv)
     
    #creer le controleur 
    controleur = ControleurMaxiMarket()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
