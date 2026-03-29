#!/usr/bin/env python3
"""
Setup helper to create seat configuration.
Allows user to click on webcam frame to define seat bounding boxes.
"""

import cv2
import json


class SeatSetupTool:
    """Interactive tool for defining seat bounding boxes."""
    
    def __init__(self):
        self.frame = None
        self.seats = []
        self.current_seat = []
        self.temp_point = None
        
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for seat definition."""
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.current_seat) == 0:
                # First corner
                self.current_seat = [(x, y)]
                self.temp_point = (x, y)
                print(f"First corner at ({x}, {y}). Click second corner...")
            elif len(self.current_seat) == 1:
                # Second corner
                x1, y1 = self.current_seat[0]
                x2, y2 = x, y
                
                # Ensure x1 < x2 and y1 < y2
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)
                
                seat_id = len(self.seats) + 1
                seat = {
                    "id": seat_id,
                    "label": f"Seat {seat_id}",
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                }
                
                self.seats.append(seat)
                self.current_seat = []
                self.temp_point = None
                
                print(f"Seat {seat_id} defined: ({x1}, {y1}) to ({x2}, {y2})")
                print(f"Total seats: {len(self.seats)}")
                print("Click two corners for next seat, or press 's' to save, 'r' to reset")
    
    def draw_seats(self, frame):
        """Draw defined seats on frame."""
        display = frame.copy()
        
        # Draw completed seats (green)
        for seat in self.seats:
            x1, y1, x2, y2 = seat["x1"], seat["y1"], seat["x2"], seat["y2"]
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(display, seat["label"], (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Draw current point being defined (red circle)
        if self.temp_point:
            cv2.circle(display, self.temp_point, 5, (0, 0, 255), -1)
        
        # Draw instruction text
        instructions = [
            "Click two corners to define each seat",
            "Press 's' to save configuration",
            "Press 'r' to reset all seats",
            "Press 'q' to quit without saving"
        ]
        
        y_offset = 30
        for instruction in instructions:
            cv2.putText(display, instruction, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 25
        
        return display
    
    def save_config(self, output_path="config.json"):
        """Save seats configuration to JSON file."""
        if len(self.seats) == 0:
            print("No seats defined. Nothing to save.")
            return False
        
        config = {
            "camera": {
                "source": 0,
                "width": 640,
                "height": 480,
                "fps_target": 2
            },
            "detection": {
                "confidence_threshold": 0.5,
                "model": "yolov8n.pt"
            },
            "seats": self.seats
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"\nConfiguration saved to {output_path}")
            print(f"Defined {len(self.seats)} seat(s)")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def run(self):
        """Run the interactive setup tool."""
        # Initialize camera
        print("Initializing camera...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Capture a single frame
        print("Capturing frame...")
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            print("Error: Failed to capture frame")
            return
        
        self.frame = frame
        
        # Create window and set mouse callback
        window_name = "Seat Setup Tool"
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        
        print("\n" + "=" * 60)
        print("SEAT SETUP TOOL")
        print("=" * 60)
        print("Instructions:")
        print("1. Click two corners (top-left, bottom-right) for each seat")
        print("2. Press 's' to save configuration")
        print("3. Press 'r' to reset and start over")
        print("4. Press 'q' to quit without saving")
        print("=" * 60 + "\n")
        
        while True:
            # Draw current state
            display = self.draw_seats(self.frame)
            cv2.imshow(window_name, display)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\nQuitting without saving...")
                break
            elif key == ord('s'):
                if self.save_config():
                    print("You can now run: python main.py")
                    break
                else:
                    print("Please define at least one seat before saving.")
            elif key == ord('r'):
                self.seats = []
                self.current_seat = []
                self.temp_point = None
                print("\nReset all seats. Start over.")
        
        cv2.destroyAllWindows()


def main():
    """Main entry point."""
    tool = SeatSetupTool()
    tool.run()


if __name__ == "__main__":
    main()
