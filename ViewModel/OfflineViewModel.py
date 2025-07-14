import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Service.DataProcessorOffline import SignalModel
from PyQt5.QtCore import QObject, pyqtSignal
import time

class OfflineViewModel(QObject):
    data_loaded = pyqtSignal()
    plot_updated = pyqtSignal(list)

    def __init__(self, pkl_path=None, fs=2000):
        super().__init__()
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.pkl_path = pkl_path or os.path.join(base, "others", "recording.pkl")
        self.model = SignalModel(self.pkl_path, fs)
        self.n_channels = self.model.n_channels
        self.fs = self.model.fs
        if self.n_channels == 0:
            print(f"[OfflineViewModel] Warning: No channels loaded from {self.pkl_path}")
        self.selected_channels = [0] if self.n_channels > 0 else []
        self.time_start = 0.0
        self.time_window = 0.5
        self.analysis_type = "Time Domain"
        self.data_loaded.emit()  # 立即触发 UI 初始化

    def set_selected_channels(self, channels: list):
        # 验证通道索引
        valid_channels = [ch for ch in channels if 0 <= ch < self.n_channels]
        if not valid_channels and self.n_channels > 0:
            valid_channels = [0]
        self.selected_channels = valid_channels
        print(f"[OfflineViewModel] Selected channels: {self.selected_channels}")
        self._update_plot()

    def set_time_range(self, time_start: float):
        self.time_start = max(0.0, time_start)
        print(f"[OfflineViewModel] Time range set to: {self.time_start:.1f}")
        self._update_plot()

    def set_analysis_type(self, analysis_type: str):
        self.analysis_type = analysis_type
        print(f"[OfflineViewModel] Analysis type set to: {analysis_type}")
        self._update_plot()

    def _update_plot(self):
        if not self.selected_channels or not self.n_channels:
            print(f"[OfflineViewModel] No valid channels to plot")
            self.plot_updated.emit([])
            return

        time_end = self.time_start + self.time_window
        plot_data = []

        for ch_idx in self.selected_channels:
            rms = self.model.compute_rms(ch_idx)
            label = f"Channel {ch_idx} (RMS: {rms:.2f})"
            if self.analysis_type == "Frequency Domain":
                xf, power = self.model.compute_spectrum(ch_idx)
                plot_data.append({
                    "x": xf,
                    "y": power,
                    "label": label,
                    "type": "spectrum",
                    "xlabel": "Frequency (Hz)",
                    "ylabel": "Power",
                    "title": "Power Spectrum"
                })
            else:
                t, data = self.model.get_channel_data(ch_idx, self.time_start, time_end)
                if self.analysis_type == "Bandpass Filter":
                    filtered = self.model.apply_bandpass_filter(ch_idx)
                    t, filtered = self.model.get_channel_data(ch_idx, self.time_start, time_end)
                    plot_data.append({
                        "x": t,
                        "y": filtered,
                        "label": label + " (Filtered)",
                        "type": "time",
                        "xlabel": "Time (s)",
                        "ylabel": "Amplitude",
                        "title": "Signal Plot"
                    })
                else:
                    plot_data.append({
                        "x": t,
                        "y": data,
                        "label": label + " (Raw)",
                        "type": "time",
                        "xlabel": "Time (s)",
                        "ylabel": "Amplitude",
                        "title": "Signal Plot"
                    })

        print(f"[OfflineViewModel] {time.strftime('%H:%M:%S')} Plot updated for channels {self.selected_channels}, Time: {self.time_start:.1f}-{time_end:.1f} s")
        self.plot_updated.emit(plot_data)

