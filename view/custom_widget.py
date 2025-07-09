from PyQt5.QtWidgets import (
    QWidget, QTabWidget, QVBoxLayout,
    QComboBox)
from PyQt5.QtCore import pyqtSignal, Qt

class CustomPanel(QWidget):

    filter_changed    = pyqtSignal(str)
    color_changed     = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)  # 标签在上方
        tabs.setMovable(False)                 # 标签不允许拖拽

        # —— 1. 滤镜选择页 ——
        filt_tab = QWidget()
        filt_layout = QVBoxLayout(filt_tab)
        self.filt_combo = QComboBox()
        for name in ("Raw", "RMS"):
            self.filt_combo.addItem(name)
        self.filt_combo.currentTextChanged.connect(self.filter_changed.emit)
        filt_layout.addWidget(self.filt_combo)
        filt_layout.setContentsMargins(5, 5, 5, 5)
        # 1) 主框文字居中
        self.filt_combo.setEditable(True)
        self.filt_combo.lineEdit().setAlignment(Qt.AlignCenter)
        self.filt_combo.setEditable(False)

        # 2) 主框最小高度 80px
        self.filt_combo.setMinimumHeight(80)

        # 3) 只给主框贴一个最小高度样式（文字居中靠上面 setAlignment）
        self.filt_combo.setStyleSheet("""
        QComboBox {
            min-height: 80px;
        }
        """)

        # 4) 给弹出的列表单独贴样式：行高、文字居中、悬停/选中背景
        self.filt_combo.view().setStyleSheet("""
        QListView::item {
            min-height: 80px;
            /* 居中文本 */
            text-align: center;
        }
        QListView::item:hover,
        QListView::item:selected {
            background-color: #B9E5E8;
        }
        """)


        # —— 2. 颜色选取页 ——
        color_tab = QWidget()
        color_layout = QVBoxLayout(color_tab)
        self.color_combo = QComboBox()
        for clr in ("White", "Pink", "Neon Blue", "Neon Pink"):
            self.color_combo.addItem(clr)
        self.color_combo.currentTextChanged.connect(self.color_changed.emit)
        color_layout.addWidget(self.color_combo)
        filt_layout.setContentsMargins(5, 5, 5, 5)


        # 把2个选项卡放进去
        tabs.addTab(filt_tab,   "filters")
        tabs.addTab(color_tab,  "colors")

        # 整个面板布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)

        self.setStyleSheet("background-color: #D9EAFD;")  # 设置背景色



