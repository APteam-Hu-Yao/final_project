from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QComboBox
from PyQt5.QtCore import pyqtSignal

class CustomPanel(QWidget):

    filter_changed    = pyqtSignal(str)
    color_changed     = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #D9EAFD;")
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(False)
        tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 150px;
                min-height: 50px;
                font-size: 30px;
            }
        """)


        #1.filter tab
        filt_tab = QWidget()
        filt_layout = QVBoxLayout(filt_tab)
        self.filt_combo = QComboBox()
        for name in ("Raw", "RMS"):
            self.filt_combo.addItem(name)
        self.filt_combo.currentTextChanged.connect(self.filter_changed.emit)
        self.filt_combo.setMinimumHeight(80)
        filt_layout.addWidget(self.filt_combo)
        filt_layout.setContentsMargins(5, 5, 5, 5)


        #2.colors tap
        color_tab = QWidget()
        color_layout = QVBoxLayout(color_tab)
        self.color_combo = QComboBox()
        for clr in ("White", "Pink", "Neon Blue", "Neon Pink"):
            self.color_combo.addItem(clr)
        self.color_combo.currentTextChanged.connect(self.color_changed.emit)
        self.color_combo.setMinimumHeight(80)
        color_layout.addWidget(self.color_combo)
        filt_layout.setContentsMargins(5, 5, 5, 5)


        # add the tabs to the tab widget
        tabs.addTab(filt_tab,   "filters")
        tabs.addTab(color_tab,  "colors")

        # make the layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)






