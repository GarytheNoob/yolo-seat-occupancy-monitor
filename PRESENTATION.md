# YOLO Seat Occupancy Monitor

**ENGG1101 Engineering Challenge | Group J4 | 2025-2026**  
**University of Hong Kong**

---

## 📌 Project Overview

**Objective:** Real-time seat occupancy monitoring system using computer vision

**Platform:** Raspberry Pi 5 with webcam

**Key Innovation:** Web-based interface with remote seat configuration (no monitor required for headless deployment)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────┐
│              User Interface                     │
│  ┌──────────────┐      ┌──────────────────┐     │
│  │  CLI Mode    │      │  Web Interface   │     │
│  │  (main.py)   │      │  (web_server.py) │     │
│  └──────┬───────┘      └────────┬─────────┘     │
│         │                       │               │
│         └───────────┬───────────┘               │
│                     │                           │
│         ┌───────────▼────────────┐              │
│         │   Backend Modules      │              │
│         │  • camera.py           │              │
│         │  • detector.py         │              │
│         │  • occupancy_checker.py│              │
│         └────────────────────────┘              │
│                     │                           │
│         ┌───────────▼────────────┐              │
│         │  Hardware & Libraries  │              │
│         │  • Webcam              │              │
│         │  • YOLOv8n             │              │
│         │  • OpenCV              │              │
│         └────────────────────────┘              │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Core Components

### Backend (941 lines Python)

- **`main.py`** - CLI application with console/window display
- **`web_server.py`** - Flask web server with MJPEG streaming
- **`camera.py`** - Webcam capture wrapper
- **`detector.py`** - YOLOv8 person detection
- **`occupancy_checker.py`** - Seat occupancy logic (center-point method)

### Frontend (1,478 lines HTML/CSS/JS)

- **`templates/index.html`** - Live monitoring dashboard
- **`templates/configure.html`** - Interactive seat configuration
- **`static/js/monitor.js`** - Real-time status updates
- **`static/js/configure.js`** - Canvas-based seat drawing
- **`static/css/style.css`** - Responsive design

### Configuration

- **`config.json`** - User-specific settings (camera, seats) - gitignored
- **`config.example.json`** - Template for new deployments

---

## 💡 Key Technical Implementation

### 1. Occupancy Detection Algorithm

- **Method:** Center-point detection
- **Logic:** If person's bounding box center falls within seat area → OCCUPIED
- **Why:** Simple, accurate, avoids false positives from people walking by
- **Threshold:** 0.5 confidence for person detection

### 2. Web Interface

- **Video Streaming:** MJPEG format (simple, works with `<img>` tag)
- **Status Updates:** REST API polling every 2 seconds
- **Seat Configuration:** HTML5 Canvas with mouse-based drawing
- **Network Access:** Accessible from any device on local network

### 3. Performance Optimization

- **Model:** YOLOv8n (nano) - fastest variant
- **Target FPS:** 1-2 FPS (optimized for Raspberry Pi 5)
- **Resolution:** 640×480 (configurable)
- **Processing:** CPU-only (no CUDA required)

---

## 📊 Project Statistics

| Metric                | Value                                 |
| --------------------- | ------------------------------------- |
| **Total Code**        | ~2,400 lines                          |
| **Python Backend**    | 941 lines                             |
| **Web Frontend**      | 1,478 lines                           |
| **Core Modules**      | 5 Python files                        |
| **Web Pages**         | 2 HTML templates                      |
| **Dependencies**      | 4 (ultralytics, opencv, numpy, flask) |
| **Installation Size** | ~500MB (with PyTorch CPU)             |
| **Model Size**        | ~6MB (YOLOv8n)                        |

---

## ✨ Key Features

### Two Operation Modes

- **CLI Mode:** Traditional command-line with OpenCV window
- **Web Mode:** Browser-based interface (recommended for Raspberry Pi)

### Web Interface Capabilities

- Live video stream with seat overlays (green=empty, red=occupied)
- Real-time status updates
- Interactive seat configuration (click & drag to define areas)
- Remote access from any device on network
- Mobile-friendly responsive design

### Raspberry Pi Optimizations

- CPU-only inference (no GPU required)
- Automated installation script (`rpi_install.sh`)
- Headless operation support
- Piwheels integration for faster ARM installation

---

## 🔄 System Workflow

### 1. **Initialization**

- Load configuration (camera settings, seat definitions)
- Initialize webcam
- Load YOLOv8n model

### 2. **Detection Loop** (1-2 FPS)

- Capture frame from camera
- Run YOLO person detection
- Calculate center point of each detected person
- Check if center point falls within any seat bounding box

### 3. **Output**

- **CLI Mode:** Console text + OpenCV window with overlays
- **Web Mode:** MJPEG stream + JSON status updates

### 4. **Configuration**

- **CLI Tool:** `setup_helper.py` (requires display)
- **Web Tool:** Browser-based canvas drawing (works headless)

---

## 🛠️ Technology Stack

| Component            | Technology               | Purpose                          |
| -------------------- | ------------------------ | -------------------------------- |
| **Object Detection** | YOLOv8n (Ultralytics)    | Person detection                 |
| **Computer Vision**  | OpenCV                   | Camera capture, image processing |
| **Deep Learning**    | PyTorch (CPU)            | YOLO inference engine            |
| **Web Framework**    | Flask                    | HTTP server, REST API            |
| **Frontend**         | HTML5 Canvas, Vanilla JS | Interactive configuration        |
| **Platform**         | Raspberry Pi 5           | Edge deployment                  |

---

## 📦 Deployment

### Installation Methods

1. **Standard:** `pip install -r requirements.txt`
2. **Raspberry Pi (Automated):** `bash rpi_install.sh`
3. **Raspberry Pi (Manual):** 3-step process (pip upgrade → PyTorch CPU → requirements)

### Running the System

```bash
# Web interface (recommended)
python web_server.py
# Access: http://localhost:5000

# CLI mode
python main.py                  # With display window
python main.py --headless       # Console only
```

### Resource Requirements

- **RAM:** ~400MB (with model loaded)
- **Storage:** ~500MB (PyTorch + dependencies)
- **CPU:** Raspberry Pi 5 (or any system with camera)
- **Network:** Local network for web interface

---

## 🎯 Design Decisions

### Why Center-Point Method?

- Simpler than IoU (Intersection over Union) calculations
- Fewer false positives from people passing by
- Computationally efficient for Raspberry Pi
- Intuitive: person's center must be in seat to count

### Why YOLOv8n?

- Smallest/fastest YOLO variant
- Pre-trained on COCO dataset (includes "person" class)
- No custom training required
- Good balance of speed vs accuracy for RPi

### Why Web Interface?

- Solves headless Raspberry Pi configuration problem
- Remote monitoring from any device
- No monitor needed for deployment
- Better user experience than CLI

### Why Flask over FastAPI?

- Simpler for Year 1 engineering students
- Well-documented and beginner-friendly
- Sufficient for single-user RPi deployment
- Smaller learning curve

---

## 📂 Project Structure

```
yolo-seat-occupancy-monitor/
├── main.py                  # CLI application
├── web_server.py           # Web server
├── camera.py               # Webcam wrapper
├── detector.py             # YOLO detection
├── occupancy_checker.py    # Occupancy logic
├── setup_helper.py         # CLI seat config tool
├── templates/              # Web UI templates
│   ├── index.html         # Dashboard
│   └── configure.html     # Seat setup
├── static/                 # Web assets
│   ├── css/style.css      # Styling
│   └── js/
│       ├── monitor.js     # Status updates
│       └── configure.js   # Interactive drawing
├── config.example.json     # Template
├── rpi_install.sh         # RPi installer
└── requirements.txt        # Dependencies
```

---

## 🔮 Future Enhancements

- Reserved seat detection (books/bags on empty seats)
- WebSocket support (more efficient than polling)
- Occupancy analytics and historical data
- Multi-camera support
- User authentication for web interface

---

## 📖 References

- **YOLOv8:** Ultralytics (https://github.com/ultralytics/ultralytics)
- **Dataset:** COCO (pre-trained person detection)
- **Platform:** Raspberry Pi 5
- **Computer Vision:** OpenCV
- **Web Framework:** Flask

---

**Project Repository:** ENGG1101 Engineering Challenge  
**Developed by:** Group J4  
**Academic Year:** 2025-2026  
**Institution:** University of Hong Kong
