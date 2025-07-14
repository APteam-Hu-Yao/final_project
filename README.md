# Signal Visualization Application

## Overview
This project is a PyQt5-based application developed for real-time visualization and offline analysis of 32-channel signal data, created as the Final Project for the Signal Visualization Application course. The application adheres to the Model-View-ViewModel (MVVM) architecture, ensuring a clear separation of concerns between data processing, business logic, and user interface. It supports real-time data streaming via TCP, real-time signal visualization using VisPy, and offline signal analysis using Matplotlib. The application provides a user-friendly interface for channel selection, connection management, and signal processing options, including raw signal display, RMS calculation, and bandpass filtering.

## Team Information
This project was completed by a team of two students with the following responsibilities:
- **Guanlin**: Focused on the View layer, including user interface design, visualization implementation (real-time and offline), and UI beautification. Responsible for creating an intuitive and visually appealing interface, with all bugs fixed in visualization widgets and updates implemented for offline visualization.
- **Yuxi**: Focused on the ViewModel and Service layers, including data processing, TCP communication, and business logic. Responsible for implementing robust TCP server-client functionality, real-time data handling, and signal processing.

Both team members contributed equally, collaborating to integrate the View, ViewModel, and Service layers seamlessly.

## Project Structure
The project is organized as follows:

```
final_project/
├── main.py                     # Application entry point
├── view/                      # View Layer 
│   ├── channels_widget.py     # Channel selection widget 
│   ├── custom_widget.py       # Custom visualization widget
│   ├── mainView.py            # Main window implementation 
│   ├── offlineView.py         # Offline visualization implementation 
│   ├── plotting_widget.py     # Plotting widget for real-time/offline visualization 
│   └── status_printer.py      # Status display widget for connection and streaming feedback
├── viewmodel/                 # ViewModel Layer 
│   ├── RealTimeViewModel.py   # Business logic for real-time visualization
│   └── OfflineViewModel.py    # Business logic for offline signal analysis
├── service/                   # Service Layer 
│   ├── DataProcessor.py       # Real-time data management and processing
│   ├── DataProcesorOffline.py # Offline data processing 
│   ├── EMGClient.py           # TCP client for data streaming
│   └── EMGServer.py           # TCP server for data streaming
├── others/                    # Additional resources
│   └── recording.pkl          # Sample data file for offline analysis
├── README.md                  # Project documentation
└── requirements.txt           # Project dependencies
```

## Application Features

### TCP Communication
- **TCP Connection Management**: Implements a robust TCP server (`EMGServer.py`) and client (`EMGClient.py`) for streaming 32-channel signal data.
- **Data Stream Reception**: Handles data chunks of 32 channels × 18 samples (576 values per chunk, transmitted as `np.float32`):
  - Data format: 18 samples per channel, 72 bytes per chunk (18 × 4 bytes).
- **Connection Handling**: Supports connection retries (up to 3 attempts), disconnection handling, and pause/resume functionality.
- **Error Handling**: Manages connection errors, incomplete data, and server disconnections with detailed logging and status updates via `status_printer.py`.

### Real-Time Signal Visualization 
- **Live Plotting**: Uses VisPy for smooth, low-latency visualization of real-time signal data for a selected channel (`plotting_widget.py`, bugs fixed).
- **Channel Selection**: Provides an intuitive interface for selecting one of the 32 channels (`channels_widget.py`, bugs fixed).
- **Smooth Updates**: Ensures seamless updates for real-time data streaming.
- **Optional Features**:
  - Toggle between raw signal, RMS signal, and bandpass-filtered signal.
  - Pause and resume buttons for controlling data streaming.
- **UI Design**: Features a clean, aesthetically pleasing interface with clear status indicators (`status_printer.py`) and customizable visualization options (`custom_widget.py`, bugs fixed).

### Offline Signal Analysis 
- **Complete Signal Visualization**: Uses Matplotlib to display the entire recorded signal for selected channels (`offlineView.py`, offline updates applied).
- **Analysis Tools**:
  - Time-domain visualization with raw or filtered signals.
  - Frequency-domain analysis with power spectrum computation.
  - RMS calculation for each channel.
- **Channel Selection**: Supports simultaneous visualization of multiple channels in offline mode (`channels_widget.py`).
- **Time Window Selection**: Allows users to specify a time range for analysis.
- **UI Beautification**: Includes well-designed plots with clear labels, legends, and customizable colors, with offline updates applied (`mainView.py`, `offlineView.py`).

### User Interface 
- **TCP Controls**: Buttons for starting, stopping, pausing, and resuming data streaming (`mainView.py`).
- **Channel Selection**: Dropdown or input field for selecting channels (0–31) (`channels_widget.py`).
- **Status Display**: Real-time feedback on connection status, streaming state, and data processing (`status_printer.py`).
- **Visualization Options**: Options to toggle between raw, RMS, and filtered signals, and to change plot colors for enhanced user experience (`custom_widget.py`, `plotting_widget.py`).

### Data Processing and Business Logic 
- **Real-Time Processing**: Handles incoming TCP data, validates chunk sizes, and applies processing (e.g., RMS, filtering) as needed (`DataProcessor.py`).
- **Offline Processing**: Loads and processes data from `recording.pkl` for offline analysis, including RMS and spectrum computation (`DataProcesorOffline.py`).
- **Business Logic**: Manages state transitions (e.g., channel switching, pause/resume) and coordinates data flow between the model and view (`RealTimeViewModel.py`, `OfflineViewModel.py`).

## Technical Requirements
- **Framework**: Built using PyQt5 for the GUI.
- **Architecture**: Strictly follows the MVVM pattern:
  - **Model**: `DataProcessor.py` and `DataProcesorOffline.py` handle data management and processing .
  - **ViewModel**: `RealTimeViewModel.py` and `OfflineViewModel.py` manage business logic and state .
  - **View**: Visualization components for real-time (VisPy) and offline (Matplotlib) modes, designed by Guanlin (`mainView.py`, `offlineView.py`, `plotting_widget.py`, etc.).
- **Visualization**:
  - Real-time visualization uses VisPy for high performance (`plotting_widget.py`).
  - Offline analysis uses Matplotlib for detailed and customizable plots (`offlineView.py`).
- **TCP Communication**:
  - Implements server-client architecture for streaming 32-channel data (`EMGServer.py`, `EMGClient.py`).
  - Buffers data for smooth visualization and handles errors gracefully.
- **Error Handling**:
  - Connection errors: Implements retries and emits status updates.
  - Data parsing: Validates data shapes (e.g., 18 samples per chunk) and logs issues.
  - Visualization: Handles empty or invalid data with user-friendly warnings displayed via `status_printer.py`.

## Setup and Usage Instructions

### Prerequisites
- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

### Installation
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd final_project
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure the `recording.pkl` file is placed in the `others/` directory for offline analysis.

### Running the Application
1. Start the TCP server:
   ```bash
   python service/EMGServer.py
   ```
2. Run the main application:
   ```bash
   python main.py
   ```
3. **TCP Connection**:
   - The server runs on `localhost:12345` by default (configurable in `EMGServer.py` and `EMGClient.py`).
   - The client connects to the server and streams data for the selected channel.
4. **Usage**:
   - Select a channel (0–31) via the UI (`channels_widget.py`) to visualize real-time data.
   - Use pause/resume buttons to control streaming (`mainView.py`).
   - Switch to offline mode to analyze the full signal with time or frequency domain options (`offlineView.py`).
   - Adjust visualization settings (e.g., raw/RMS/filtered signals, plot colors) via the UI (`custom_widget.py`, `plotting_widget.py`).

### TCP Connection Specifications
- **Host**: `localhost` (default, configurable)
- **Port**: `12345` (default, configurable)
- **Data Format**:
  - 32 channels, 18 samples per channel per chunk.
  - Data is sent as 32-bit float values (72 bytes per chunk).
- **Commands**:
  - `start:channel:<number>`: Starts streaming for the specified channel.
  - `switch:channel:<number>`: Switches to a different channel.
  - `pause`: Pauses the data stream.
  - `resume`: Resumes the data stream.

### Data Format Specifications
- **Real-Time Data**:
  - Each chunk contains 18 samples for a single channel.
  - Data is stored as `np.float32` in a NumPy array.
- **Offline Data**:
  - Loaded from `recording.pkl` (pickle file).
  - Contains 32 channels of biosignal data and device information (e.g., sampling frequency).
  - Shape: `(32, samples_per_window, num_windows)`.

## MVVM Architecture Implementation
- **Model** (`DataProcessor.py`, `DataProcesorOffline.py`):
  - Manages real-time and offline data processing.
  - Handles buffering, data validation, and signal processing (e.g., RMS, bandpass filtering).
- **ViewModel** (`RealTimeViewModel.py`, `OfflineViewModel.py`):
  - Coordinates data flow between the model and view.
  - Manages state (e.g., channel selection, filter type, pause status).
  - Emits signals for data updates, status changes, and warnings.
- **View** (Guanlin):
  - Implements GUI components and visualizations using VisPy (real-time) and Matplotlib (offline) (`mainView.py`, `offlineView.py`, `plotting_widget.py`).
  - Provides channel selection (`channels_widget.py`), custom visualization options (`custom_widget.py`), and status feedback (`status_printer.py`).
  - All visualization-related bugs have been fixed, and offline visualization has been updated for improved functionality.

## Dependencies
See `requirements.txt` for a complete list. Key dependencies include:
- `PyQt5`: For GUI framework.
- `numpy`: For numerical operations and data handling.
- `vispy`: For real-time visualization.
- `matplotlib`: For offline signal analysis.
- `pickle`: For loading offline data from `.pkl` files.


## Contact
For questions or issues, contact:
- Guanlin Hu: guanlin.hu@fau.de
- Yuxi Yao: yuxi.yao@fau.de