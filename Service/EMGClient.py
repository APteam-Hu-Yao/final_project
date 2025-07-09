import socket
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import time

class TCPClientThread(QThread):
    def __init__(self, client, chunk_size):
        super().__init__(parent=client)
        self.client = client
        self.chunk_size = chunk_size
        self.running = False
        self.packet_count = 0

    def run(self):
        self.running = True
        while self.running and self.client.running:
            if self.client.paused:
                self.msleep(100)
                continue
            try:
                data = self.client.socket.recv(self.chunk_size)
                if len(data) == self.chunk_size:
                    array = np.frombuffer(data, dtype=np.float32).reshape(18)
                    self.client.data_received.emit(array)
                    self.packet_count += 1
                    if self.packet_count % 500 == 0:
                        min_val, max_val = np.min(array), np.max(array)
                        print(f"[Client] {time.strftime('%H:%M:%S')} Received data packet {self.packet_count}, Shape: {array.shape}, Channel: Ch {self.client.current_channel}, Amplitude: [{min_val:.2f}, {max_val:.2f}], Bytes: {len(data)}")
                elif len(data) == 0:
                    self.running = False
                    self.client.connection_status.emit(False, "Server closed connection")
                    print(f"[Client] {time.strftime('%H:%M:%S')} Server closed connection")
                    self.client.reconnect()
                    break
                else:
                    print(f"[Client] {time.strftime('%H:%M:%S')} Incomplete data received: {len(data)} bytes")
            except socket.timeout:
                continue
            except Exception as e:
                self.running = False
                self.client.connection_status.emit(False, f"Receive error: {e}")
                print(f"[Client] {time.strftime('%H:%M:%S')} Receive error: {e}")
                self.client.reconnect()
                break

    def stop(self):
        self.running = False
        self.wait()

class TCPClient(QObject):
    data_received = pyqtSignal(np.ndarray)
    connection_status = pyqtSignal(bool, str)

    def __init__(self, host='localhost', port=12345, parent=None):
        super().__init__(parent)
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.paused = False
        self.current_channel = 0
        self.chunk_size = 18 * 4  # 18 float32 = 72 bytes
        self.thread = None
        self.connect()

    def connect(self):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"[Client] {time.strftime('%H:%M:%S')} Attempting connection {attempt+1}/{max_retries} to {self.host}:{self.port}")
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(5)
                self.socket.connect((self.host, self.port))
                self.running = True
                self.connection_status.emit(True, f"Connected to {self.host}:{self.port}")
                print(f"[Client] {time.strftime('%H:%M:%S')} Connected to {self.host}:{self.port}, Channel: Ch {self.current_channel}")
                self.thread = TCPClientThread(self, self.chunk_size)
                self.thread.start()
                return
            except Exception as e:
                print(f"[Client] {time.strftime('%H:%M:%S')} Connection attempt {attempt+1}/{max_retries} failed: {e}")
                time.sleep(1)
        self.connection_status.emit(False, f"Connection failed after {max_retries} attempts")
        print(f"[Client] {time.strftime('%H:%M:%S')} Connection failed after {max_retries} attempts")

    def reconnect(self):
        self.disconnect()
        print(f"[Client] {time.strftime('%H:%M:%S')} Attempting to reconnect...")
        self.connect()

    def disconnect(self):
        self.running = False
        self.paused = False
        if self.thread:
            self.thread.stop()
            self.thread = None
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self.connection_status.emit(False, "Disconnected")
            print(f"[Client] {time.strftime('%H:%M:%S')} Disconnected, Channel: Ch {self.current_channel}")

    def start(self, channel: int):
        self.current_channel = channel
        self.paused = False
        if self.running and self.socket:
            try:
                self.socket.send(f"start:channel:{channel}".encode())
                print(f"[Client] {time.strftime('%H:%M:%S')} Sent start:channel:{channel}")
            except Exception as e:
                self.connection_status.emit(False, f"Failed to send start: {e}")
                print(f"[Client] {time.strftime('%H:%M:%S')} Failed to send start: {e}")
                self.reconnect()
        else:
            self.connection_status.emit(False, "Not connected, cannot start")
            print(f"[Client] {time.strftime('%H:%M:%S')} Not connected, cannot start")
            self.reconnect()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.running and self.socket:
            try:
                message = "pause" if self.paused else "resume"
                self.socket.send(message.encode())
                self.connection_status.emit(not self.paused, "Paused" if self.paused else "Resumed")
                print(f"[Client] {time.strftime('%H:%M:%S')} Sent {message}, Channel: Ch {self.current_channel}")
            except Exception as e:
                self.connection_status.emit(False, f"Failed to send pause/resume: {e}")
                print(f"[Client] {time.strftime('%H:%M:%S')} Failed to send pause/resume: {e}")
                self.reconnect()
        else:
            self.connection_status.emit(False, "Not connected, cannot pause/resume")
            print(f"[Client] {time.strftime('%H:%M:%S')} Not connected, cannot pause/resume")
            self.reconnect()

    def send_channel(self, channel: int):
        self.current_channel = channel
        if self.running and self.socket:
            try:
                self.socket.send(f"switch:channel:{channel}".encode())
                print(f"[Client] {time.strftime('%H:%M:%S')} Sent switch:channel:{channel}")
            except Exception as e:
                self.connection_status.emit(False, f"Failed to send channel: {e}")
                print(f"[Client] {time.strftime('%H:%M:%S')} Failed to send channel: {e}")
                self.reconnect()
        else:
            self.connection_status.emit(False, "Not connected, cannot switch channel")
            print(f"[Client] {time.strftime('%H:%M:%S')} Not connected, cannot switch channel")
            self.reconnect()