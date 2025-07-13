from vispy.scene.cameras import PanZoomCamera
import numpy as np
from vispy.scene import SceneCanvas
from vispy.scene.visuals import Line, Text
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QSizePolicy
from view.status_printer import StatusLabel
import time


class PlotPanel(QWidget):
    def __init__(self, max_points=1000, sampling_rate=2000, parent=None):
        super().__init__(parent)
        self.max_points = max_points  # 1000 samples, 0.5 seconds
        self.sampling_rate = sampling_rate  # 2000 Hz
        self.time_step = 1.0 / self.sampling_rate  # 0.0005 seconds
        self.current_channel = 0
        self.packet_count = 0
        self.sample_count = 0

        # Initialize VisPy canvas with interaction
        self.canvas = SceneCanvas(keys='interactive', bgcolor='#4A628A', parent=self)
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = PanZoomCamera(interactive=True)

        # Waveform curve
        self.curve = Line(color='white', width=2.0, parent=self.view.scene, method='gl')
        self.data = np.zeros(max_points, dtype=np.float32)
        self.times = np.linspace(0, max_points * self.time_step, max_points)
        self.ptr = 0

        # X-axis ticks and labels
        self.axis_line = Line(parent=self.view.scene, color='white')
        self.tick_lines = []
        self.tick_labels = []
        window_duration = self.max_points * self.time_step
        self.tick_positions = np.arange(0, window_duration + 0.1, 0.1)  # 0.0, 0.1, ..., 0.5 seconds
        for _ in self.tick_positions:
            self.tick_lines.append(Line(parent=self.view.scene, color='white'))
            self.tick_labels.append(Text(parent=self.view.scene, color='white', font_size=8))

        # Y-axis ticks and labels
        self.y_axis_line = Line(parent=self.view.scene, color='white')
        self.y_tick_lines = []
        self.y_tick_labels = []
        self.y_tick_positions = np.arange(-30000, 30001, 5000) if self.current_channel == 0 else np.arange(-2000, 2001, 500)
        for _ in self.y_tick_positions:
            self.y_tick_lines.append(Line(parent=self.view.scene, color='white'))
            self.y_tick_labels.append(Text(parent=self.view.scene, color='white', font_size=8))

        # Y-axis min/max labels
        self.y_min_label = Text(text='Min: 0.00', color='white', font_size=10, parent=self.view.scene)
        self.y_max_label = Text(text='Max: 0.00', color='white', font_size=10, parent=self.view.scene)

        self.update_axis()

        # Initialize view range
        y_range = (-30000, 30000) if self.current_channel == 0 else (-2000, 2000)
        self.view.camera.set_range(x=(0, max_points * self.time_step), y=y_range)
        self.canvas.update()
        print(f"[PlotPanel] {time.strftime('%H:%M:%S')} Initialized canvas, max_points: {max_points}, sampling_rate: {self.sampling_rate} Hz, y_range: {y_range}")

        # place it
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 50)
        layout.addWidget(self.canvas.native)
        self.setMinimumHeight(400)

    def update_axis(self):
        window_duration = self.max_points * self.time_step
        current_time  = self.sample_count * self.time_step

        if current_time < window_duration:
            x_min, x_max = 0.0, window_duration
        else:
            x_min, x_max = current_time - window_duration, current_time


        y_min, y_max = (-30000, 30000) if self.current_channel == 0 else (-2000, 2000)


        x_axis_y = y_min
        self.axis_line.set_data(np.array([[x_min, x_axis_y],
                                          [x_max, x_axis_y]]))

        tick_height  = 0.025 * (y_max - y_min)
        label_offset = 300 if self.current_channel == 0 else 30

        self.tick_positions = np.arange(0, window_duration + 1e-8, 0.1)
        for i, tick_time in enumerate(self.tick_positions):
            if i >= len(self.tick_lines):
                self.tick_lines.append(Line(parent=self.view.scene, color='white'))
                self.tick_labels.append(Text(parent=self.view.scene, color='white',
                                             font_size=8))
            tick_x = x_min + tick_time
            self.tick_lines[i].set_data(np.array([[tick_x, x_axis_y],
                                                  [tick_x, x_axis_y + tick_height]]))
            self.tick_labels[i].text = '' if tick_time == 0 else f'{tick_time:.1f}s'
            self.tick_labels[i].pos  = [tick_x, x_axis_y - label_offset]

        self.y_axis_line.set_data(np.array([[x_min, y_min], [x_min, y_max]]))
        y_tick_height = 0.02 * (x_max - x_min)
        y_label_offset = 0.03 * (x_max - x_min)
        self.y_tick_positions = np.arange(-30000, 30001, 5000) if self.current_channel == 0 else np.arange(-2000, 2001, 500)
        for i, y_val in enumerate(self.y_tick_positions):
            if i >= len(self.y_tick_lines):
                self.y_tick_lines.append(Line(parent=self.view.scene, color='white'))
                self.y_tick_labels.append(Text(parent=self.view.scene, color='white', font_size=8))
            self.y_tick_lines[i].set_data(np.array([[x_min, y_val], [x_min + y_tick_height, y_val]]))
            self.y_tick_labels[i].text = f'{y_val:.0f}'
            self.y_tick_labels[i].pos = [x_min - y_label_offset, y_val]

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
            self.sample_count += n
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

            current_time = self.sample_count * self.time_step
            window = self.max_points * self.time_step

            if current_time < window:
                start, end = 0.0, window
            else:
                start, end = current_time - window, current_time

            self.times = np.linspace(start, end, self.max_points)
            vertices = np.vstack((self.times, self.data)).T
            self.curve.set_data(vertices)

            min_val, max_val = self.data.min(), self.data.max()

            self.y_min_label.text = f'Min: {min_val:.2f}'
            self.y_max_label.text = f'Max: {max_val:.2f}'

            offset_x = start - 0.05 * (end - start)
            self.y_min_label.pos = (offset_x, min_val)
            self.y_max_label.pos = (offset_x, max_val)

            y_range = (-30000, 30000) if self.current_channel == 0 else (-2000, 2000)
            self.view.camera.set_range(x=(start, end), y=y_range)

            self.update_axis()

            self.canvas.update()
            self.canvas.app.process_events()
            if self.packet_count % 50 == 0:
                print(f"[PlotPanel] {time.strftime('%H:%M:%S')} Rendered plot {self.packet_count}, Samples: {n}, Channel: Ch {self.current_channel}, y_range: {y_range}")
        except Exception as e:
            print(f"[PlotPanel] {time.strftime('%H:%M:%S')} update_data error: {e}")

    def set_color(self, color: str):
        color_map = {
            "White": "white",
            "Pink": "#FFC0CB",
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
        self.sample_count = 0
        self.current_channel = channel
        self.data = np.zeros(self.max_points, dtype=np.float32)
        self.ptr = 0
        self.times = np.linspace(0, self.max_points * self.time_step, self.max_points)
        self.curve.set_data(np.vstack((self.times, self.data)).T)
        self.y_min_label.text = 'Min: 0.00'
        self.y_max_label.text = 'Max: 0.00'
        y_range = (-30000, 30000) if self.current_channel == 0 else (-2000, 2000)
        self.view.camera.set_range(x=(0, self.max_points * self.time_step), y=y_range)
        self.update_axis()
        self.canvas.update()
        self.canvas.app.process_events()
        print(f"[PlotPanel] {time.strftime('%H:%M:%S')} Buffer reset for channel: Ch {self.current_channel}, y_range: {y_range}")

class PlotBar(QWidget):
    def __init__(self,view_model,parent = None):
        super().__init__(parent)
        self.view_model= view_model
        self.start_button = QPushButton('Start') #create the start button
        self.start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.start_button.setMinimumSize(0,100)
        self.start_button.setStyleSheet('background-color: #496989; color: white; font-size:35px')
        self.stop_resume_button = QPushButton('Stop') #create the stop_resume button
        self.stop_resume_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.stop_resume_button.setMinimumSize(0,100)
        self.stop_resume_button.setStyleSheet('background-color: #496989; color: white; font-size:35px')
        self.offline_button = QPushButton("Offline") #create the offline view button
        self.offline_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.offline_button.setMinimumSize(0, 75)
        self.offline_button.setStyleSheet('background-color: #9AA6B2; color: black; font-size:35px')


        self.status_container = StatusLabel() #create the status label

        #place them horizontal
        layout = QHBoxLayout()
        layout.addWidget(self.status_container)
        layout.addStretch()
        layout.addWidget(self.start_button)
        layout.addSpacing(20)
        layout.addWidget(self.stop_resume_button)
        layout.addSpacing(300)
        layout.addWidget(self.offline_button)

        # adjust the space
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setMinimumSize(750,125)
