#!/usr/bin/env python3
"""
Flask web server for YOLO seat occupancy monitoring.
Provides web interface with live video stream and seat status display.
"""

import json
import time
from datetime import datetime

import cv2
from flask import Flask, Response, jsonify, render_template, request

from camera import Camera
from detector import PersonDetector
from occupancy_checker import check_occupancy, draw_overlay, load_seats

# Initialize Flask app
app = Flask(__name__)

# Global variables for camera, detector, and configuration
camera = None
detector = None
config = None
seats = []


def load_config(config_path="config.json"):
    """Load configuration from JSON file."""
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_path}")
        print("Please run 'python setup_helper.py' to create seat configuration.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        return None


def save_config(config_data, config_path="config.json"):
    """Save configuration to JSON file."""
    try:
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def initialize_system():
    """Initialize camera and detector from config."""
    global camera, detector, config, seats

    # Load configuration
    config = load_config()
    if config is None:
        raise RuntimeError("Failed to load configuration")

    # Extract config values
    camera_config = config.get("camera", {})
    detection_config = config.get("detection", {})

    camera_source = camera_config.get("source", 0)
    camera_width = camera_config.get("width", 640)
    camera_height = camera_config.get("height", 480)

    model_path = detection_config.get("model", "yolov8n.pt")
    confidence_threshold = detection_config.get("confidence_threshold", 0.5)

    # Load seats
    seats = config.get("seats", [])

    # Initialize camera
    print("Initializing camera...")
    try:
        camera = Camera(source=camera_source, width=camera_width, height=camera_height)
    except RuntimeError as e:
        raise RuntimeError(f"Camera initialization failed: {e}")

    # Initialize person detector
    print("Loading YOLO model (this may take a moment on first run)...")
    try:
        detector = PersonDetector(
            model_path=model_path, confidence_threshold=confidence_threshold
        )
    except RuntimeError as e:
        raise RuntimeError(f"Detector initialization failed: {e}")

    print(f"System initialized with {len(seats)} seat(s)")


def generate_frames():
    """
    Generator function for MJPEG video stream.
    Continuously captures frames, runs detection, and yields JPEG images.
    """
    global camera, detector, seats

    # Get target FPS from config
    fps_target = config.get("camera", {}).get("fps_target", 2)
    frame_delay = 1.0 / fps_target if fps_target > 0 else 0.5

    while True:
        try:
            # Capture frame
            frame = camera.get_frame()
            if frame is None:
                print("Warning: Failed to capture frame")
                time.sleep(frame_delay)
                continue

            # Detect persons
            person_detections = detector.detect(frame)

            # Check occupancy
            statuses = check_occupancy(person_detections, seats)

            # Draw overlay
            frame_with_overlay = draw_overlay(frame, seats, statuses, person_detections)

            # Encode frame as JPEG
            ret, buffer = cv2.imencode(
                ".jpg", frame_with_overlay, [cv2.IMWRITE_JPEG_QUALITY, 85]
            )
            if not ret:
                print("Warning: Failed to encode frame")
                time.sleep(frame_delay)
                continue

            frame_bytes = buffer.tobytes()

            # Yield frame in multipart format
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )

            # Control frame rate
            time.sleep(frame_delay)

        except Exception as e:
            print(f"Error in frame generation: {e}")
            time.sleep(frame_delay)


@app.route("/")
def index():
    """Main monitoring page."""
    return render_template("index.html")


@app.route("/configure")
def configure():
    """Seat configuration page."""
    return render_template("configure.html")


@app.route("/video_feed")
def video_feed():
    """MJPEG video stream endpoint."""
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/api/status")
def api_status():
    """
    Get current seat occupancy status.
    Returns JSON with seat statuses and timestamp.
    """
    global camera, detector, seats

    try:
        # Capture frame
        frame = camera.get_frame()
        if frame is None:
            return jsonify({"error": "Failed to capture frame"}), 500

        # Detect persons
        person_detections = detector.detect(frame)

        # Check occupancy
        statuses = check_occupancy(person_detections, seats)

        # Build response
        seat_statuses = []
        for seat in seats:
            seat_id = seat["id"]
            seat_statuses.append(
                {
                    "id": seat_id,
                    "label": seat["label"],
                    "status": statuses.get(seat_id, "EMPTY"),
                }
            )

        return jsonify(
            {
                "seats": seat_statuses,
                "timestamp": datetime.now().isoformat(),
                "person_count": len(person_detections),
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/snapshot")
def api_snapshot():
    """
    Get a single frame snapshot (for seat configuration).
    Returns JPEG image without overlay.
    """
    global camera

    try:
        # Capture frame
        frame = camera.get_frame()
        if frame is None:
            return jsonify({"error": "Failed to capture frame"}), 500

        # Encode as JPEG
        ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        if not ret:
            return jsonify({"error": "Failed to encode frame"}), 500

        # Return image
        return Response(buffer.tobytes(), mimetype="image/jpeg")

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/seats", methods=["GET"])
def api_seats_get():
    """Get current seat configuration."""
    global seats, config

    return jsonify(
        {
            "seats": seats,
            "camera": {
                "width": config.get("camera", {}).get("width", 640),
                "height": config.get("camera", {}).get("height", 480),
            },
        }
    )


@app.route("/api/seats", methods=["POST"])
def api_seats_post():
    """
    Update seat configuration.
    Expects JSON body with 'seats' array.
    """
    global seats, config

    try:
        data = request.get_json()
        if not data or "seats" not in data:
            return jsonify({"error": "Missing 'seats' in request body"}), 400

        new_seats = data["seats"]

        # Validate seat data
        for seat in new_seats:
            required_fields = ["id", "label", "x1", "y1", "x2", "y2"]
            for field in required_fields:
                if field not in seat:
                    return jsonify({"error": f"Missing field '{field}' in seat"}), 400

            # Validate coordinates
            if seat["x1"] >= seat["x2"] or seat["y1"] >= seat["y2"]:
                return (
                    jsonify({"error": f"Invalid coordinates for seat {seat['id']}"}),
                    400,
                )

        # Update config
        config["seats"] = new_seats
        seats = new_seats

        # Save to file
        if not save_config(config):
            return jsonify({"error": "Failed to save configuration"}), 500

        return jsonify({"success": True, "message": f"Saved {len(new_seats)} seat(s)"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/config")
def api_config():
    """Get full configuration (read-only)."""
    global config
    return jsonify(config)


def main():
    """Main entry point."""
    print("=" * 60)
    print("YOLO Seat Occupancy Monitor - Web Server")
    print("=" * 60)

    try:
        # Initialize system
        initialize_system()

        print("\nWeb server starting...")
        print("Access the interface at: http://localhost:1101")
        print("Or from another device: http://[your-ip]:1101")
        print("\nPress Ctrl+C to stop")
        print("-" * 60)

        # Run Flask app
        app.run(host="0.0.0.0", port=1101, debug=False, threaded=True)

    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Cleanup
        if camera:
            camera.release()
        print("Cleanup complete. Goodbye!")


if __name__ == "__main__":
    main()
