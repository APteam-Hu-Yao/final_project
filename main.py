import sys
from PyQt5.QtWidgets import QApplication
from view.mainView import MainWindow
from ViewModel.RealTimeViewModel import SignalViewModel
from Service.DataProcessor import DataProcessor
from Service.EMGClient import TCPClient

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tcp_client = TCPClient()
    data_processor = DataProcessor(tcp_service=tcp_client, parent=app)
    view_model = SignalViewModel(data_processor)
    window = MainWindow(view_model)
    window.show()
    sys.exit(app.exec_())