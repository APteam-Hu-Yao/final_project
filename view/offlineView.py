from PyQt5.QtWidgets import (
    QWidget, QComboBox, QCheckBox, QSlider, QLabel, QVBoxLayout,
    QHBoxLayout, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from ViewModel.OfflineViewModel import OfflineViewModel
import time


class OfflineView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vm = OfflineViewModel()
        self.vm.data_loaded.connect(self._on_data_loaded)
        self.show_spectrum = False
        self.apply_filter = False
        self.selected_channels = [0]
        self.setWindowTitle("Offline Signal Analysis")
        self.setWindowIcon(QIcon("others/icon.png"))
        self.setStyleSheet('background-color:#9AA6B2; font-family: "Segoe UI"')

        self._init_ui()

    def _init_ui(self):
        # Channel combo (single main selector)
        self.channel_combo = QComboBox()
        self.channel_combo.addItems([f"Ch {i}" for i in range(self.vm.n_channels)])
        self.channel_combo.currentIndexChanged.connect(self._update_plot)
        self.channel_combo.setMinimumHeight(60)
        self.channel_combo.setStyleSheet('font-size:25px')

        # Analysis type combo
        self.AnalysisLabel = QLabel("Analysis Type:")
        self.AnalysisLabel.setAlignment(Qt.AlignLeft)
        self.AnalysisLabel.setStyleSheet("font-size: 25px")
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems(["Time Domain", "Frequency Domain", "Bandpass Filter"])
        self.analysis_combo.currentTextChanged.connect(self._on_analysis_changed)
        self.analysis_combo.setMinimumHeight(60)
        self.analysis_combo.setStyleSheet('font-size:25px')

        # Show multiple channels checkbox
        self.ChannelLabel = QLabel("Select Channel:")
        self.ChannelLabel.setAlignment(Qt.AlignLeft)
        self.ChannelLabel.setStyleSheet("font-size: 25px")
        self.multi_channel_check = QCheckBox("Show Multiple Channels")
        self.multi_channel_check.stateChanged.connect(self._on_multi_channel_toggle)
        self.multi_channel_check.setMinimumHeight(60)
        self.multi_channel_check.setStyleSheet('font-size:25px')

        # Multiple channel checkbox group (hidden by default)
        self.channel_select_box = QGroupBox("Channels")
        self.channel_select_layout = QGridLayout()
        self.channel_checkboxes = []

        for i in range(self.vm.n_channels):
            cb = QCheckBox(f"Ch {i}")
            cb.stateChanged.connect(self._update_plot)
            self.channel_checkboxes.append(cb)
            row = i // 4
            col = i % 4
            self.channel_select_layout.addWidget(cb, row, col)

        self.channel_select_box.setLayout(self.channel_select_layout)
        self.channel_select_box.setStyleSheet("font-size: 18px")
        self.channel_select_box.setVisible(False)

        # Time slider
        self.TimeLabel = QLabel("Time range")
        self.TimeLabel.setAlignment(Qt.AlignLeft)
        self.TimeLabel.setStyleSheet("font-size: 25px")
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(100)
        self.time_slider.setValue(0)
        self.time_slider.valueChanged.connect(self._update_plot)

        # Matplotlib
        self.figure = Figure(tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Layout
        layout = QVBoxLayout()
        h_widget = QWidget()
        h_layout = QHBoxLayout()
        layout.addWidget(self.toolbar, stretch=1)
        layout.addWidget(self.canvas, stretch=7)
        layout.addWidget(self.TimeLabel)
        layout.addWidget(self.time_slider, stretch=2)
        h_layout.addWidget(self.ChannelLabel)
        h_layout.addWidget(self.channel_combo, stretch=1)
        h_layout.addWidget(self.AnalysisLabel)
        h_layout.addWidget(self.analysis_combo, stretch=1)
        h_layout.addSpacing(50)
        h_layout.addWidget(self.multi_channel_check, stretch=1)
        h_layout.addWidget(self.channel_select_box, stretch=3)
        h_widget.setLayout(h_layout)
        h_widget.setStyleSheet('background-color: #BCCCDC')
        layout.addWidget(h_widget, stretch=2)
        self.setLayout(layout)

    def _on_multi_channel_toggle(self, state):
        is_checked = state == Qt.Checked
        self.channel_select_box.setVisible(is_checked)
        self._update_plot()

    def _on_data_loaded(self):
        self.channel_combo.clear()
        self.channel_combo.addItems([f"Ch {i}" for i in range(self.vm.n_channels)])
        t, _ = self.vm.get_channel_data(0)
        if len(t) > 0:
            max_time = t[-1]
            self.time_slider.setMaximum(int(max_time * 10))
        print(f"[OfflineView] {time.strftime('%H:%M:%S')} Data loaded, updating plot")
        self._update_plot()

    def _on_analysis_changed(self, analysis_type):
        self.show_spectrum = analysis_type == "Frequency Domain"
        self.apply_filter = analysis_type == "Bandpass Filter"
        print(f"[OfflineView] {time.strftime('%H:%M:%S')} Analysis type changed to: {analysis_type}")
        self._update_plot()

    def _update_plot(self):
        self.figure.clear()
        ch = self.channel_combo.currentIndex()
        time_start = self.time_slider.value() / 10.0
        time_window = 0.5
        time_end = time_start + time_window

        if self.multi_channel_check.isChecked():
            self.selected_channels = [
                i for i, cb in enumerate(self.channel_checkboxes) if cb.isChecked()
            ]
            if not self.selected_channels:
                self.selected_channels = [ch]
        else:
            self.selected_channels = [ch]

        ax = self.figure.add_subplot(1, 1, 1)

        for i, channel_id in enumerate(self.selected_channels):
            rms = self.vm.compute_rms(channel_id)
            t, data = self.vm.get_channel_data(channel_id)
            indices = (t >= time_start) & (t <= time_end)
            t_window = t[indices]
            data_window = data[indices]

            label = f"Channel {channel_id}"
            alpha = 1.0 if i == 0 else 0.5

            if self.show_spectrum:
                xf, power = self.vm.compute_spectrum(channel_id)
                ax.plot(xf, power, label=label, alpha=alpha)
                ax.set_xlabel("Frequency (Hz)")
                ax.set_ylabel("Power")
                ax.set_title("Power Spectrum")
            else:
                if self.apply_filter:
                    filtered = self.vm.apply_bandpass_filter(channel_id)
                    ax.plot(t_window, filtered[indices], label=label + " (Filtered)", alpha=alpha)
                else:
                    ax.plot(t_window, data_window, label=label + " (Raw)", alpha=alpha)
                ax.set_xlabel("Time (s)")
                ax.set_ylabel("Amplitude")
                ax.set_title("Signal Plot")

        ax.grid(True)
        ax.legend()
        self.canvas.draw()

        print(f"[OfflineView] {time.strftime('%H:%M:%S')} Plot updated for channels {self.selected_channels}, Time: {time_start:.1f}-{time_end:.1f} s")
