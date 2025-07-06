import numpy as np
from vispy.scene import SceneCanvas
from vispy.scene import visuals
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout,QPushButton,QHBoxLayout, QSizePolicy


class PlotPanel(QWidget):
     def __init__(self, max_points=500, parent=None):
         super().__init__(parent)
         # 1) VisPy 画布
         self.canvas = SceneCanvas(keys=None, bgcolor = '#D9EAFD', parent=self)
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
         #接收一个 1D numpy 数组 new_samples（长度例如 18），将它追加到循环缓冲区末尾，用于下一次绘图。
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
        # """定时器回调，把最新 buffer 绘出来"""
        #  # 1) 生成 x 轴数据
         x = np.arange(self.max_points)
         # 2) 因为是循环缓冲，要把数据对齐：从 ptr 开始到末尾，再到 ptr 之前
         y = np.concatenate([self.data[self.ptr:], self.data[:self.ptr]])
         # 3) 更新 curve
         self.curve.set_data(x, y)
         # 4) 刷新 VisPy 画布
         self.canvas.update()

class PlotButton(QWidget):
    def __init__(self):
        super(). __init__()
        self.button_start = QPushButton("START")
        self.button_stop_resume = QPushButton("STOP")


        #点击stop，光标按住的时候，stop变disable（灰色），松开时变成able的resume按钮

        self.button_start.setStyleSheet("background-color: white; color: black; ")
        self.button_stop_resume.setStyleSheet("background-color: white; color: black")




        self.layout = QHBoxLayout()
        self.layout.addWidget(self.button_start)
        self.layout.addWidget(self.button_stop_resume)

        self.setLayout(self.layout)
        # 放大按钮本身
        for btn in (self.button_start, self.button_stop_resume):
            btn.setMinimumHeight(0)
            btn.setMinimumWidth(60)
            btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.button_stop_resume.pressed.connect(self._on_pressed)
        self.button_stop_resume.released.connect(self._on_released)

    def _on_pressed(self):
        # 当鼠标按住时，把按钮禁用（变灰）
        self.button_stop_resume.setEnabled(False)

    def _on_released(self):
        # 当鼠标松开后，先切换文字
        if self.button_stop_resume.text() == "STOP":
            self.button_stop_resume.setText("RESUME")
        else:
            self.button_stop_resume.setText("STOP")

        # 恢复可用
        self.button_stop_resume.setEnabled(True)



