import sys
from PyQt5.QtWidgets import QApplication
from view.mainView import MainWindow
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
