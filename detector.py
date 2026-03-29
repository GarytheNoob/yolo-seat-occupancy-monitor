"""
Person detector module using YOLOv8.
Detects persons in video frames using a pre-trained YOLO model.
"""

from ultralytics import YOLO


class PersonDetector:
    """Detects persons in images using YOLOv8."""
    
    def __init__(self, model_path="yolov8n.pt", confidence_threshold=0.5):
        """
        Initialize the person detector.
        
        Args:
            model_path: Path to YOLO model weights (will auto-download if not found)
            confidence_threshold: Minimum confidence for detections (0.0 to 1.0)
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
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
        Detect persons in a frame.
        
        Args:
            frame: Input image as numpy array (BGR format from OpenCV)
        
        Returns:
            list: List of detected persons, each as a dict with keys:
                  - x1, y1, x2, y2: Bounding box coordinates
                  - confidence: Detection confidence score
        """
        if frame is None:
            return []
        
        # Run inference
        results = self.model(frame, verbose=False)
        
        persons = []
        
        # Process results
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Filter for person class (class 0 in COCO dataset)
                if int(box.cls[0]) == 0:
                    confidence = float(box.conf[0])
                    
                    # Filter by confidence threshold
                    if confidence >= self.confidence_threshold:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        persons.append({
                            "x1": int(x1),
                            "y1": int(y1),
                            "x2": int(x2),
                            "y2": int(y2),
                            "confidence": confidence
                        })
        
        return persons
