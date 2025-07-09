from PyQt5.QtWidgets import QLabel, QWidget, QHBoxLayout, QComboBox
from PyQt5.QtCore import pyqtSignal
import time

class StatusLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Disconnected")
        print(f"[StatusLabel] {time.strftime('%H:%M:%S')} Initialized")

    def set_status(self, message: str):
        self.setText(message)
        print(f"[StatusLabel] {time.strftime('%H:%M:%S')} Status updated: {message}")

class CustomPanel(QWidget):
    filter_changed = pyqtSignal(str)
    color_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Raw", "RMS"])
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)

        self.color_combo = QComboBox()
        self.color_combo.addItems(["Blue", "Pink", "Neon Blue", "Neon Pink"])
        self.color_combo.currentTextChanged.connect(self.on_color_changed)

        self.layout.addWidget(self.filter_combo)
        self.layout.addWidget(self.color_combo)
        self.setLayout(self.layout)
        print(f"[CustomPanel] {time.strftime('%H:%M:%S')} Initialized")

    def on_filter_changed(self, filter_type):
        self.filter_changed.emit(filter_type)
        print(f"[CustomPanel] {time.strftime('%H:%M:%S')} Filter changed to: {filter_type}")

    def on_color_changed(self, color):
        self.color_changed.emit(color)
        print(f"[CustomPanel] {time.strftime('%H:%M:%S')} Color changed to: {color}")