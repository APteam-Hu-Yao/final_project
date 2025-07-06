import sys
from PyQt5.QtWidgets import QApplication
from view.mainView import MainWindow

if __name__ == "__main__":
    #create the app
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
