# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout,QWidget,QTextEdit
# from PyQt5.QtGui import QPalette, QColor
# from PyQt5.QtCore import Qt
#
# def build_dark_palette() -> QPalette:
#     dark = QPalette()
#     dark.setColor(QPalette.Window, QColor("#2b2b2b"))
#     dark.setColor(QPalette.WindowText, Qt.white)
#     dark.setColor(QPalette.Base, QColor("#3c3f41"))
#     dark.setColor(QPalette.AlternateBase, QColor("#313335"))
#     dark.setColor(QPalette.Text, Qt.white)
#     dark.setColor(QPalette.ToolTipBase, Qt.white)
#     dark.setColor(QPalette.ToolTipText, Qt.white)
#
#
#     dark.setColor(QPalette.Button, QColor("#3c3f41"))
#     dark.setColor(QPalette.ButtonText, Qt.white)
#     dark.setColor(QPalette.Highlight, QColor("#007acc"))
#     dark.setColor(QPalette.HighlightedText, Qt.white)
#
#     dark.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
#     dark.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
#
#     return dark
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     app.setStyle("Fusion")
#     app.setPalette(build_dark_palette())
#
#     w = QWidget()
#     w.setWindowTitle("Dark-themed Demo")
#
#     edit = QTextEdit("please type")
#     layout = QVBoxLayout(w)
#     layout.addWidget(edit)
#
#     w.resize(600,300)
#     w.show()
#     sys.exit(app.exec())

# plotting_widget.py
import numpy as np
from vispy.scene import SceneCanvas
from vispy.scene import visuals
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout

class RealTimePlotWidget(QWidget):
    def __init__(self, max_points=500, parent=None):
        super().__init__(parent)

        # 1) VisPy 画布
        self.canvas = SceneCanvas(keys=None, bgcolor='black', parent=self)
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = 'panzoom'  # 允许平移/缩放
        self.view.camera.set_range(x=(0, max_points), y=(-1,1))

        # 2) 折线 Visual，用于更新绘图
        self.curve = visuals.Line(color='lime', parent=self.view.scene)
        self.max_points = max_points
        self.data = np.zeros(max_points, dtype=np.float32)
        self.ptr = 0  # 插入指针

        # 3) 把 VisPy 画布嵌入 PyQt5 Widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.canvas.native)

        # 4) 定时刷新（如果你自己驱动 update_data，可以不需要这个 Timer）
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer)
        self._timer.start(50)  # 每 50 ms 刷新一次

    def update_data(self, new_samples):
        """
        接收一个 1D numpy 数组 new_samples（长度例如 18），
        将它追加到循环缓冲区末尾，用于下一次绘图。
        """
        n = len(new_samples)
        # 如果过长，就只取最后 max_points 长度
        if n >= self.max_points:
            self.data[:] = new_samples[-self.max_points:]
            self.ptr = 0
        else:
            # 循环缓冲写入
            end = (self.ptr + n) % self.max_points
            if self.ptr + n < self.max_points:
                self.data[self.ptr:self.ptr+n] = new_samples
            else:
                part = self.max_points - self.ptr
                self.data[self.ptr:] = new_samples[:part]
                self.data[:end] = new_samples[part:]
            self.ptr = end

    def _on_timer(self):
        """定时器回调，把最新 buffer 绘出来"""
        # 1) 生成 x 轴数据
        x = np.arange(self.max_points)
        # 2) 因为是循环缓冲，要把数据对齐：从 ptr 开始到末尾，再到 ptr 之前
        y = np.concatenate([self.data[self.ptr:], self.data[:self.ptr]])
        # 3) 更新 curve
        self.curve.set_data(x, y)
        # 4) 刷新 VisPy 画布
        self.canvas.update()


