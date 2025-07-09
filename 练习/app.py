import sys
from PyQt5.QtWidgets import (QApplication,
                             QMainWindow,
                             QWidget,
                             QVBoxLayout,
                             QHBoxLayout,
                             QGridLayout,
                             QStackedLayout,
                             QPushButton,
                             QTabWidget,
                             QLabel,
                             )
from PyQt5.QtGui import QPalette, QColor
from layout_colorwidget import Color

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(600,500)
        self.setWindowTitle("app von mir")
        # layout1 = QHBoxLayout()
        # layout2 = QVBoxLayout()
        # layout3 = QVBoxLayout()
        #
        # layout1.setContentsMargins(0,0,0,0)
        # layout1.setSpacing(200)
        #
        # layout2.addWidget(Color('blue'))
        # layout2.addWidget(Color('yellow'))
        # layout2.addWidget(Color('purple'))
        #
        # layout1.addLayout(layout2)
        #
        # layout1.addWidget(Color('white'))
        #
        # layout3.addWidget(Color('orange'))
        # layout3.addWidget(Color('pink'))
        #
        # layout1.addLayout( layout3 )
        #
        # layout = QHBoxLayout()
        # layout.addWidget(Color('red'))
        # layout.addWidget(Color('blue'))
        # layout.addWidget(Color('yellow'))
        # layout = QGridLayout()
        # layout = QStackedLayout()
        # layout.addWidget(Color('blue'))
        # layout.addWidget(Color('yellow'))
        # layout.addWidget(Color('pink'))
        # layout.addWidget(Color('black'))
        # layout.setCurrentIndex(2)
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.West)
        tabs.setMovable(True)
        for n, color in enumerate(['pink', 'white', 'yellow', 'orange']):
            tabs.addTab(Color(color), color)
        #
        # widget = QWidget()
        # widget.setLayout(layout)

        self.setCentralWidget(tabs)


app = QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()