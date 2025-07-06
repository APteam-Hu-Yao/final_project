from PyQt5.QtWidgets import QLabel, QHBoxLayout, QWidget, QFrame
from viewmodel.RealTimeViewModel import SignalViewModel
from PyQt5.QtCore import Qt

class StatusLights(QFrame):
    def __init__(self, color:str, diameter: int = 12, parent = None):
        super().__init__(parent)
        self.diameter = diameter
        self.setFixedSize(diameter, diameter)
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: {diameter//2}px;
        """)
    def setColor(self, color:str):
        self.setStyleSheet(f"""
        background-color:{color};
        border-radius:{self.diameter//2}px;
        """)

class StatusLabel(QWidget):
    def __init__(self):
        super().__init__()
        self.pause_label = QLabel("Pause")
        self.pause_light = StatusLights("red", diameter=10)
        self.connection_label = QLabel("Connection")
        self.connection_light = StatusLights("green", diameter=10)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.layout.addWidget(self.pause_label)
        self.layout.addWidget(self.pause_light)
        self.layout.addSpacing(16)
        self.layout.addWidget(self.connection_label)
        self.layout.addWidget(self.connection_light)
        self.layout.addStretch(1)
        self.setLayout(self.layout)

