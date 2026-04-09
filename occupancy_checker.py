"""
Occupancy checker module.
Checks seat occupancy based on person and item detections using center-point method.
Implements tri-state status: EMPTY, OCCUPIED (person), RESERVED (items only).
"""

import json
import cv2

# Color scheme for seat status visualization (BGR format)
COLOR_EMPTY = (0, 255, 0)      # Green
COLOR_OCCUPIED = (0, 0, 255)   # Red
COLOR_RESERVED = (255, 165, 0) # Blue


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


def check_occupancy(person_detections, item_detections, seats):
    """
    Check seat status based on person and item detections.
    Uses center-point method: if center is in seat, it occupies/reserves the seat.
    
    Priority: Person (OCCUPIED) > Items (RESERVED) > Empty
    
    Args:
        person_detections: List of person detection dicts (from detector.py)
        item_detections: List of item detection dicts (from detector.py)
        seats: List of seat dicts (from config.json)
    
    Returns:
        dict: Mapping of seat_id to status ("EMPTY", "OCCUPIED", or "RESERVED")
    """
    # Initialize all seats as empty
    statuses = {seat["id"]: "EMPTY" for seat in seats}
    
    # Check each person (highest priority)
    for person in person_detections:
        # Calculate center point of person bounding box
        center_x = (person["x1"] + person["x2"]) / 2
        center_y = (person["y1"] + person["y2"]) / 2
        
        # Check if center point is in any seat
        for seat in seats:
            if is_point_in_seat(center_x, center_y, seat):
                statuses[seat["id"]] = "OCCUPIED"
                break  # One person can only occupy one seat
    
    # Check each item (second priority, only if seat not already occupied)
    for item in item_detections:
        # Calculate center point of item bounding box
        center_x = (item["x1"] + item["x2"]) / 2
        center_y = (item["y1"] + item["y2"]) / 2
        
        # Check if center point is in any seat
        for seat in seats:
            seat_id = seat["id"]
            # Only mark as reserved if not already occupied by a person
            if (is_point_in_seat(center_x, center_y, seat) and 
                statuses[seat_id] != "OCCUPIED"):
                statuses[seat_id] = "RESERVED"
                break  # One item reserves one seat
    
    return statuses


def draw_overlay(frame, seats, statuses, person_detections, item_detections):
    """
    Draw bounding boxes and labels on frame.
    
    Args:
        frame: Input frame (will be modified in-place)
        seats: List of seat dictionaries
        statuses: Dict mapping seat_id to status ("EMPTY", "OCCUPIED", or "RESERVED")
        person_detections: List of person detection dicts
        item_detections: List of item detection dicts
    
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
    
    # Draw item detections (blue boxes)
    for item in item_detections:
        x1, y1, x2, y2 = item["x1"], item["y1"], item["x2"], item["y2"]
        conf = item["confidence"]
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_RESERVED, 2)
        cv2.putText(frame, f"Item {conf:.2f}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_RESERVED, 2)
    
    # Draw seat bounding boxes with tri-state colors
    for seat in seats:
        x1, y1, x2, y2 = seat["x1"], seat["y1"], seat["x2"], seat["y2"]
        seat_id = seat["id"]
        label = seat["label"]
        status = statuses.get(seat_id, "EMPTY")
        
        # Choose color based on status
        if status == "OCCUPIED":
            color = COLOR_OCCUPIED  # Red
        elif status == "RESERVED":
            color = COLOR_RESERVED  # Blue
        else:
            color = COLOR_EMPTY     # Green
        
        # Draw rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
        
        # Draw label
        text = f"{label}: {status}"
        cv2.putText(frame, text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    return frame
