"""
Person detector module using YOLOv8.
Detects persons and items (bags, laptops, books) in video frames using a pre-trained YOLO model.
"""

from ultralytics import YOLO

# COCO class IDs for item detection
PERSON_CLASS = 0
ITEM_CLASSES = {
    25: "Backpack",
    26: "Handbag",
    28: "Suitcase",
    61: "Laptop",
    73: "Book"
}
ALL_TARGET_CLASSES = [PERSON_CLASS] + list(ITEM_CLASSES.keys())


class PersonDetector:
    """Detects persons and items (bags, laptops, books) in images using YOLOv8."""
    
    def __init__(self, model_path="yolov8n.pt", confidence_threshold=0.5, detect_items=True, item_confidence_threshold=0.4):
        """
        Initialize the person and item detector.
        
        Args:
            model_path: Path to YOLO model weights (will auto-download if not found)
            confidence_threshold: Minimum confidence for person detections (0.0 to 1.0)
            detect_items: Whether to detect items (bags, laptops, books)
            item_confidence_threshold: Minimum confidence for item detections (0.0 to 1.0)
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.detect_items = detect_items
        self.item_confidence_threshold = item_confidence_threshold
        self.model = None
        
        self._load_model()
    
    def _load_model(self):
        """Load the YOLO model."""
        try:
            self.model = YOLO(self.model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model: {e}")
    
    def detect(self, frame):
        """
        Detect persons and items in a frame.
        
        Args:
            frame: Input image as numpy array (BGR format from OpenCV)
        
        Returns:
            tuple: (persons, items) where each is a list of dicts with keys:
                   - x1, y1, x2, y2: Bounding box coordinates
                   - confidence: Detection confidence score
                   - type: "person" or "item"
                   - class_id: COCO class ID
        """
        if frame is None:
            return [], []
        
        # Run inference
        results = self.model(frame, verbose=False)
        
        persons = []
        items = []
        
        # Process results
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                detection_dict = {
                    "x1": int(x1),
                    "y1": int(y1),
                    "x2": int(x2),
                    "y2": int(y2),
                    "confidence": confidence,
                    "type": "person" if class_id == PERSON_CLASS else "item",
                    "class_id": class_id
                }
                
                # Filter for person class
                if class_id == PERSON_CLASS and confidence >= self.confidence_threshold:
                    persons.append(detection_dict)
                # Filter for item classes if enabled
                elif self.detect_items and class_id in ITEM_CLASSES and confidence >= self.item_confidence_threshold:
                    items.append(detection_dict)
        
        return persons, items
