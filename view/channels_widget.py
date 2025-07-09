from PyQt5.QtWidgets import QWidget, QComboBox, QHBoxLayout
from PyQt5.QtCore import pyqtSignal
import time

class ChannelsWidget(QWidget):
    channel_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.channel_combo = QComboBox()
        self.channel_combo.addItems([f"Channel {i}" for i in range(32)])
        layout.addWidget(self.channel_combo)
        self.channel_combo.currentIndexChanged.connect(self.on_channel_changed)

    def get_current_channel(self):
        return self.channel_combo.currentIndex()

    def on_channel_changed(self, index):
        self.channel_changed.emit(index)
        print(f"[ChannelsWidget] {time.strftime('%H:%M:%S')} Channel selected: Ch {index}")