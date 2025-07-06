from PyQt5.QtWidgets import QLabel, QSizePolicy, QComboBox, QWidget, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

# class CustomWidget(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setObjectName("glassPanel")
#         self.setStyleSheet("""
#                 #glassPanel {
#                     background-color: rgba(250, 250, 250, 80);   /* 半透明白 */
#                      border-radius: 48px;                         /* 圆角 */
#                     border: 1px solid rgba(255,255,255,120);     /* 细白边 */
#                 }
#             """)
#         self.setMinimumHeight(0)
#         self.setMaximumHeight(500)
#         self.setSizePolicy(
#             QSizePolicy.Preferred,
#             QSizePolicy.Expanding
#         )


from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout,
    QComboBox, QLabel, QSlider, QPushButton,
    QHBoxLayout
)
from PyQt5.QtCore import Qt, pyqtSignal

class CustomPanel(QWidget):
    # 把各个子控件的信号汇总出去
    frequency_changed = pyqtSignal(int)
    filter_changed    = pyqtSignal(str)
    color_changed     = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)  # 标签在上方
        tabs.setMovable(False)                 # 标签不允许拖拽

        # —— 1. 频率切换页 ——
        freq_tab = QWidget()
        freq_layout = QVBoxLayout(freq_tab)
        self.freq_combo = QComboBox()
        for f in (100, 500, 1000, 1500, 2000):
            self.freq_combo.addItem(f"{f} Hz", f)
        self.freq_combo.currentIndexChanged.connect(
            lambda i: self.frequency_changed.emit(self.freq_combo.itemData(i))
        )
        freq_layout.addWidget(QLabel("select sampling rate："))
        freq_layout.addWidget(self.freq_combo)

        # —— 2. 滤镜选择页 ——
        filt_tab = QWidget()
        filt_layout = QVBoxLayout(filt_tab)
        self.filt_combo = QComboBox()
        for name in ("Raw", "RMS"):
            self.filt_combo.addItem(name)
        self.filt_combo.currentTextChanged.connect(self.filter_changed.emit)
        filt_layout.addWidget(QLabel(""))
        filt_layout.addWidget(self.filt_combo)

        # —— 3. 颜色选取页 ——
        color_tab = QWidget()
        color_layout = QVBoxLayout(color_tab)
        self.color_combo = QComboBox()
        for clr in ("Blue", "Pink", "Neon Blue", "Neon Pink"):
            self.color_combo.addItem(clr)
        self.color_combo.currentTextChanged.connect(self.color_changed.emit)
        color_layout.addWidget(QLabel(""))
        color_layout.addWidget(self.color_combo)

        # 把三个选项卡放进去
        tabs.addTab(freq_tab,   "sampling rate")
        tabs.addTab(filt_tab,   "filters")
        tabs.addTab(color_tab,  "colors")

        # 整个面板布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)
