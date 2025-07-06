import pickle
import socket
import threading
import time
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

class EMGTCPServer(QObject):
    data_received = pyqtSignal(np.ndarray)  # 32x18 
    connection_status = pyqtSignal(bool, str) 

    def __init__(self, host='localhost', port=12345, pkl_file= 'others/recording.pkl'):
        
        super().__init__()
        self.host = host
        self.port = port
        self.pkl_file = pkl_file
        self.server_socket = None
        self.clients = []
        self.client_lock = threading.Lock()  # 保护 clients 列表的线程锁
        self.running = False
        self.paused = False
        self.data = None
        self.sampling_rate = None
        self.CHANNELS = 32
        self.SAMPLES_PER_PACKET = 18
        self.load_data()

    def load_data(self):
        try:
            with open(self.pkl_file, 'rb') as f:
                self.data = pickle.load(f)
            self.emg_signal = self.data['biosignal'][:32, :, :]
            self.sampling_rate = self.data['device_information']['sampling_frequency']
            if not isinstance(self.sampling_rate, (int, float)) or self.sampling_rate <= 0:
                raise ValueError("Invalid sampling rate")
            self.connection_status.emit(True, f"Data loaded successfully. Shape: {self.emg_signal.shape}, Sampling rate: {self.sampling_rate} Hz")
        except Exception as e:
            self.connection_status.emit(False, f"Error loading data: {e}")
            raise

    def print_data(self, data, window_index):

        print(f"\nSending window {window_index}:")
        print(f"Shape: {data.shape}")
        print("Data values:")
        for i in range(min(5, data.shape[0])): 
            print(f"Channel {i+1}: {data[i, :]}")
        print("-" * 50)

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            self.connection_status.emit(True, f"Server started on {self.host}:{self.port}")
            
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
        except Exception as e:
            self.connection_status.emit(False, f"Server start failed: {e}")
            raise

    def accept_connections(self):
        while self.running:
            try:
                self.server_socket.settimeout(1.0) 
                client_socket, address = self.server_socket.accept()
                with self.client_lock:
                    self.clients.append(client_socket)
                self.connection_status.emit(True, f"New connection from {address}")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.connection_status.emit(False, f"Error accepting connection: {e}")

    def handle_client(self, client_socket):
        try:
            num_windows = self.emg_signal.shape[2]
            window_index = 0
            while self.running and window_index < num_windows:
                if self.paused:
                    time.sleep(0.1)  
                    continue
                current_window = self.emg_signal[..., window_index]
                self.print_data(current_window, window_index)
                data_bytes = current_window.tobytes()
                client_socket.sendall(data_bytes)
                self.data_received.emit(current_window)
                sleep_time = self.SAMPLES_PER_PACKET / self.sampling_rate
                time.sleep(sleep_time)
                window_index += 1
                if window_index >= num_windows:
                    window_index = 0
                    self.connection_status.emit(True, "Restarting data transmission")
        except Exception as e:
            self.connection_status.emit(False, f"Client error: {e}")
        finally:
            with self.client_lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
            client_socket.close()
            self.connection_status.emit(False, "Client disconnected")

    def toggle_pause(self):
        self.paused = not self.paused
        self.connection_status.emit(not self.paused, "Paused" if self.paused else "Resumed")

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        with self.client_lock:
            for client in self.clients:
                client.close()
            self.clients.clear()
        self.connection_status.emit(False, "Server stopped")

    
if __name__ == "__main__":
    server = EMGTCPServer()
    try:
        server.start()
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop() 