from PyQt5.QtWidgets import QLabel, QHBoxLayout, QWidget, QFrame
from PyQt5.QtGui import QColor, QFont


class StatusLights(QFrame):
    def __init__(self, color, diameter: int = 14, parent=None):
        super().__init__(parent)
        self.diameter = diameter
        self.setFixedSize(diameter, diameter)
        # 支持 QColor 或 #RRGGBB 字符串
        hexcode = color.name() if isinstance(color, QColor) else color
        # 样式表写在一行，避免多余空白被 Qt 解析失败
        self.setStyleSheet(
            f"background-color: {hexcode};"
            f"border-radius: {self.diameter // 2}px;"
        )

    def setColor(self, color):
        """接受 QColor 或者 #RRGGBB 字符串"""
        hexcode = color.name() if isinstance(color, QColor) else color
        self.setStyleSheet(
            f"background-color: {hexcode};"
            f"border-radius: {self.diameter // 2}px;"
        )


class StatusLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.connection_label = QLabel("Connection(TCP)")
        font = QFont("Segoe UI", 9, QFont.Bold)  # 简写：字体名，字号，粗细
        self.setFont(font)
        # 初始颜色可以设为灰色，表示未知
        self.connection_light = StatusLights("#CCCCCC", diameter=20)

        layout = QHBoxLayout(self)
        layout.addSpacing(16)
        layout.addWidget(self.connection_label)
        layout.addWidget(self.connection_light)
        layout.addStretch(1)
        self.setContentsMargins(0, 0, 0, 0)

    def set_connection(self, is_connected: bool, message: str = ''):
        """True → 绿灯；False → 红灯"""
        hexcode = "#00DFA2" if is_connected else "#FF0060"
        self.connection_light.setColor(hexcode)
