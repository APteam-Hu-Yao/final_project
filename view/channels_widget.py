from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
import time

class ChannelList(QListWidget):
    channel_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._channel_count = 32
        self.setSelectionMode(QListWidget.SingleSelection)
        self._populate()

        self.currentItemChanged.connect(self._on_current_item_changed)

        self.setStyleSheet("""
        QListWidget{
            font-size: 35px;
            color:#333333;
            background-color: #BCCCDC;
        }
        QListWidget::item{
            min-height: 60px;
            max-height: 60px;
            padding-left: 10px;
        }
        QListWidget::item::selected{
            background-color: #4A628A;
            color: #FFFFFF
        }
        """)

    def _populate(self):
        self.clear()
        for ch in range(self._channel_count):
            item = QListWidgetItem(f"Channel {ch}")
            item.setData(Qt.UserRole, ch)
            self.addItem(item)

    def _on_current_item_changed(self, current, previous):
        if current is None:
            return
        ch = current.data(Qt.UserRole)
        self.channel_changed.emit(ch)
        print(f"[ChannelList] {time.strftime('%H:%M:%S')} Channel selected: Ch {ch}")

    def get_current_channel(self):
        cur = self.currentItem()
        return cur.data(Qt.UserRole) if cur else None

    def select_channel(self, ch: int):
        if not (0 <= ch < self._channel_count):
            return
        self.setCurrentRow(ch)
