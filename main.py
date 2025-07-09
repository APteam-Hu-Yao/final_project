
import sys
from PyQt5.QtWidgets import QApplication
from view.mainView import MainWindow
from ViewModel.RealTimeViewModel import SignalViewModel
from Service.DataProcessor import DataProcessor
from Service.EMGClient import TCPClient
from view.offlineView import OfflineView


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tcp_client = TCPClient()
    data_processor = DataProcessor(tcp_service=tcp_client, parent=app)
    view_model = SignalViewModel(data_processor)

    window = MainWindow(view_model)
    offline_window = OfflineView()
    window.show()
    offline_window.show()
    sys.exit(app.exec_())



def closeEvent(self, event):
    self.view_model.stop_all_threads()  # 你需要定义这个函数
    event.accept()
