from PyQt5.QtWidgets import QComboBox, QSizePolicy
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
class ChannelCombo(QComboBox):
    channel_changed = pyqtSignal(int)
    def __init__(self, parent=None):
        super(). __init__(parent)
        self.addItems([f"Ch {i}" for i in range(32)])
        self.setFocusPolicy(Qt.NoFocus)
        # —— 1. 大小策略：宽度优先按内容，垂直不拉伸 ——
        self.setSizePolicy(
            QSizePolicy.Fixed,  # 水平用内容决定
            QSizePolicy.Fixed  # 垂直固定（或 Preferred 也行）
        )

        # —— 2. 最小/最大宽度限制 ——
        self.setMinimumWidth(60)  # 最少占 120px
        self.setMaximumWidth(1200)  # 最多扩展到 200px
        self.setStyleSheet("""
            /* 整个控件背景 */
            QComboBox {
                background-color: #BCCCDC;
                color: #333333;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            /* 箭头区域 */
            QComboBox::drop-down {
                border: none;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
            }
            /* 下拉列表（QAbstractItemView 是内部列表） */
            QComboBox QAbstractItemView {
                background-color: #BCCCDC;
                color: #333333;
                border: none;
                padding: 0;
            }
            /* 列表项常规样式 */
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-radius: 4px;
                margin: 2px 0;
            }
            /* 选中时样式 */
            QComboBox QAbstractItemView::item:selected {
                background-color: #44475A;
                color: #f8f8f2;
                outline: none;
            }
        """)
        # 监听内置的 currentIndexChanged，将其转发为我们的自定义信号
        self.currentIndexChanged.connect(self._on_channel_changed)

    def _on_channel_changed(self, index: int):
        # 这里简单打印，后面再接到 ViewModel
        channel_name = self.itemText(index)
        print(f"Selected channel index: {index}, name: {channel_name}")
