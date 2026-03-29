"""
Occupancy checker module.
Checks seat occupancy based on person detections using center-point method.
"""

import json
import cv2


def load_seats(config_path):
    """
    Load seat configuration from JSON file.
    
    Args:
        config_path: Path to config.json file
    
    Returns:
        list: List of seat dictionaries
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get('seats', [])
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            "Please run 'python setup_helper.py' to create seat configuration."
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")


def is_point_in_seat(px, py, seat):
    """
    Check if a point is inside a seat bounding box.
    
    Args:
        px: X coordinate of point
        py: Y coordinate of point
        seat: Seat dictionary with x1, y1, x2, y2
    
    Returns:
        bool: True if point is inside seat, False otherwise
    """
    return (seat["x1"] <= px <= seat["x2"] and 
            seat["y1"] <= py <= seat["y2"])


def check_occupancy(person_detections, seats):
    """
    Check which seats are occupied based on person detections.
    Uses center-point method: if person's center is in seat, seat is occupied.
    
    Args:
        person_detections: List of person detection dicts (from detector.py)
        seats: List of seat dicts (from config.json)
    
    Returns:
        dict: Mapping of seat_id to status ("EMPTY" or "OCCUPIED")
    """
    # Initialize all seats as empty
    statuses = {seat["id"]: "EMPTY" for seat in seats}
    
    # Check each person
    for person in person_detections:
        # Calculate center point of person bounding box
        center_x = (person["x1"] + person["x2"]) / 2
        center_y = (person["y1"] + person["y2"]) / 2
        
        # Check if center point is in any seat
        for seat in seats:
            if is_point_in_seat(center_x, center_y, seat):
                statuses[seat["id"]] = "OCCUPIED"
                break  # One person can only occupy one seat
    
    return statuses


def draw_overlay(frame, seats, statuses, person_detections):
    """
    Draw bounding boxes and labels on frame.
    
    Args:
        frame: Input frame (will be modified in-place)
        seats: List of seat dictionaries
        statuses: Dict mapping seat_id to status
        person_detections: List of person detection dicts
    
    Returns:
        numpy.ndarray: Frame with overlays drawn
    """
    # Draw person detections (yellow boxes)
    for person in person_detections:
        x1, y1, x2, y2 = person["x1"], person["y1"], person["x2"], person["y2"]
        conf = person["confidence"]
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(frame, f"Person {conf:.2f}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    
    # Draw seat bounding boxes (green = empty, red = occupied)
    for seat in seats:
        x1, y1, x2, y2 = seat["x1"], seat["y1"], seat["x2"], seat["y2"]
        seat_id = seat["id"]
        label = seat["label"]
        status = statuses.get(seat_id, "EMPTY")
        
        # Choose color based on status
        color = (0, 0, 255) if status == "OCCUPIED" else (0, 255, 0)
        
        # Draw rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
        
        # Draw label
        text = f"{label}: {status}"
        cv2.putText(frame, text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    return frame
