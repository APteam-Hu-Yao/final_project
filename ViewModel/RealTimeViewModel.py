from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
import time

class SignalViewModel(QObject):
    data_updated = pyqtSignal(np.ndarray)
    pause_status_updated = pyqtSignal(bool, str)
    connection_status_updated = pyqtSignal(bool, str)
    invalid_data_warning = pyqtSignal(str)
    color_updated = pyqtSignal(str)

    def __init__(self, data_processor):
        super().__init__()
        self.data_processor = data_processor
        self.current_channel = 0
        self.sampling_rate = 2000
        self.filter_type = "Raw"
        self.color = "lime"
        self.is_plotting = False
        self.rms_window_size = 18
        self.packet_count = 0

        self.data_processor.status_updated.connect(self.handle_pause_status)
        self.data_processor.tcp_service.connection_status.connect(self.handle_connection_status)
        self.data_processor.data_updated.connect(self.update_realtime_data)

    def set_channel(self, channel: int):
        if 0 <= channel < 32:
            if self.current_channel != channel:
                self.current_channel = channel
                self.data_processor.current_channel = channel
                self.data_processor.clear_full_data()
                self.data_processor.tcp_service.send_channel(channel)
                print(f"[ViewModel] {time.strftime('%H:%M:%S')} Switched to channel: Ch {channel}")
            self.update_realtime_data()

    def start_plotting(self):
        self.is_plotting = True
        self.data_processor.clear_full_data()
        self.data_processor.paused = False
        self.data_processor.tcp_service.paused = False
        self.data_processor.tcp_service.start(self.current_channel)
        self.pause_status_updated.emit(True, "Started")
        print(f"[ViewModel] {time.strftime('%H:%M:%S')} Plotting started, Channel: Ch {self.current_channel}")

    def toggle_pause(self):
        self.data_processor.toggle_pause()
        self.data_processor.tcp_service.toggle_pause()
        self.is_plotting = not self.data_processor.paused
        print(f"[ViewModel] {time.strftime('%H:%M:%S')} Pause toggled, State: {'Paused' if self.data_processor.paused else 'Running'}, Channel: Ch {self.current_channel}")

    def set_filter(self, filter_type: str):
        self.filter_type = filter_type
        self.update_realtime_data()
        print(f"[ViewModel] {time.strftime('%H:%M:%S')} Filter changed to: {filter_type}, Channel: Ch {self.current_channel}")

    def set_color(self, color: str):
        self.color = color
        self.color_updated.emit(color)
        print(f"[ViewModel] {time.strftime('%H:%M:%S')} Color changed to: {color}, Channel: Ch {self.current_channel}")

    def handle_pause_status(self, status: bool, message: str):
        self.pause_status_updated.emit(status, message)

    def handle_connection_status(self, status: bool, message: str):
        self.connection_status_updated.emit(status, message)

    def update_realtime_data(self, data=None):
        if not self.is_plotting:
            print(f"[ViewModel] {time.strftime('%H:%M:%S')} Not plotting, skipping update, Channel: Ch {self.current_channel}")
            return
        if data is None:
            data = self.data_processor.get_realtime_data(self.current_channel)
        if data.size == 0:
            print(f"[ViewModel] {time.strftime('%H:%M:%S')} No data for channel: Ch {self.current_channel}, sending zeros")
            data = np.zeros(18, dtype=np.float32)

        self.packet_count += 1
        min_val, max_val = np.min(data), np.max(data)
        print(f"[ViewModel] {time.strftime('%H:%M:%S')} Processing data for Ch {self.current_channel}, Packet {self.packet_count}, Shape: {data.shape}, Amplitude: [{min_val:.2f}, {max_val:.2f}]")

        if self.filter_type == "RMS":
            if data.size >= self.rms_window_size:
                rms = np.sqrt(np.mean(data[-self.rms_window_size:]**2))
                data = np.full(self.rms_window_size, rms)
                if self.packet_count % 50 == 0:
                    print(f"[ViewModel] {time.strftime('%H:%M:%S')} RMS calculated: {rms:.2f} for Ch {self.current_channel}, Packet {self.packet_count}")
            else:
                print(f"[ViewModel] {time.strftime('%H:%M:%S')} Insufficient data for RMS, Channel: Ch {self.current_channel}")
                self.invalid_data_warning.emit(f"Insufficient data for RMS, Channel {self.current_channel}")
                return

        self.data_updated.emit(data)