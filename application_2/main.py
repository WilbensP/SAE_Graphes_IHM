import sys
from PyQt6.QtWidgets import QApplication
from controller import MaxiMarketController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = MaxiMarketController()
    controller.get_view().show()
    sys.exit(app.exec())
