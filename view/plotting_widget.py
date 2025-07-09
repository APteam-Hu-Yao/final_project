import numpy as np
from vispy.scene import SceneCanvas
from vispy.scene.visuals import Line, Text
from vispy.color import Color
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QSizePolicy
from view.status_printer import StatusLabel

import time



class PlotPanel(QWidget):
    def __init__(self, max_points=1000, sampling_rate=2000, parent=None):
        super().__init__(parent)
        self.max_points = max_points  # 1000 样本，0.5 秒
        self.sampling_rate = sampling_rate  # 2000 Hz
        self.time_step = 1.0 / self.sampling_rate  # 0.0005 秒
        self.current_channel = 0
        self.update_count = 0
        self.sample_count = 0
        self.packet_count = 0
        # 初始化 VisPy 画布
        self.canvas = SceneCanvas(keys=None, bgcolor = Color("#4A628A"),parent=self)
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = 'panzoom'

        # 波形曲线
        self.curve = Line(color='white',width=2.0, parent=self.view.scene, method='gl')
        self.data = np.zeros(max_points, dtype=np.float32)
        self.times = np.linspace(0, max_points * self.time_step, max_points)
        self.ptr = 0

        # 横坐标刻度和标签
        self.axis_line = Line(parent=self.view.scene, color='white')
        self.tick_lines = []
        self.tick_labels = []
        self.tick_positions = np.arange(0, 0.51, 0.1)  # 0.0, 0.1, ..., 0.5 秒
        for _ in self.tick_positions:
            self.tick_lines.append(Line(parent=self.view.scene, color='white'))
            self.tick_labels.append(Text(parent=self.view.scene, color='white', font_size=8))

        self.update_axis()

        # 初始化视图范围
        self.view.camera.set_range(x=(0, max_points * self.time_step), y=(-2000, 2000))
        self.canvas.update()
        print(
            f"[PlotPanel] {time.strftime('%H:%M:%S')} Initialized canvas, max_points: {max_points}, sampling_rate: {self.sampling_rate} Hz")

        # 布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas.native)

    def update_axis(self):
        # 横坐标范围
        if self.sample_count == 0:
            x_min, x_max = 0, self.max_points * self.time_step
        else:
            current_time = self.sample_count * self.time_step
            x_min = current_time - self.max_points * self.time_step
            x_max = current_time

        # 纵坐标基线
        y_base = -20000 if self.current_channel == 0 else -2000
        tick_height = 0.05 * abs(y_base)
        label_offset = 0.06 * abs(y_base)

        # 绘制横轴主线
        self.axis_line.set_data(np.array([[x_min, y_base], [x_max, y_base]]))

        # 绘制刻度线 + 标签
        for i, tick_time in enumerate(self.tick_positions):
            tick_x = x_min + tick_time
            self.tick_lines[i].set_data(np.array([[tick_x, y_base], [tick_x, y_base + tick_height]]))
            self.tick_labels[i].text = f'{tick_time:.1f}s'
            self.tick_labels[i].pos = [tick_x, y_base - label_offset]

    def update_data(self, new_samples):

        try:
            if not isinstance(new_samples, np.ndarray):
                new_samples = np.zeros(18, dtype=np.float32)
                print(
                    f"[PlotPanel] {time.strftime('%H:%M:%S')} Non-array data received, using zeros, Channel: Ch {self.current_channel}")
            elif new_samples.size != 18:
                new_samples = np.zeros(18, dtype=np.float32)
                print(
                    f"[PlotPanel] {time.strftime('%H:%M:%S')} Incorrect data size {new_samples.size}, using zeros, Channel: Ch {self.current_channel}")

            n = len(new_samples)
            self.packet_count += 1
            if self.packet_count % 50 == 0:
                print(
                    f"[PlotPanel] {time.strftime('%H:%M:%S')} Received data {self.packet_count} for Ch {self.current_channel}, Samples: {n}, Amplitude: [{np.min(new_samples):.2f}, {np.max(new_samples):.2f}]")

            if n >= self.max_points:
                self.data[:] = new_samples[-self.max_points:]
                self.ptr = 0
            else:
                if self.ptr + n <= self.max_points:
                    self.data[self.ptr:self.ptr + n] = new_samples
                else:
                    part = self.max_points - self.ptr
                    self.data[self.ptr:] = new_samples[:part]
                    self.data[:n - part] = new_samples[part:]
                self.ptr = (self.ptr + n) % self.max_points

            self.sample_count += n
            current_time = self.sample_count * self.time_step
            self.times = np.linspace(current_time - self.max_points * self.time_step, current_time, self.max_points)

            vertices = np.vstack((self.times, self.data)).T
            self.curve.set_data(vertices)

            y_range = (-20000, 20000) if self.current_channel == 0 else (-2000, 2000)
            self.view.camera.set_range(x=(self.times[0], self.times[-1]), y=y_range)

            self.update_axis()

            self.canvas.update()
            self.canvas.app.process_events()
            if self.packet_count % 50 == 0:
                print(
                    f"[PlotPanel] {time.strftime('%H:%M:%S')} Rendered plot {self.packet_count}, Samples: {n}, Channel: Ch {self.current_channel}, y_range: {y_range}")
        except Exception as e:
            print(f"[PlotPanel] {time.strftime('%H:%M:%S')} update_data error: {e}")

    def set_color(self, color: str):
        color_map = {
            "White": "white",
            "Pink": "pink",
            "Neon Blue": "#00FFFF",
            "Neon Pink": "#FF69B4",
            "lime": "lime"
        }
        try:
            self.curve.set_data(color=color_map.get(color, "lime"))
            self.canvas.update()
            self.canvas.app.process_events()
            print(
                f"[PlotPanel] {time.strftime('%H:%M:%S')} Color changed to: {color}, Channel: Ch {self.current_channel}")
        except Exception as e:
            print(f"[PlotPanel] {time.strftime('%H:%M:%S')} set_color error: {e}")

    def reset_buffer(self, channel: int):
        self.packet_count = 0
        self.current_channel = channel
        self.data = np.zeros(self.max_points, dtype=np.float32)
        self.ptr = 0
        self.sample_count = 0
        self.times = np.linspace(0, self.max_points * self.time_step, self.max_points)
        self.curve.set_data(np.vstack((self.times, self.data)).T)
        y_range = (-20000, 20000) if self.current_channel == 0 else (-2000, 2000)
        self.view.camera.set_range(x=(0, self.max_points * self.time_step), y=y_range)
        self.update_axis()
        self.canvas.update()
        self.canvas.app.process_events()
        print(
            f"[PlotPanel] {time.strftime('%H:%M:%S')} Buffer reset for channel: Ch {self.current_channel}, y_range: {y_range}")

class PlotBar(QWidget):
    def __init__(self,view_model,parent = None):
        super().__init__(parent)
        self.view_model= view_model
        self.start_button = QPushButton('Start') #create the start button
        self.start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.start_button.setMinimumSize(0,100)
        self.start_button.setStyleSheet('background-color: #496989; color: white; font-family: "Segoe UI"; font-size:35px')
        self.stop_resume_button = QPushButton('Stop') #create the stop_resume button
        self.stop_resume_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.stop_resume_button.setMinimumSize(0,100)
        self.stop_resume_button.setStyleSheet('background-color: #496989; color: white; font-family: "Segoe UI"; font-size:35px')
        self.status_container = StatusLabel() #create the status label
        #place them horizontal
        layout = QHBoxLayout()
        layout.addWidget(self.status_container)
        layout.addStretch()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_resume_button)
        layout.addStretch()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setMinimumSize(750,125)
        # self.start_button.clicked.connect(self.view_model.start_plotting)
        # #toggle the stop/resume
        self.stop_resume_button.clicked.connect(self.toggle_button)
        # self.stop_resume_button.clicked.connect(self.view_model.toggle_pause)

    def toggle_button(self):
        # if it's stop, turn resume;else turn stop
        if self.stop_resume_button.text() == "Stop":
            self.stop_resume_button.setText("Resume")
            # 在这里可以插入暂停后的处理逻辑
        else:
            self.stop_resume_button.setText("Stop")
            # 在这里可以插入恢复后的处理逻辑







