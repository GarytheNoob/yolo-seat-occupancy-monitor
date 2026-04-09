#!/usr/bin/env python3
"""
Main application for YOLO seat occupancy monitoring.
Captures webcam feed, detects persons, and checks seat occupancy.
"""

import argparse
import json
import time
import cv2
from datetime import datetime

from camera import Camera
from detector import PersonDetector
from occupancy_checker import load_seats, check_occupancy, draw_overlay


def load_config(config_path):
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_path}")
        print("Please run 'python setup_helper.py' to create seat configuration.")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        exit(1)


def format_status_line(seats, statuses):
    """Format seat statuses as a single line for console output."""
    status_parts = []
    for seat in seats:
        seat_id = seat["id"]
        label = seat["label"]
        status = statuses.get(seat_id, "EMPTY")
        status_parts.append(f"{label}: {status}")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] " + " | ".join(status_parts)


def main():
    """Main application entry point."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="YOLO Seat Occupancy Monitor")
    parser.add_argument("--headless", action="store_true",
                        help="Run without display window (console output only)")
    parser.add_argument("--config", type=str, default="config.json",
                        help="Path to config file (default: config.json)")
    args = parser.parse_args()
    
    # Load configuration
    print(f"Loading configuration from {args.config}...")
    config = load_config(args.config)
    
    # Extract config values
    camera_config = config.get("camera", {})
    detection_config = config.get("detection", {})
    
    camera_source = camera_config.get("source", 0)
    camera_width = camera_config.get("width", 640)
    camera_height = camera_config.get("height", 480)
    fps_target = camera_config.get("fps_target", 2)
    
    model_path = detection_config.get("model", "yolov8s.pt")
    confidence_threshold = detection_config.get("confidence_threshold", 0.5)
    detect_items = detection_config.get("detect_items", True)
    item_confidence_threshold = detection_config.get("item_confidence_threshold", 0.4)
    
    # Load seats
    seats = load_seats(args.config)
    print(f"Loaded {len(seats)} seat(s)")
    
    # Initialize camera
    print("Initializing camera...")
    try:
        camera = Camera(source=camera_source, width=camera_width, height=camera_height)
    except RuntimeError as e:
        print(f"Error: {e}")
        exit(1)
    
    # Initialize person detector
    print("Loading YOLO model (this may take a moment on first run)...")
    try:
        detector = PersonDetector(model_path=model_path, 
                                 confidence_threshold=confidence_threshold,
                                 detect_items=detect_items,
                                 item_confidence_threshold=item_confidence_threshold)
    except RuntimeError as e:
        print(f"Error: {e}")
        exit(1)
    
    print("Starting occupancy monitoring...")
    print(f"Mode: {'Headless (console only)' if args.headless else 'Display window'}")
    print(f"Target FPS: {fps_target}")
    if not args.headless:
        print("Press 'q' to quit")
    else:
        print("Press Ctrl+C to quit")
    print("-" * 60)
    
    # Calculate frame delay for target FPS
    frame_delay = 1.0 / fps_target if fps_target > 0 else 0
    
    try:
        while True:
            start_time = time.time()
            
            # Capture frame
            frame = camera.get_frame()
            if frame is None:
                print("Error: Failed to capture frame")
                break
            
            # Detect persons and items
            person_detections, item_detections = detector.detect(frame)
            
            # Check occupancy
            statuses = check_occupancy(person_detections, item_detections, seats)
            
            # Print status to console
            print(format_status_line(seats, statuses))
            
            # Display mode
            if not args.headless:
                # Draw overlay
                frame_with_overlay = draw_overlay(frame, seats, statuses, person_detections, item_detections)
                
                # Show frame
                cv2.imshow("Seat Occupancy Monitor", frame_with_overlay)
                
                # Check for quit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nQuitting...")
                    break
            
            # Control frame rate
            elapsed = time.time() - start_time
            if elapsed < frame_delay:
                time.sleep(frame_delay - elapsed)
    
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    
    finally:
        # Cleanup
        camera.release()
        if not args.headless:
            cv2.destroyAllWindows()
        print("Cleanup complete. Goodbye!")


if __name__ == "__main__":
    main()
