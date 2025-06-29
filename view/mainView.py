from PyQt5.QtWidgets import (QMainWindow,
                             QPushButton,
                             QLabel,
                             QWidget,
                             QVBoxLayout,
                             QHBoxLayout,
                             QLineEdit,
                             QMenuBar,
                             QAction,
                             QGraphicsOpacityEffect,
                             QListWidget,
                             QSizePolicy,
                             )
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from view.plotting_widget import PlotPanel, PlotButton
from view.channels_widget import channel_list
from view.custom_widget import custom_label

#creat the window class that we need
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("live EMG plotting")
        self.resize(1200, 900)
        self.setWindowIcon(QIcon("others/icon.png"))
        self.setStyleSheet("background-color: #f0f3f9;")
        # self.menu = QMenuBar()


        # decide the order of the widgets
        self.V_layout = QVBoxLayout()
        self.H_layout = QHBoxLayout()

        # create widgets that accept the order
        self.basic_container = QWidget()
        self.container1 = QWidget()

        #1.create an instance of 32 channels choose mechanism panel
        self.channel_container = channel_list()


        #2.create an instance of plotting panel by vispy and an instance of the buttons
        #plan the order of plotting panel and buttons
        self.plot_container = QWidget()
        self.plot_container.layout = QVBoxLayout()
        self.plot_container.layout.addWidget(PlotPanel(max_points=500),stretch=5)
        self.plot_container.layout.addWidget(PlotButton(),stretch=0)
        self.plot_container.setLayout(self.plot_container.layout)
        self.plot_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        #3.customize area for userinterface
        self.custom_container = custom_label()

        #add those containers to the layout
        self.V_layout.addWidget(self.container1)
        self.V_layout.addWidget(self.custom_container)
        self.H_layout.addWidget(self.channel_container)
        self.H_layout.addWidget(self.plot_container)
        #参数 (index, stretch)：index 是控件在 layout 中的顺序
        self.H_layout.setStretch(0, 0)  # channel_list 不再拉伸
        self.H_layout.setStretch(1, 1)  # plot_widget 占据剩余所有空间

        #apply layout to the widget and make the widget central
        self.basic_container.setLayout(self.V_layout)
        self.setCentralWidget(self.basic_container)
        self.container1.setLayout(self.H_layout)
