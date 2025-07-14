from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSizePolicy, QSplitter
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from view.plotting_widget import PlotPanel, PlotBar
from view.channels_widget import ChannelList
from view.custom_widget import CustomPanel
from view.offlineView import OfflineView
from ViewModel.OfflineViewModel import OfflineViewModel
import time

class MainWindow(QMainWindow):
    def __init__(self, view_model):
        super().__init__()
        self.view_model = view_model
        self.setWindowTitle("Live EMG Plotting")
        self.resize(1450, 900)
        self.setWindowIcon(QIcon("others/icon.png"))
        self.setStyleSheet('background-color: #f0f3f9; font-family: "Segoe UI"')
        self.offline_window = None

        # 1. Create channel selection panel
        self.channel_container = ChannelList()

        # 2. Create plotting area
        self.plot_panel = PlotPanel(max_points=1000, sampling_rate=2000, parent=self)
        self.plot_bar = PlotBar(self.view_model)

        self.plot_container = QWidget()
        self.plot_container.layout = QVBoxLayout()
        self.plot_container.layout.addWidget(self.plot_panel, stretch=5)
        self.plot_container.layout.addWidget(self.plot_bar, stretch=0)
        self.plot_container.setSizePolicy(QSizePolicy.MinimumExpanding,
                                         QSizePolicy.MinimumExpanding)
        self.plot_container.setLayout(self.plot_container.layout)

        # 3. Customize area for user interface
        self.custom_container = CustomPanel()

        # Create layout
        split_top = QSplitter(Qt.Horizontal)
        split_top.addWidget(self.channel_container)
        split_top.addWidget(self.plot_container)
        split_top.setSizes([200, 1000])

        split_bottom = QSplitter(Qt.Horizontal)
        split_bottom.addWidget(self.custom_container)

        split_top.setChildrenCollapsible(False)

        vsplit = QSplitter(Qt.Vertical)
        vsplit.addWidget(split_top)
        vsplit.addWidget(split_bottom)
        vsplit.setSizes([600, 300])
        vsplit.setChildrenCollapsible(False)

        # Apply layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(vsplit)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Connect signals and slots
        self.plot_bar.start_button.clicked.connect(self.start_plotting)
        self.plot_bar.stop_resume_button.clicked.connect(self.toggle_pause)
        self.plot_bar.offline_button.clicked.connect(self.offline_show)
        self.channel_container.channel_changed.connect(self.change_channel)
        self.custom_container.filter_changed.connect(self.view_model.set_filter)
        self.custom_container.color_changed.connect(self.view_model.set_color)
        self.view_model.data_updated.connect(self.plot_panel.update_data)
        self.view_model.connection_status_updated.connect(self.plot_bar.status_container.set_connection)
        self.view_model.color_updated.connect(self.plot_panel.set_color)

    def start_plotting(self):
        channel = self.channel_container.get_current_channel()
        self.view_model.set_channel(channel)
        self.view_model.start_plotting()
        self.plot_bar.start_button.setEnabled(False)
        self.plot_bar.stop_resume_button.setEnabled(True)
        self.plot_bar.stop_resume_button.setText("Stop")
        print(f"[MainWindow] {time.strftime('%H:%M:%S')} Start button clicked, Channel: Ch {channel}")

    def toggle_pause(self):
        self.view_model.toggle_pause()
        if self.view_model.is_plotting:
            self.plot_bar.stop_resume_button.setText("Stop")
            self.plot_bar.start_button.setEnabled(False)
        else:
            self.plot_bar.stop_resume_button.setText("Resume")
            self.plot_bar.start_button.setEnabled(True)
        print(f"[MainWindow] {time.strftime('%H:%M:%S')} Toggle button clicked, State: {'Running' if self.view_model.is_plotting else 'Paused'}")

    def offline_show(self):
        if self.offline_window is None or not self.offline_window.isVisible():
            self.offline_window = OfflineView()
            self.offline_window.show()
        else:
            self.offline_window.raise_()
            self.offline_window.activateWindow()

    def change_channel(self, channel: int):
        self.view_model.set_channel(channel)
        self.plot_panel.reset_buffer(channel)
        print(f"[MainWindow] {time.strftime('%H:%M:%S')} Channel changed to: Ch {channel}")