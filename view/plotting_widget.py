from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from vispy.scene import SceneCanvas, Line, Text
from vispy.scene.cameras import PanZoomCamera
import numpy as np
import time

class PlotPanel(QWidget):
    def __init__(self, max_points=1000, sampling_rate=2000, parent=None):
        super().__init__(parent)
        self.max_points = max_points  # 1000 样本，0.5 秒
        self.sampling_rate = sampling_rate  # 2000 Hz
        self.time_step = 1.0 / self.sampling_rate  # 0.0005 秒
        self.current_channel = 0
        self.packet_count = 0

        # 初始化 VisPy 画布，启用交互
        self.canvas = SceneCanvas(keys='interactive', bgcolor='white', parent=self)
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = PanZoomCamera(interactive=True)

        # 波形曲线
        self.curve = Line(color='lime', parent=self.view.scene, method='gl')
        self.data = np.zeros(max_points, dtype=np.float32)
        self.times = np.linspace(0, max_points * self.time_step, max_points)
        self.ptr = 0

        # X 轴刻度和标签
        self.axis_line = Line(parent=self.view.scene, color='black')
        self.tick_lines = []
        self.tick_labels = []
        self.tick_positions = np.arange(0, 0.51, 0.1)  # 0.0, 0.1, ..., 0.5 秒
        for _ in self.tick_positions:
            self.tick_lines.append(Line(parent=self.view.scene, color='black'))
            self.tick_labels.append(Text(parent=self.view.scene, color='black', font_size=8))

        # Y 轴刻度和标签
        self.y_axis_line = Line(parent=self.view.scene, color='black')
        self.y_tick_lines = []
        self.y_tick_labels = []
        self.y_tick_positions = np.arange(-3000, 3001, 500)  # 初始刻度
        for _ in self.y_tick_positions:
            self.y_tick_lines.append(Line(parent=self.view.scene, color='black'))
            self.y_tick_labels.append(Text(parent=self.view.scene, color='black', font_size=8))

        # Y 轴数值标签（最小值和最大值）
        self.y_min_label = Text(text='Min: 0.00', color='black', font_size=10, parent=self.view.scene)
        self.y_max_label = Text(text='Max: 0.00', color='black', font_size=10, parent=self.view.scene)

        self.update_axis()

        # 初始化视图范围
        y_range = (-30000, 30000) if self.current_channel == 0 else (-2000, 2000)
        self.view.camera.set_range(x=(0, max_points * self.time_step), y=y_range)
        self.canvas.update()
        print(f"[PlotPanel] {time.strftime('%H:%M:%S')} Initialized canvas, max_points: {max_points}, sampling_rate: {self.sampling_rate} Hz, y_range: {y_range}")

        # 布局，增加底部边距
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 50)  # 底部留 50 像素
        layout.addWidget(self.canvas.native)
        self.setMinimumHeight(400)  # 确保画布高度足够

    def update_axis(self):
        current_time = self.ptr * self.time_step
        x_min, x_max = current_time - self.max_points * self.time_step, current_time
        y_min, y_max = self.view.camera.rect.bottom, self.view.camera.rect.top

        # 更新 X 轴，放置在 y=0 位置
        x_axis_y = 0  # X 轴固定在 y=0
        self.axis_line.set_data(np.array([[x_min, x_axis_y], [x_max, x_axis_y]]))
        tick_height = 0.025 * (y_max - y_min)  # 刻度长度
        label_offset = 300 if self.current_channel == 0 else 30  # 增加偏移量以将标签放低
        for i, tick_time in enumerate(self.tick_positions):
            tick_x = x_min + tick_time
            self.tick_lines[i].set_data(np.array([[tick_x, x_axis_y], [tick_x, x_axis_y + tick_height]]))
            # 跳过 0.0s 的标签
            self.tick_labels[i].text = '' if tick_time == 0 else f'{tick_time:.1f}s'
            self.tick_labels[i].pos = [tick_x, x_axis_y - label_offset]

        # 更新 Y 轴刻度
        self.y_tick_positions = np.arange(-30000, 30001, 5000) if self.current_channel == 0 else np.arange(-2000, 2001, 500)
        self.y_axis_line.set_data(np.array([[x_min, y_min], [x_min, y_max]]))
        y_tick_height = 0.02 * (x_max - x_min)
        y_label_offset = 0.03 * (x_max - x_min)
        for i, y_val in enumerate(self.y_tick_positions):
            self.y_tick_lines[i].set_data(np.array([[x_min, y_val], [x_min + y_tick_height, y_val]]))
            self.y_tick_labels[i].text = f'{y_val:.0f}'
            self.y_tick_labels[i].pos = [x_min - y_label_offset, y_val]

        # 更新 Y 轴标签位置（右上角）
        self.y_min_label.pos = [x_max - 0.1 * (x_max - x_min), y_max - 0.1 * (y_max - y_min)]
        self.y_max_label.pos = [x_max - 0.1 * (x_max - x_min), y_max - 0.2 * (y_max - y_min)]

    def update_data(self, new_samples):
        try:
            if not isinstance(new_samples, np.ndarray):
                new_samples = np.zeros(18, dtype=np.float32)
                print(f"[PlotPanel] {time.strftime('%H:%M:%S')} Non-array data received, using zeros, Channel: Ch {self.current_channel}")
            elif new_samples.size != 18:
                new_samples = np.zeros(18, dtype=np.float32)
                print(f"[PlotPanel] {time.strftime('%H:%M:%S')} Incorrect data size {new_samples.size}, using zeros, Channel: Ch {self.current_channel}")

            n = len(new_samples)
            self.packet_count += 1
            if self.packet_count % 50 == 0:
                print(f"[PlotPanel] {time.strftime('%H:%M:%S')} Received data {self.packet_count} for Ch {self.current_channel}, Samples: {n}, Amplitude: [{np.min(new_samples):.2f}, {np.max(new_samples):.2f}]")

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

            # 设置固定 Y 轴范围
            y_range = (-30000, 30000) if self.current_channel == 0 else (-2000, 2000)
            self.view.camera.set_range(x=(self.times[0], self.times[-1]), y=y_range)

            # 更新 Y 轴数值标签
            min_val, max_val = np.min(self.data), np.max(self.data)
            self.y_min_label.text = f'Min: {min_val:.2f}'
            self.y_max_label.text = f'Max: {max_val:.2f}'

            self.times = np.linspace(self.ptr * self.time_step - self.max_points * self.time_step, self.ptr * self.time_step, self.max_points)
            vertices = np.vstack((self.times, self.data)).T
            self.curve.set_data(vertices)

            self.update_axis()

            self.canvas.update()
            self.canvas.app.process_events()
            if self.packet_count % 50 == 0:
                print(f"[PlotPanel] {time.strftime('%H:%M:%S')} Rendered plot {self.packet_count}, Samples: {n}, Channel: Ch {self.current_channel}, y_range: {y_range}")
        except Exception as e:
            print(f"[PlotPanel] {time.strftime('%H:%M:%S')} update_data error: {e}")

    def set_color(self, color: str):
        color_map = {
            "Blue": "blue",
            "Pink": "pink",
            "Neon Blue": "#00FFFF",
            "Neon Pink": "#FF69B4",
            "lime": "lime"
        }
        try:
            self.curve.set_data(color=color_map.get(color, "lime"))
            self.canvas.update()
            self.canvas.app.process_events()
            print(f"[PlotPanel] {time.strftime('%H:%M:%S')} Color changed to: {color}, Channel: Ch {self.current_channel}")
        except Exception as e:
            print(f"[PlotPanel] {time.strftime('%H:%M:%S')} set_color error: {e}")

    def reset_buffer(self, channel: int):
        self.packet_count = 0
        self.current_channel = channel
        self.data = np.zeros(self.max_points, dtype=np.float32)
        self.ptr = 0
        self.times = np.linspace(0, self.max_points * self.time_step, self.max_points)
        self.curve.set_data(np.vstack((self.times, self.data)).T)
        y_range = (-30000, 30000) if self.current_channel == 0 else (-2000, 2000)
        self.view.camera.set_range(x=(0, self.max_points * self.time_step), y=y_range)
        self.y_min_label.text = 'Min: 0.00'
        self.y_max_label.text = 'Max: 0.00'
        self.update_axis()
        self.canvas.update()
        self.canvas.app.process_events()
        print(f"[PlotPanel] {time.strftime('%H:%M:%S')} Buffer reset for channel: Ch {self.current_channel}, y_range: {y_range}")