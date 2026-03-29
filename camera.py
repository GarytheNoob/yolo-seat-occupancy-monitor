"""
Camera module for webcam capture.
Provides a simple wrapper around OpenCV VideoCapture.
"""

import cv2


class Camera:
    """Handles webcam capture and frame retrieval."""
    
    def __init__(self, source=0, width=640, height=480):
        """
        Initialize camera.
        
        Args:
            source: Camera device index (default: 0)
            width: Frame width in pixels
            height: Frame height in pixels
        """
        self.source = source
        self.width = width
        self.height = height
        self.cap = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the video capture device."""
        self.cap = cv2.VideoCapture(self.source)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera at source {self.source}")
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
    
    def get_frame(self):
        """
        Capture a single frame from the camera.
        
        Returns:
            numpy.ndarray: The captured frame, or None if capture failed
        """
        if not self.is_opened():
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            return None
        
        return frame
    
    def is_opened(self):
        """
        Check if camera is currently opened.
        
        Returns:
            bool: True if camera is open, False otherwise
        """
        return self.cap is not None and self.cap.isOpened()
    
    def release(self):
        """Release the camera resource."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
