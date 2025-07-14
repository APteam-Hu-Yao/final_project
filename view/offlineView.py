from PyQt5.QtWidgets import (
    QWidget, QComboBox, QSlider, QLabel, QVBoxLayout,
    QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from ViewModel.OfflineViewModel import OfflineViewModel
import time

class OfflineView(QWidget):
    def __init__(self, view_model=None, parent=None):
        super().__init__(parent)
        self.vm = view_model or OfflineViewModel()
        self.vm.data_loaded.connect(self._on_data_loaded)
        self.vm.plot_updated.connect(self._update_plot)
        self.setWindowTitle("Offline Signal Analysis")
        self.setWindowIcon(QIcon("others/icon.png"))
        self.setStyleSheet('background-color:#9AA6B2; font-family: "Segoe UI"')
        self._init_ui()

    def _init_ui(self):
        # Channel combo
        self.channel_combo = QComboBox()
        self.channel_combo.addItems([f"Ch {i}" for i in range(self.vm.n_channels)])
        self.channel_combo.currentIndexChanged.connect(self._on_channel_changed)
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

        # Channel label
        self.ChannelLabel = QLabel("Select Channel:")
        self.ChannelLabel.setAlignment(Qt.AlignLeft)
        self.ChannelLabel.setStyleSheet("font-size: 25px")

        # Time slider
        self.TimeLabel = QLabel("Time range")
        self.TimeLabel.setAlignment(Qt.AlignLeft)
        self.TimeLabel.setStyleSheet("font-size: 25px")
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setValue(0)
        self.time_slider.valueChanged.connect(self._on_time_changed)

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
        h_widget.setLayout(h_layout)
        h_widget.setStyleSheet('background-color: #BCCCDC')
        layout.addWidget(h_widget, stretch=2)
        self.setLayout(layout)

    def _on_data_loaded(self):
        self.channel_combo.clear()
        if self.vm.n_channels == 0:
            print(f"[OfflineView] No channels available")
            self.canvas.draw()
            return
        self.channel_combo.addItems([f"Ch {i}" for i in range(self.vm.n_channels)])
        t, _ = self.vm.model.get_channel_data(0, 0, 1)
        if len(t) > 0:
            max_time = t[-1]
            self.time_slider.setMaximum(int(max_time * 10))
        print(f"[OfflineView] {time.strftime('%H:%M:%S')} Data loaded, {self.vm.n_channels} channels available")
        self._on_channel_changed(0)  # Initialize with first channel

    def _on_channel_changed(self, index):
        print(f"[OfflineView] Channel changed to: {index}")
        self.vm.set_selected_channels([index])

    def _on_analysis_changed(self, analysis_type):
        print(f"[OfflineView] Analysis type changed to: {analysis_type}")
        self.vm.set_analysis_type(analysis_type)
        # Disable time slider for Frequency Domain, enable for others
        self.time_slider.setEnabled(analysis_type != "Frequency Domain")

    def _on_time_changed(self, value):
        print(f"[OfflineView] Time changed to: {value / 10.0}")
        self.vm.set_time_range(value / 10.0)

    def _update_plot(self, plot_data):
        self.figure.clear()
        if not plot_data:
            print(f"[OfflineView] No plot data received")
            self.canvas.draw()
            return
        ax = self.figure.add_subplot(1, 1, 1)
        for i, data in enumerate(plot_data):
            ax.plot(data["x"], data["y"], label=data["label"], alpha=1.0)
            ax.set_xlabel(data["xlabel"])
            ax.set_ylabel(data["ylabel"])
            ax.set_title(data["title"])
        ax.grid(True)
        ax.legend()
        self.canvas.draw()
        print(f"[OfflineView] {time.strftime('%H:%M:%S')} Plot updated with {len(plot_data)} channels")