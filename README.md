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
- Headless mode for console-only operation
- Interactive seat configuration tool
- Configurable frame rate (default: 2 FPS for Raspberry Pi optimization)

## Requirements

- Python 3.7+
- Webcam
- Raspberry Pi 5 (or any system with camera access)

## Installation

1. Clone this repository:
```bash
cd yolo-seat-occupancy-monitor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Note: On first run, YOLOv8n model (~6MB) will be automatically downloaded.

## Quick Start

### Step 1: Configure Seats

Run the interactive setup tool to define seat locations:

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

### Step 2: Run the Monitor

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

## Configuration

The `config.json` file contains:

```json
{
  "camera": {
    "source": 0,           // Camera device index
    "width": 640,          // Frame width
    "height": 480,         // Frame height
    "fps_target": 2        // Target frame rate
  },
  "detection": {
    "confidence_threshold": 0.5,  // Min confidence for person detection
    "model": "yolov8n.pt"         // YOLO model (nano for speed)
  },
  "seats": [
    {
      "id": 1,
      "label": "Seat 1",
      "x1": 100, "y1": 100,
      "x2": 250, "y2": 300
    }
  ]
}
```

## How It Works

1. **Person Detection**: Uses pre-trained YOLOv8n to detect persons in each frame
2. **Occupancy Check**: Calculates the center point of each detected person
3. **Seat Assignment**: If a person's center point falls within a seat's bounding box, the seat is marked as OCCUPIED
4. **Visualization**: Displays color-coded overlays (green = empty, red = occupied) and prints status to console

## Troubleshooting

**Camera not found:**
- Check camera is connected: `ls /dev/video*`
- Try different camera source in config.json (0, 1, 2, etc.)

**YOLOv8 model download fails:**
- Ensure internet connection on first run
- Model will be cached for subsequent runs

**Performance issues on Raspberry Pi:**
- Already using YOLOv8n (fastest variant)
- Reduce resolution in config.json (e.g., 320x240)
- Lower fps_target to 1

## Project Structure

```
yolo-seat-occupancy-monitor/
├── main.py                 # Main application
├── camera.py              # Webcam capture wrapper
├── detector.py            # YOLOv8 person detection
├── occupancy_checker.py   # Seat occupancy logic
├── setup_helper.py        # Interactive seat configuration tool
├── config.json           # Configuration file
└── requirements.txt      # Python dependencies
```

## License

Part of ENGG1101 group project. For educational purposes.
