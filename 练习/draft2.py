# from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QVBoxLayout, QWidget
# from realtime_plot import RealTimePlotWidget
# # from viewmodel.mainViewModel import MainViewModel
#
# import sys
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Live EMG Plotter")
#         self.resize(800, 400)
#
#         # 1. 注入 ViewModel
#         self.vm = MainViewModel()
#         # 2. 创建 UI
#         container = QWidget()
#         layout = QVBoxLayout(container)
#         self.setCentralWidget(container)
#
#         # 通道选择
#         self.combo = QComboBox()
#         self.combo.addItems([str(i) for i in range(32)])
#         self.combo.currentIndexChanged.connect(self.on_channel_changed)
#         layout.addWidget(self.combo)
#
#         # 实时绘图控件
#         self.plot = RealTimePlotWidget(max_points=500)
#         layout.addWidget(self.plot)
#
#         # 3. 连接 ViewModel 信号
#         # vm 每次收到 (32,18) 数据时，触发 new_frame
#         self.vm.new_frame.connect(self._on_new_frame)
#
#     def on_channel_changed(self, idx):
#         self.vm.select_channel(idx)
#
#     def _on_new_frame(self, data):
#         # data.shape == (32,18)
#         ch = self.vm.current_channel
#         samples = data[ch, :]  # 1D array of length 18
#         self.plot.update_data(samples)
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     w = MainWindow()
#     w.show()
#     sys.exit(app.exec_())


import pickle

with open(r"D:\appliedprogramming\final_project\others\recording.pkl", "rb") as f:
    data = pickle.load(f)

print(type(data))
print(data)