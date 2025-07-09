from PyQt5.QtWidgets import (QMainWindow,
                             QWidget,
                             QVBoxLayout,
                             QSizePolicy,
                             QSplitter,
                             )
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QEvent
from view.plotting_widget import PlotPanel, PlotBar
from view.channels_widget import ChannelList
from view.custom_widget import CustomPanel
from view.status_printer import StatusLabel
import time
from ViewModel.RealTimeViewModel import SignalViewModel


#create the window class that we need
class MainWindow(QMainWindow):
    def __init__(self,viewmodel):
        super().__init__()
        self.view_model = viewmodel
        self.setWindowTitle("live EMG plotting")
        self.resize(1450, 900)
        self.setWindowIcon(QIcon("others/icon.png"))
        self.setStyleSheet("background-color: #f0f3f9;")


        # self.menu = QMenuBar()


        #1.create an instance of 32 channels choose mechanism panel
        self.channel_container = ChannelList()

        #2.create the plotting area
        self.plot_panel = PlotPanel(max_points=1000, sampling_rate=2000, parent=self) #create plot_panel
        self.plot_bar = PlotBar(self.view_model)  #create the control buttons

        self.plot_container = QWidget()  #plan the order of plotting panel and buttons
        self.plot_container.layout = QVBoxLayout()
        self.plot_container.layout.addWidget(self.plot_panel,stretch=5)
        self.plot_container.layout.addWidget(self.plot_bar,stretch=0)
        self.plot_container.setSizePolicy(QSizePolicy.MinimumExpanding,
                                          QSizePolicy.MinimumExpanding)#guarantees the plotting panel has a minimum size
        self.plot_container.setLayout(self.plot_container.layout)



        #3.customize area for userinterface
        self.custom_container = CustomPanel()


        # create the layout
        split_top = QSplitter(Qt.Horizontal)  #the first column
        split_top.addWidget(self.channel_container)
        split_top.addWidget(self.plot_container)
        split_top.setSizes([200,1000])

        split_bottom =QSplitter(Qt.Horizontal) #the second column
        split_bottom.addWidget(self.custom_container)

        split_top.setChildrenCollapsible(False)  # guarantees the plotting panel has a minimum size


        vsplit = QSplitter(Qt.Vertical) # make the first top and the second bottom
        vsplit.addWidget(split_top)
        vsplit.addWidget(split_bottom)
        vsplit.setSizes([600, 300])
        vsplit.setChildrenCollapsible(False)  #guarantees the plotting panel has a minimum size

        #apply the layout
        main_widget = QWidget() #create widget that receive the layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(vsplit)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 信号连接
        self.plot_bar.start_button.clicked.connect(self.start_plotting)
        self.plot_bar.stop_resume_button.clicked.connect(self.toggle_pause)
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
        self.plot_bar.stop_resume_button.setText("STOP")
        print(f"[MainWindow] {time.strftime('%H:%M:%S')} Start button clicked, Channel: Ch {channel}")

    def toggle_pause(self):
        self.view_model.toggle_pause()
        if self.view_model.is_plotting:
            self.plot_bar.stop_resume_button.setText("STOP")
            self.plot_bar.start_button.setEnabled(False)
        else:
            self.plot_bar.stop_resume_button.setText("RESUME")
            self.plot_bar.start_button.setEnabled(True)
        print(
            f"[MainWindow] {time.strftime('%H:%M:%S')} Toggle button clicked, State: {'Running' if self.view_model.is_plotting else 'Paused'}")

    def change_channel(self, channel: int):
        self.view_model.set_channel(channel)
        self.plot_panel.reset_buffer(channel)
        print(f"[MainWindow] {time.strftime('%H:%M:%S')} Channel changed to: Ch {channel}")




