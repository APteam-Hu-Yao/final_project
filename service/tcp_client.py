import socket
import numpy as np
import time

class EMGTCPClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.CHANNELS = 32
        self.SAMPLES_PER_PACKET = 18
        self.window_count = 0

    def print_data(self, data):
        """Print the received chunk of data"""
        print(f"\nReceived window {self.window_count}:")
        print(f"Shape: {data.shape}")
        self.window_count += 1

    def connect(self):
        """Connect to the TCP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.connected = False

    def receive_data(self):
        """Receive and process EMG data from the server"""
        if not self.connected:
            print("Not connected to server")
            return None

        try:
            # Receive data (32 channels × 18 samples of float32)
            buffer_size = self.CHANNELS * self.SAMPLES_PER_PACKET * 4  # 4 bytes per float32
            data = self.socket.recv(buffer_size)
            
            if not data:
                print("Connection closed by server")
                self.connected = False
                return None
            
            # Convert received bytes to numpy array
            # Reshape to (channels, samples)
            data_array = np.frombuffer(data, dtype=np.float32).reshape(self.CHANNELS, self.SAMPLES_PER_PACKET)
            
            return data_array
            
        except Exception as e:
            print(f"Error receiving data: {e}")
            self.connected = False
            return None

    def close(self):
        """Close the connection"""
        if self.socket:
            self.socket.close()
            self.connected = False
            print("Connection closed")

def main():
    # Create and connect the client
    client = EMGTCPClient()
    client.connect()

    try:
        # Receive and process data
        while client.connected:
            data = client.receive_data()
            if data is not None:
                # Print the received data
                client.print_data(data)
            
            # No need for additional sleep as we're already receiving at 1 chunk per second

    except KeyboardInterrupt:
        print("\nStopping client...")
    finally:
        client.close()

if __name__ == "__main__":
    main() 