import os
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# 注意：根据你的项目包结构修改下面这行的导入路径
from ViewModel.OfflineViewModel import OfflineViewModel

class OfflineView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vm = OfflineViewModel()
        self.vm.data_loaded.connect(self._on_data_loaded)

        self._init_ui()
        # 手动触发一次——数据加载完成后会发 data_loaded 信号
        # （如果 load 是在 ctor 里同线程同步完成的，也会立即执行）
        # 否则，这句话可以删，改为真正的异步加载后再触发
        self.vm.data_loaded.emit()

    def _init_ui(self):
        # 通道下拉
        self.channel_combo = QtWidgets.QComboBox()
        self.channel_combo.addItems([f"Ch {i}" for i in range(self.vm.n_channels)])
        self.channel_combo.currentIndexChanged.connect(self._update_plot)

        # Matplotlib 画布
        self.figure = Figure(tight_layout=True)
        self.canvas = FigureCanvas(self.figure)

        # 布局
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(QtWidgets.QLabel("选择通道：", alignment=Qt.AlignLeft))
        lay.addWidget(self.channel_combo)
        lay.addWidget(self.canvas)
        self.setLayout(lay)

    def _on_data_loaded(self):
        # 数据准备好了，开始第一次绘图
        self._update_plot()

    def _update_plot(self):
        ch = self.channel_combo.currentIndex()
        t, data = self.vm.get_channel_data(ch)
        rms = self.vm.compute_rms(ch)

        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        ax.plot(t, data)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.set_title(f"Channel {ch} —  RMS: {rms:.2f}")
        ax.grid(True)

        self.canvas.draw()
