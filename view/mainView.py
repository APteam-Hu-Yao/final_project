from PyQt5.QtWidgets import (QMainWindow,
                             QWidget,
                             QVBoxLayout,
                             QHBoxLayout,
                             QGridLayout,
                             QSizePolicy,
                             )
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from view.plotting_widget import PlotPanel, PlotButton
from view.channels_widget import ChannelCombo
from view.custom_widget import CustomPanel
from view.status_printer import StatusLabel
from viewmodel.RealTimeViewModel import SignalViewModel

#creat the window class that we need
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.vm = viewmodel
        self.setWindowTitle("live EMG plotting")
        self.resize(1200, 900)
        self.setWindowIcon(QIcon("others/icon.png"))
        self.setStyleSheet("background-color: #f0f3f9;")
        # self.menu = QMenuBar()

        # decide the order of the widgets
        self.V_layout = QVBoxLayout()
        self.H_layout = QHBoxLayout()
        self.G_layout = QGridLayout()

        #create widgets that accept the order
        self.whole_block = QWidget()

        #1.create an instance of 32 channels choose mechanism panel
        self.channel_container = ChannelCombo()

        #2.create a panel that prints the status of connection
        self.status_container = StatusLabel()


        #3.create the plotting area
        self.plot_panel = PlotPanel(max_points=1000) #create plot_panel
        self.plot_button = PlotButton()  #create the control buttons

        self.plot_container = QWidget()  #plan the order of plotting panel and buttons
        self.plot_container.layout = QVBoxLayout()
        self.plot_container.layout.addWidget(self.plot_panel,stretch=5)
        self.plot_container.layout.addWidget(self.plot_button,stretch=0)
        self.plot_container.setLayout(self.plot_container.layout)
        self.plot_container.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )


        #4.customize area for userinterface
        self.custom_container = CustomPanel()


        self.G_layout.addWidget(self.channel_container, 0,0)
        self.G_layout.addWidget(self.status_container, 1,0)
        self.G_layout.addWidget(self.plot_container, 0,1)
        self.G_layout.addWidget(self.custom_container, 1,1)
        self.G_layout.setContentsMargins(0, 0, 0, 0)  # 左、上、右、下的外边距都设 0
        self.G_layout.setSpacing(0)  # 控件之间的间距也设为 0
        self.G_layout.setColumnStretch(0,0)
        self.G_layout.setColumnStretch(1, 1)
        # self.G_layout.setRowStretch(0, 1)


        self.whole_block.setLayout(self.G_layout)
        self.setCentralWidget(self.whole_block)


