from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
import time

class ChannelList(QListWidget):
    """
    a 32 channels list, 带信号 & 时间戳打印 & 外部接口
    """
    # 和原 combo 保持一致的信号名
    channel_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._channel_count = 32
        self.setSelectionMode(QListWidget.SingleSelection)
        self._populate()

        # 选中行变化时调用
        self.currentItemChanged.connect(self._on_current_item_changed)

        # 样式不变
        self.setStyleSheet("""
        QListWidget{
            font-family: 'Segoe UI';
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
        # 发信号
        self.channel_changed.emit(ch)
        # 打印日志
        print(f"[ChannelList] {time.strftime('%H:%M:%S')} Channel selected: Ch {ch}")

    def get_current_channel(self):
        """返回当前选中的通道号，若无选中返回 None"""
        cur = self.currentItem()
        return cur.data(Qt.UserRole) if cur else None

    def select_channel(self, ch: int):
        """程序内选中通道，并触发 on_current_item_changed"""
        if not (0 <= ch < self._channel_count):
            return
        # 用 setCurrentRow 自动更新 currentItem 并发信号
        self.setCurrentRow(ch)
