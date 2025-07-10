from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt
from view.channels_widget import ChannelsWidget
from view.plotting_widget import PlotPanel
from view.custom_widget import StatusLabel, CustomPanel
import time

class MainWindow(QMainWindow):
    def __init__(self, view_model, parent=None):
        super().__init__(parent)
        self.view_model = view_model
        self.setWindowTitle("EMG Signal Viewer")
        self.resize(800, 600)

        # 主布局
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 绘图区域
        self.plot_panel = PlotPanel(max_points=1000, sampling_rate=2000, parent=self)
        main_layout.addWidget(self.plot_panel, stretch=1)
        main_layout.addSpacing(20)
        # 控制区域  
        controls_layout = QHBoxLayout()
        main_layout.addLayout(controls_layout)

        # 通道选择
        self.channels_widget = ChannelsWidget(parent=self)
        controls_layout.addWidget(self.channels_widget)

        # 滤波和颜色选择
        self.custom_panel = CustomPanel(parent=self)
        controls_layout.addWidget(self.custom_panel)

        # 按钮
        self.plot_button = QPushButton("START", self)
        self.toggle_button = QPushButton("STOP", self)
        self.toggle_button.setEnabled(False)
        controls_layout.addWidget(self.plot_button)
        controls_layout.addWidget(self.toggle_button)
        
        # 状态标签
        self.status_label = StatusLabel(parent=self)
        main_layout.addWidget(self.status_label)
        main_layout.addSpacing(20) 
        # 信号连接
        self.plot_button.clicked.connect(self.start_plotting)
        self.toggle_button.clicked.connect(self.toggle_pause)
        self.channels_widget.channel_changed.connect(self.change_channel)
        self.custom_panel.filter_changed.connect(self.view_model.set_filter)
        self.custom_panel.color_changed.connect(self.view_model.set_color)
        self.view_model.data_updated.connect(self.plot_panel.update_data)
        self.view_model.pause_status_updated.connect(self.handle_pause_status)
        self.view_model.connection_status_updated.connect(self.status_label.set_status)
        self.view_model.invalid_data_warning.connect(self.status_label.set_status)
        self.view_model.color_updated.connect(self.plot_panel.set_color)

    def start_plotting(self):
        channel = self.channels_widget.get_current_channel()
        self.view_model.set_channel(channel)
        self.view_model.start_plotting()
        self.plot_button.setEnabled(False)
        self.toggle_button.setEnabled(True)
        self.toggle_button.setText("STOP")
        print(f"[MainWindow] {time.strftime('%H:%M:%S')} Start button clicked, Channel: Ch {channel}")

    def toggle_pause(self):
        self.view_model.toggle_pause()
        if self.view_model.is_plotting:
            self.toggle_button.setText("STOP")
            self.plot_button.setEnabled(False)
        else:
            self.toggle_button.setText("RESUME")
            self.plot_button.setEnabled(True)
        print(f"[MainWindow] {time.strftime('%H:%M:%S')} Toggle button clicked, State: {'Running' if self.view_model.is_plotting else 'Paused'}")

    def change_channel(self, channel: int):
        self.view_model.set_channel(channel)
        self.plot_panel.reset_buffer(channel)
        print(f"[MainWindow] {time.strftime('%H:%M:%S')} Channel changed to: Ch {channel}")

    def handle_pause_status(self, status: bool, message: str):
        self.status_label.set_status(message)
        if not status:
            self.toggle_button.setText("RESUME")
            self.plot_button.setEnabled(True)
        else:
            self.toggle_button.setText("STOP")
            self.plot_button.setEnabled(False)