import os
import pickle
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
import time
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt

class OfflineViewModel(QObject):
    data_loaded = pyqtSignal()

    def __init__(self, pkl_path=None, fs=2000):
        super().__init__()
        # 默认数据文件路径
        if pkl_path is None:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            pkl_path = os.path.join(base, "others", "recording.pkl")
        self.pkl_path = pkl_path
        self.fs = fs  # 默认采样率
        self.channel_data = []  # 存储每个通道的信号数据
        self.channel_time = []  # 存储每个通道的时间轴
        self.n_channels = 0
        self._load_data()

    def _load_data(self):
        """从 pkl 文件加载数据，处理 biosignal 并生成连续波形"""
        try:
            with open(self.pkl_path, "rb") as f:
                rec = pickle.load(f)
            info = rec["device_information"]
            self.n_channels = info["number_of_biosignal_channels"]  # 通常为 32
            self.fs = info.get("sampling_frequency", self.fs)  # 获取采样率，默认为 2000 Hz
            sig_all = rec["biosignal"]  # 形状 (38, 18, K)
            sig = sig_all[:self.n_channels]  # 形状 (n_channels, 18, K)

            # 展平每个通道的数据为 (n_samples,)
            C, M, K = sig.shape
            total_samples = M * K
            self.channel_data = []
            self.channel_time = []
            for c in range(C):
                arr = sig[c].T.reshape(-1)  # (K, 18) -> (K*18,)
                t = np.arange(total_samples) / self.fs
                self.channel_data.append(arr)
                self.channel_time.append(t)
            
            print(f"[OfflineViewModel] {time.strftime('%H:%M:%S')} Loaded data from {self.pkl_path}, Shape: ({self.n_channels}, {total_samples}), Sampling rate: {self.fs} Hz")
            self.data_loaded.emit()
        except Exception as e:
            print(f"[OfflineViewModel] {time.strftime('%H:%M:%S')} Error loading data: {e}")
            self.channel_data = []
            self.channel_time = []
            self.n_channels = 0
            self.data_loaded.emit()

    def get_channel_data(self, ch_idx: int):
        """返回指定通道的 (time, data) 数组"""
        if ch_idx < 0 or ch_idx >= self.n_channels or not self.channel_data:
            return np.array([]), np.array([])
        return self.channel_time[ch_idx], self.channel_data[ch_idx]

    def compute_rms(self, ch_idx: int):
        """计算指定通道的 RMS 值"""
        if ch_idx < 0 or ch_idx >= self.n_channels or not self.channel_data:
            return 0.0
        d = self.channel_data[ch_idx]
        return float(np.sqrt(np.mean(d ** 2)))

    def compute_spectrum(self, ch_idx: int):
        """计算指定通道的功率谱"""
        if ch_idx < 0 or ch_idx >= self.n_channels or not self.channel_data:
            return np.array([]), np.array([])
        data = self.channel_data[ch_idx]
        n = len(data)
        yf = fft(data)
        xf = fftfreq(n, 1 / self.fs)[:n // 2]
        power = np.abs(yf)[:n // 2] ** 2
        return xf, power

    def apply_bandpass_filter(self, ch_idx: int, lowcut=20, highcut=500, order=4):
        """对指定通道应用带通滤波"""
        if ch_idx < 0 or ch_idx >= self.n_channels or not self.channel_data:
            return np.array([])
        data = self.channel_data[ch_idx]
        nyq = 0.5 * self.fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return filtfilt(b, a, data)