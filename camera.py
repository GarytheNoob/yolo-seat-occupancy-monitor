"""
Camera module for webcam capture.
Provides a simple wrapper around OpenCV VideoCapture.
"""

import cv2


class Camera:
    """Handles webcam capture and frame retrieval."""

    def __init__(self, source=0, width=640, height=480, autofocus=True, focus=0):
        """
        Initialize camera.

        Args:
            source: Camera device index (default: 0)
            width: Frame width in pixels
            height: Frame height in pixels
            autofocus: Enable camera autofocus when supported
            focus: Manual focus value (applied when autofocus is disabled)
        """
        self.source = source
        self.width = width
        self.height = height
        self.autofocus = bool(autofocus)
        self.focus = focus
        self.cap = None
        self.autofocus_supported = False
        self.focus_supported = False

        self._initialize()
    
    def _initialize(self):
        """Initialize the video capture device."""
        self.cap = cv2.VideoCapture(self.source)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera at source {self.source}")
        
        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        self.autofocus_supported = self._probe_property(cv2.CAP_PROP_AUTOFOCUS)
        self.focus_supported = self._probe_property(cv2.CAP_PROP_FOCUS)

        if self.autofocus is not None:
            self.set_autofocus(self.autofocus)

        if not self.autofocus and self.focus is not None:
            self.set_focus(self.focus)

    def _probe_property(self, prop_id):
        value = self.cap.get(prop_id)
        return value != -1
    
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

    def get_autofocus(self):
        if not self.is_opened() or not self.autofocus_supported:
            return None
        value = self.cap.get(cv2.CAP_PROP_AUTOFOCUS)
        if value == -1:
            return None
        return bool(round(value))

    def get_focus(self):
        if not self.is_opened() or not self.focus_supported:
            return None
        value = self.cap.get(cv2.CAP_PROP_FOCUS)
        if value == -1:
            return None
        return value

    def set_autofocus(self, enabled):
        if not self.is_opened():
            return False
        self.autofocus = bool(enabled)
        result = self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1 if self.autofocus else 0)
        if result:
            self.autofocus_supported = True
        return bool(result)

    def set_focus(self, value):
        if value is None or not self.is_opened():
            return False
        self.focus = value
        result = self.cap.set(cv2.CAP_PROP_FOCUS, float(value))
        if result:
            self.focus_supported = True
        return bool(result)
    
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
