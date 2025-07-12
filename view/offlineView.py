import os
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import time
from ViewModel.OfflineViewModel import OfflineViewModel

class OfflineView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vm = OfflineViewModel()
        self.vm.data_loaded.connect(self._on_data_loaded)
        self.show_spectrum = False
        self.apply_filter = False
        self.selected_channels = [0]  # 默认显示通道 0

        self._init_ui()

    def _init_ui(self):
        """初始化用户界面"""
        # 通道选择
        self.channel_combo = QtWidgets.QComboBox()
        self.channel_combo.addItems([f"Ch {i}" for i in range(self.vm.n_channels)])
        self.channel_combo.currentIndexChanged.connect(self._update_plot)

        # 分析类型选择
        self.analysis_combo = QtWidgets.QComboBox()
        self.analysis_combo.addItems(["Time Domain", "Frequency Domain", "Bandpass Filter"])
        self.analysis_combo.currentTextChanged.connect(self._on_analysis_changed)

        # 多通道显示
        self.multi_channel_check = QtWidgets.QCheckBox("Show Multiple Channels")
        self.multi_channel_check.stateChanged.connect(self._update_plot)

        # 时间范围滑块
        self.time_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(100)  # 初始范围，加载数据后更新
        self.time_slider.setValue(0)
        self.time_slider.valueChanged.connect(self._update_plot)

        # Matplotlib 画布和工具栏
        self.figure = Figure(tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # 布局
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(QtWidgets.QLabel("Select Channel:", alignment=Qt.AlignLeft))
        lay.addWidget(self.channel_combo)
        lay.addWidget(QtWidgets.QLabel("Analysis Type:", alignment=Qt.AlignLeft))
        lay.addWidget(self.analysis_combo)
        lay.addWidget(self.multi_channel_check)
        lay.addWidget(QtWidgets.QLabel("Time Range (s):", alignment=Qt.AlignLeft))
        lay.addWidget(self.time_slider)
        lay.addWidget(self.toolbar)
        lay.addWidget(self.canvas)
        self.setLayout(lay)

        # 设置样式
        self.setStyleSheet("background-color: #f0f3f9;")

    def _on_data_loaded(self):
        """数据加载完成后的回调"""
        self.channel_combo.clear()
        self.channel_combo.addItems([f"Ch {i}" for i in range(self.vm.n_channels)])
        # 更新时间滑块范围
        t, _ = self.vm.get_channel_data(0)
        if len(t) > 0:
            max_time = t[-1]
            self.time_slider.setMaximum(int(max_time * 10))  # 0.1 秒精度
        print(f"[OfflineView] {time.strftime('%H:%M:%S')} Data loaded, updating plot")
        self._update_plot()

    def _on_analysis_changed(self, analysis_type):
        """分析类型变更回调"""
        self.show_spectrum = analysis_type == "Frequency Domain"
        self.apply_filter = analysis_type == "Bandpass Filter"
        print(f"[OfflineView] {time.strftime('%H:%M:%S')} Analysis type changed to: {analysis_type}")
        self._update_plot()

    def _update_plot(self):
        """更新绘图"""
        self.figure.clear()
        ch = self.channel_combo.currentIndex()
        rms = self.vm.compute_rms(ch)
        t, data = self.vm.get_channel_data(ch)

        # 时间窗口
        time_start = self.time_slider.value() / 10.0  # 0.1 秒精度
        time_window = 0.5  # 0.5 秒窗口，与 PlotPanel 一致
        time_end = time_start + time_window
        indices = (t >= time_start) & (t <= time_end)
        t_window = t[indices]
        data_window = data[indices]

        if self.show_spectrum:
            # 频域图（使用全时间范围以获得更好分辨率）
            ax = self.figure.add_subplot(1, 1, 1)
            if len(data) > 0:
                xf, power = self.vm.compute_spectrum(ch)
                ax.plot(xf, power, label=f"Channel {ch}")
                ax.set_xlabel("Frequency (Hz)")
                ax.set_ylabel("Power")
                ax.set_title(f"Power Spectrum — Channel {ch} (RMS: {rms:.2f})")
                ax.grid(True)
        else:
            # 时域图
            ax = self.figure.add_subplot(1, 1, 1)
            if self.apply_filter:
                filtered_data = self.vm.apply_bandpass_filter(ch)
                ax.plot(t_window, filtered_data[indices], label=f"Channel {ch} (Filtered)")
            else:
                ax.plot(t_window, data_window, label=f"Channel {ch} (Raw)")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Amplitude")
            ax.set_title(f"Channel {ch} — RMS: {rms:.2f}")
            ax.grid(True)

        # 多通道显示
        if self.multi_channel_check.isChecked():
            self.selected_channels = [ch, (ch + 1) % self.vm.n_channels, (ch + 2) % self.vm.n_channels]
            for extra_ch in self.selected_channels[1:]:
                t, extra_data = self.vm.get_channel_data(extra_ch)
                extra_data_window = extra_data[indices]
                if self.show_spectrum:
                    xf, power = self.vm.compute_spectrum(extra_ch)
                    ax.plot(xf, power, label=f"Channel {extra_ch}", alpha=0.5)
                elif self.apply_filter:
                    filtered_data = self.vm.apply_bandpass_filter(extra_ch)
                    ax.plot(t_window, filtered_data[indices], label=f"Channel {extra_ch} (Filtered)", alpha=0.5)
                else:
                    ax.plot(t_window, extra_data_window, label=f"Channel {extra_ch} (Raw)", alpha=0.5)
                ax.legend()

        self.canvas.draw()
        print(f"[OfflineView] {time.strftime('%H:%M:%S')} Plot updated for Channel {ch}, Time: {time_start:.1f}-{time_end:.1f} s")