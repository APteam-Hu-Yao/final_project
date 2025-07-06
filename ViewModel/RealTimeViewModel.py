from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import numpy as np

class SignalViewModel(QObject):
    data_updated = pyqtSignal(np.ndarray) 
    pause_status_updated = pyqtSignal(bool, str)  #dataprocessor
    connection_status_updated = pyqtSignal(bool, str)  #tcpservice

    def __init__(self, data_processor):
        super().__init__()
        self.data_processor = data_processor
        self.current_channel = 0

        self.data_processor.status_updated.connect(self.handle_pause_status)
        self.data_processor.tcp_service.connection_status.connect(self.handle_connection_status)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_realtime_data)
        self.timer.start(33)

    def set_channel(self, channel: int):
        if 0 <= channel < 32:
            self.current_channel = channel
            self.update_realtime_data()
            self.status_updated.emit(True, f"Channel set to {channel}")

    def toggle_pause(self):
        self.data_processor.toggle_pause()

    def handle_pause_status(self, status: bool, message: str):
        self.pause_status_updated.emit(status, message)

    def handle_connection_status(self, status: bool, message: str):
        self.connection_status_updated.emit(status, message)

    def update_realtime_data(self):
        data = self.data_processor.get_realtime_data(self.current_channel)
        if data.size > 0:
            self.data_updated.emit(data)