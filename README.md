# YOLO Seat Occupancy Monitor

Year 2025-2026, Group J4.

This is part of the group project of the course ENGG1101 "Engineering Challenge"
at the University of Hong Kong.

## Overview

A real-time seat occupancy monitoring system using YOLOv8 person detection and center-point occupancy checking. Designed to run on Raspberry Pi 5 with a webcam.

## Features

- YOLOv8 person detection with configurable confidence threshold
- Center-point method for seat occupancy determination
- Real-time video display with color-coded seat overlays (green = empty, red = occupied)
- **Web interface** with live video streaming and status dashboard
- Web-based seat configuration (no monitor required for headless setup!)
- Headless mode for console-only operation
- Interactive seat configuration tool
- Configurable frame rate (default: 2 FPS for Raspberry Pi optimization)

## Requirements

- Python 3.7+
- Webcam
- Raspberry Pi 5 (or any system with camera access)

## Installation

### Standard Installation

1. Clone this repository:

```bash
cd yolo-seat-occupancy-monitor
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create your configuration file:

```bash
cp config.example.json config.json
```

**Note:** `config.json` is gitignored (user-specific). The example file contains default values to get you started. You'll configure your specific seats later using the web interface or setup helper.

**First run:** YOLOv8s model (~22MB) will be automatically downloaded.

### Raspberry Pi Installation

For Raspberry Pi, follow these steps carefully to avoid installation issues:

**Important:** This project runs on CPU only - **NO NVIDIA CUDA required**. PyTorch will run in CPU mode on Raspberry Pi.

#### Option 1: Automated Installation (Recommended)

Run the installation script:

```bash
bash rpi_install.sh
```

This script will automatically:

- Upgrade pip, setuptools, and wheel
- Install CPU-only PyTorch (~200MB)
- Install remaining dependencies with piwheels
- Verify all packages are installed correctly

Then create your configuration file:

```bash
cp config.example.json config.json
```

#### Option 2: Manual Installation

1. Update pip and build tools (fixes `setuptools.build_meta` error):

```bash
python3 -m pip install --upgrade pip setuptools wheel
```

2. Install PyTorch with CPU-only support (lightweight, ~200MB vs ~2GB with CUDA):

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

3. Install remaining dependencies using piwheels (pre-built ARM wheels):

```bash
pip install -r requirements.txt --extra-index-url https://www.piwheels.org/simple
```

4. Create your configuration file:

```bash
cp config.example.json config.json
```

**Notes:**

- We use `opencv-python-headless` for Raspberry Pi compatibility (lighter weight, no GUI dependencies)
- PyTorch CPU-only version is sufficient for YOLO inference at 1-2 FPS
- Total installation size: ~500MB (vs 2-3GB with CUDA)

## Quick Start

### Before You Begin

If this is your first time running the project, make sure you have created your configuration file:

```bash
cp config.example.json config.json
```

This creates your personal config file (gitignored) from the example template.

### Option A: Web Interface (Recommended)

The web interface is the easiest way to get started, especially for headless Raspberry Pi setups.

#### 1. Start the Web Server

```bash
python web_server.py
```

The server will start on `http://localhost:1101` by default.

#### 2. Access the Interface

**On the same machine:**

- Open your browser to: http://localhost:1101

**From another device on the same network:**

- Find your IP address (Raspberry Pi: `hostname -I`)
- Open browser to: http://[your-ip]:1101
- Example: http://192.168.1.100:1101

#### 3. Configure Seats

- Click "Configure Seats" button
- Click "Capture Frame" to get a snapshot
- Click and drag to draw rectangles around each seat
- Enter labels for each seat
- Click "Save Configuration"

#### 4. Monitor Occupancy

- The main page shows live video with seat overlays
- Real-time status updates every 2 seconds
- Green = Empty, Red = Occupied, Blue = Reserved

Press Ctrl+C in the terminal to stop the server.

### Option B: Traditional CLI Mode

For advanced users or when you prefer command-line operation:

#### Step 1: Configure Seats (CLI Method)

Run the interactive setup tool to define seat locations (requires display):

```bash
python setup_helper.py
```

Instructions:

1. A webcam frame will appear
2. Click two corners (top-left, bottom-right) for each seat
3. Press 's' to save configuration
4. Press 'r' to reset if you make a mistake
5. Press 'q' to quit without saving

The configuration will be saved to `config.json`.

#### Step 2: Run the Monitor (CLI)

**With display window:**

```bash
python main.py
```

Press 'q' to quit.

**Headless mode (console output only):**

```bash
python main.py --headless
```

Press Ctrl+C to quit.

**Custom config file:**

```bash
python main.py --config custom_config.json
```

## Web Interface Details

### Available Pages

- **Main Dashboard** (`/`) - Live video stream and seat status display
- **Seat Configuration** (`/configure`) - Interactive seat setup tool

### API Endpoints

The web server provides REST API endpoints for integration:

- `GET /api/status` - Current seat statuses and person count
- `GET /api/seats` - Seat configuration
- `POST /api/seats` - Update seat configuration
- `GET /api/snapshot` - Single frame snapshot (JPEG)
- `GET /api/config` - Full configuration
- `GET /video_feed` - MJPEG video stream

### Network Access

By default, the server binds to `0.0.0.0:5000` (accessible from any device on your network).

**Security Note:** This is designed for local network use. If you need to expose it to the internet, consider adding authentication.

## Configuration

The `config.json` file contains:

```json
{
  "camera": {
    "source": 0, // Camera device index
    "width": 640, // Frame width
    "height": 480, // Frame height
    "fps_target": 2 // Target frame rate
  },
  "detection": {
    "confidence_threshold": 0.5, // Min confidence for person detection
    "model": "yolov8s.pt", // YOLO model
    "detect_items": true, // Whether to detect items (bags, etc.)
    "item_confidence_threshold": 0.4, // Confidence threshold for item detection
    "item_classes": [25, 26, 28, 61, 73] // COCO classes for items (backpack, handbag, etc.)
  },
  "seats": [
    {
      "id": 1,
      "label": "Seat 1",
      "x1": 100,
      "y1": 100,
      "x2": 250,
      "y2": 300
    }
  ]
}
```

## How It Works

1. **Person Detection**: Uses pre-trained YOLOv8s to detect persons in each frame
2. **Occupancy Check**: Calculates the center point of each detected person
3. **Seat Assignment**: If a person's center point falls within a seat's bounding box, the seat is marked as OCCUPIED
4. **Visualization**: Displays color-coded overlays (green = empty, red = occupied) and prints status to console

## Troubleshooting

**pip installation fails on Raspberry Pi:**

- Error: `Cannot import 'setuptools.build_meta'`
- **Root cause:** Outdated pip/setuptools, or PyTorch trying to install CUDA version
- **Solution:** Follow the 3-step Raspberry Pi installation above:

  ```bash
  # Step 1: Upgrade pip
  python3 -m pip install --upgrade pip setuptools wheel

  # Step 2: Install CPU-only PyTorch first
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

  # Step 3: Install remaining dependencies
  pip install -r requirements.txt --extra-index-url https://www.piwheels.org/simple
  ```

**CUDA/GPU errors on Raspberry Pi:**

- **You don't need CUDA!** This project runs on CPU only
- Make sure you installed PyTorch with `--index-url https://download.pytorch.org/whl/cpu`
- The CPU version is faster to install and takes less space (~200MB vs ~2GB)

**Camera not found:**

- Check camera is connected: `ls /dev/video*`
- Try different camera source in config.json (0, 1, 2, etc.)
- On RPi, ensure camera is enabled: `sudo raspi-config` → Interface Options → Camera

**YOLOv8 model download fails:**

- Ensure internet connection on first run
- Model will be cached for subsequent runs
- Location: `~/.cache/ultralytics/`

## Future Enhancements

Potential improvements for future versions:

1. **WebSocket Support**: More efficient real-time updates (currently uses MJPEG + polling)
1. **Occupancy Analytics**: Track usage patterns and statistics over time
1. **Multi-Camera Support**: Monitor multiple areas simultaneously
1. **User Authentication**: Password protection for web interface
1. **Historical Data**: Recording and playback of occupancy events

## Project Structure

```
yolo-seat-occupancy-monitor/
├── main.py                 # Main application (CLI mode)
├── web_server.py          # Flask web server (web mode)
├── camera.py              # Webcam capture wrapper
├── detector.py            # YOLOv8 person detection
├── occupancy_checker.py   # Seat occupancy logic
├── setup_helper.py        # Interactive seat configuration tool (CLI)
├── templates/             # HTML templates for web interface
│   ├── index.html        # Main monitoring dashboard
│   └── configure.html    # Seat configuration page
├── static/               # Static web assets
│   ├── css/
│   │   └── style.css    # Styling
│   └── js/
│       ├── monitor.js   # Dashboard JavaScript
│       └── configure.js # Configuration JavaScript
├── rpi_install.sh         # Automated Raspberry Pi installation script
├── config.json           # User configuration (gitignored, create from example)
├── config.example.json   # Configuration template (commit this)
└── requirements.txt      # Python dependencies
```

**Note:** `config.json` is gitignored to avoid conflicts. Each user creates their own from `config.example.json`.

## References

### Technology Stack

- **Ultralytics YOLOv8**: https://github.com/ultralytics/ultralytics
  - Official YOLOv8 implementation and documentation
  - Model: YOLOv8s (small) for optimal Raspberry Pi performance

- **OpenCV**: https://opencv.org/
  - Computer vision library for camera capture and image processing
  - Documentation: https://docs.opencv.org/

- **PyTorch**: https://pytorch.org/
  - Deep learning framework (CPU-only for Raspberry Pi)
  - Download CPU wheels: https://download.pytorch.org/whl/cpu

- **Flask**: https://flask.palletsprojects.com/
  - Lightweight Python web framework for the web interface
  - Simple, beginner-friendly, perfect for Year 1 students

- **Raspberry Pi**: https://www.raspberrypi.com/products/raspberry-pi-5/
  - Hardware platform: Raspberry Pi 5
- **Piwheels**: https://www.piwheels.org/
  - Pre-built ARM wheels for faster installation on Raspberry Pi

### Dataset

- **COCO Dataset**: https://cocodataset.org/
  - Pre-trained YOLOv8 model trained on COCO dataset
  - Includes "person" class for occupancy detection

## License

Part of ENGG1101 group project. For educational purposes.

## Acknowledgments

This project was developed for ENGG1101 "Engineering Challenge" at the University of Hong Kong.

**Technologies used:**

- Ultralytics YOLOv8 for object detection
- OpenCV for computer vision
- PyTorch for deep learning
- Flask for web interface
- Raspberry Pi 5 for edge deployment
