from PyQt5.QtWidgets import QListWidget, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
class channel_list(QListWidget):
    def __init__(self):
        super(). __init__()
        self.addItems([f"Ch {i}" for i in range(32)])
        self.setMinimumWidth(200)
        # 槽先留空，只做样式
        self.currentRowChanged.connect(lambda idx: print(f"选中通道 {idx}"))

        #加上 QSS 样式
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("""
            QListWidget {
                background-color: #BCCCDC;
                color: #cccccc;
                border: none;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #44475a;
                color: #f8f8f2;
                outline: none;
                border: none
            }
            QListWidget::item:hover {
                background-color: #3e3e3e;
            }
        """)