import cv2
import numpy as np

def resize_frame(frame, width=None, height=None):
    """Resize frame maintaining aspect ratio"""
    if width is None and height is None:
        return frame
    
    h, w = frame.shape[:2]
    if width is None:
        aspect_ratio = height / h
        dimension = (int(w * aspect_ratio), height)
    else:
        aspect_ratio = width / w
        dimension = (width, int(h * aspect_ratio))
    
    return cv2.resize(frame, dimension, interpolation=cv2.INTER_AREA)

def draw_text(frame, text, position, scale=1, color=(0, 255, 0), thickness=2):
    """Draw text on frame with background"""
    cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX,
                scale, color, thickness) 