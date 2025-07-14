import os
import pickle
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt

class SignalModel:
    def __init__(self, pkl_path=None, fs=2000):
        self.fs = fs
        self.channel_data = []
        self.channel_time = []
        self.n_channels = 0
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.pkl_path = pkl_path or os.path.join(base, "others", "recording.pkl")
        self._load_data()

    def _load_data(self):
        try:
            with open(self.pkl_path, "rb") as f:
                rec = pickle.load(f)
            if "device_information" not in rec or "biosignal" not in rec:
                raise ValueError("Invalid pkl file format: missing 'device_information' or 'biosignal'.")
            info = rec["device_information"]
            self.n_channels = info["number_of_biosignal_channels"]
            self.fs = info.get("sampling_frequency", self.fs)
            sig_all = rec["biosignal"]
            sig = sig_all[:self.n_channels]
            C, M, K = sig.shape
            total_samples = M * K
            self.channel_data = [sig[c].T.reshape(-1) for c in range(C)]
            self.channel_time = [np.arange(total_samples) / self.fs for _ in range(C)]
            print(f"[SignalModel] Loaded data from {self.pkl_path}, Shape: ({self.n_channels}, {total_samples}), Sampling rate: {self.fs} Hz")
        except FileNotFoundError:
            print(f"[SignalModel] Error: File {self.pkl_path} not found.")
            self.channel_data = []
            self.channel_time = []
            self.n_channels = 0
        except Exception as e:
            print(f"[SignalModel] Error loading data: {str(e)}")
            self.channel_data = []
            self.channel_time = []
            self.n_channels = 0

    def get_channel_data(self, ch_idx: int, time_start: float, time_end: float):
        if ch_idx < 0 or ch_idx >= self.n_channels or not self.channel_data:
            return np.array([]), np.array([])
        t = self.channel_time[ch_idx]
        data = self.channel_data[ch_idx]
        indices = (t >= time_start) & (t <= time_end)
        return t[indices], data[indices]

    def compute_rms(self, ch_idx: int):
        if ch_idx < 0 or ch_idx >= self.n_channels or not self.channel_data:
            return 0.0
        d = self.channel_data[ch_idx]
        return float(np.sqrt(np.mean(d ** 2)))

    def compute_spectrum(self, ch_idx: int):
        if ch_idx < 0 or ch_idx >= self.n_channels or not self.channel_data:
            return np.array([]), np.array([])
        data = self.channel_data[ch_idx]
        n = len(data)
        yf = fft(data)
        xf = fftfreq(n, 1 / self.fs)[:n // 2]
        power = np.abs(yf)[:n // 2] ** 2
        return xf, power

    def apply_bandpass_filter(self, ch_idx: int, lowcut=20, highcut=500, order=4):
        if ch_idx < 0 or ch_idx >= self.n_channels or not self.channel_data:
            return np.array([])
        data = self.channel_data[ch_idx]
        nyq = 0.5 * self.fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return filtfilt(b, a, data)