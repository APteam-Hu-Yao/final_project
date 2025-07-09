import os
import pickle
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

class OfflineViewModel(QObject):
    # 信号：数据加载完成，可以通知 View 去绘图
    data_loaded = pyqtSignal()

    def __init__(self, pkl_path=None, fs=2000):
        super().__init__()
        # 默认打开项目根目录下的 others/recording.pkl
        if pkl_path is None:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            pkl_path = os.path.join(base, "others", "recording.pkl")
        self.pkl_path = pkl_path
        self.fs = fs              # 采样率
        self._load_data()

    def _load_data(self):
        """从 pkl 里读出 'biosignal'，重构每个通道的连续波形和时轴。"""
        with open(self.pkl_path, "rb") as f:
            rec = pickle.load(f)

        info = rec["device_information"]
        n_bio = info["number_of_biosignal_channels"]  # 32
        sig_all = rec["biosignal"]  # (38, 18, K)
        sig = sig_all[:n_bio]  # (32, 18, K)   # 形状 (C, 18, N_chunks)
        C, M, K = sig.shape

        # 对每个通道，按 (chunk_samples, n_chunks) 转成一维的连续信号
        self.channel_data = []
        self.channel_time = []
        total_samples = M * K
        for c in range(C):
            arr = sig[c].T.reshape(-1)          # shape = (K, M) 转成 (K*M,)
            t   = np.arange(total_samples) / self.fs
            self.channel_data.append(arr)
            self.channel_time.append(t)

        self.n_channels = C
        self.data_loaded.emit()

    def get_channel_data(self, ch_idx: int):
        """返回 (time, data) 两个 ndarray，供 View 绘图。"""
        return self.channel_time[ch_idx], self.channel_data[ch_idx]

    def compute_rms(self, ch_idx: int):
        """返回该通道整个信号的均方根（scalar）。"""
        d = self.channel_data[ch_idx]
        return float(np.sqrt(np.mean(d ** 2)))
