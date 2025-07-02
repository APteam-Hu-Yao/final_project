import socket
import threading
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

class TCPClient(QObject):
    data_received = pyqtSignal(np.ndarray)  
    connection_status = pyqtSignal(bool, str)  

    def __init__(self, host='localhost', port=12345):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.chunk_size = 32 * 18 * 4 

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.host, self.port))
            self.running = True
            self.connection_status.emit(True, f"Connected to {self.host}:{self.port}")
            threading.Thread(target=self.receive_data, daemon=True).start()
        except Exception as e:
            self.connection_status.emit(False, f"Connection failed: {e}")

    def receive_data(self):
        while self.running:
            try:
                data = self.socket.recv(self.chunk_size)
                if len(data) == self.chunk_size:
                    array = np.frombuffer(data, dtype=np.float32).reshape(32, 18)
                    self.data_received.emit(array)
                elif len(data) == 0: 
                    self.running = False
                    self.connection_status.emit(False, "Server closed connection")
                    break
                else:
                    self.connection_status.emit(False, "Incomplete data received")
            except socket.timeout:
                continue
            except Exception as e:
                self.running = False
                self.connection_status.emit(False, f"Receive error: {e}")
                break

    def disconnect(self):
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
            self.connection_status.emit(False, "Disconnected")

def main():
    # Create and connect the client
    client = TCPClient()
    client.connect()

    try:
        # Receive and process data
        while client.running:
            data = client.receive_data()
            if data is not None:
                # Print the received data
                client.print_data(data)
            
            # No need for additional sleep as we're already receiving at 1 chunk per second

    except KeyboardInterrupt:
        print("\nStopping client...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main() 