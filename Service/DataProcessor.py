
import numpy as np
from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal

class DataProcessor(QObject):
    data_updated = pyqtSignal(np.ndarray)  
    full_data_updated = pyqtSignal(np.ndarray) 
    status_updated = pyqtSignal(bool, str)  

    def __init__(self, tcp_service, buffer_size=100):
        super().__init__()
        self.tcp_service = tcp_service
        self.buffer = deque(maxlen=buffer_size)
        self.full_data = []
        self.sample_count = 0
        self.paused = False

    def process_chunk(self, data: np.ndarray):
        if data.shape != (32, 18):
            raise ValueError(f"Invalid data shape: {data.shape}")
        if not self.paused:
            self.buffer.append(data.copy())
            self.full_data.append(data.copy())
            self.sample_count += 18
            self.data_updated.emit(data)

    def get_realtime_data(self, channel: int):
        if not self.buffer or not (0 <= channel < 32):
            return np.array([])
        return np.concatenate([chunk[channel, :] for chunk in self.buffer])

    def get_full_data(self, channel: int):
        if not self.full_data or not (0 <= channel < 32):
            return np.array([])
        full_data = np.concatenate([chunk[channel, :] for chunk in self.full_data])
        self.full_data_updated.emit(full_data)
        return full_data

    def get_rms(self, channel: int):
        data = self.get_full_data(channel)
        return np.sqrt(np.mean(data**2)) if data.size > 0 else 0.0

    def toggle_pause(self):
        self.paused = not self.paused
        self.tcp_service.toggle_pause()
        self.status_updated.emit(not self.paused, "Paused" if self.paused else "Resumed")

    def clear_full_data(self):
        self.full_data = []
        self.sample_count = 0