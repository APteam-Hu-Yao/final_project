from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
import time

class DataProcessor(QObject):
    data_updated = pyqtSignal(np.ndarray)
    status_updated = pyqtSignal(bool, str)

    def __init__(self, tcp_service, parent=None):
        super().__init__(parent)
        self.tcp_service = tcp_service
        self.current_channel = 0
        self.paused = False
        self.buffer = []
        self.full_data = []
        self.sample_count = 0
        self.max_samples = 1000
        self.packet_count = 0

        self.tcp_service.data_received.connect(self.process_chunk)
        self.tcp_service.connection_status.connect(self.handle_connection_status)

    def process_chunk(self, data: np.ndarray):
        if data.shape != (18,):
            print(f"[DataProcessor] {time.strftime('%H:%M:%S')} Invalid data shape: {data.shape}, Channel: Ch {self.current_channel}")
            return
        if not self.paused:
            min_val, max_val = np.min(data), np.max(data)
            print(f"[DataProcessor] {time.strftime('%H:%M:%S')} Received data for Ch {self.current_channel}, Shape: {data.shape}, Amplitude: [{min_val:.2f}, {max_val:.2f}]")
            self.buffer.append(data.copy())
            self.full_data.append(data.copy())
            self.sample_count += 18
            self.packet_count += 1
            if self.packet_count % 100 == 0:
                print(f"[DataProcessor] {time.strftime('%H:%M:%S')} Processed packet {self.packet_count}, Channel: Ch {self.current_channel}, Total samples: {self.sample_count}")
            self.data_updated.emit(data)
            if len(self.full_data) > self.max_samples:
                self.full_data = self.full_data[-self.max_samples:]

    def get_realtime_data(self, channel: int):
        if channel != self.current_channel:
            return np.array([])
        data = np.concatenate(self.buffer) if self.buffer else np.array([])
        self.buffer.clear()
        return data

    def clear_full_data(self):
        self.buffer.clear()
        self.full_data.clear()
        self.sample_count = 0
        self.packet_count = 0
        print(f"[DataProcessor] {time.strftime('%H:%M:%S')} Cleared buffers, Channel: Ch {self.current_channel}")

    def toggle_pause(self):
        self.paused = not self.paused
        self.status_updated.emit(not self.paused, "Paused" if self.paused else "Resumed")
        print(f"[DataProcessor] {time.strftime('%H:%M:%S')} State changed: {'Paused' if self.paused else 'Running'}, Channel: Ch {self.current_channel}")

    def handle_connection_status(self, status: bool, message: str):
        self.status_updated.emit(status, message)