import mediapipe as mp
import numpy as np

class BicepModel:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.counter = 0
        self.stage = None
        
    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        if angle > 180.0:
            angle = 360-angle
        return angle
    
    def process_frame(self, frame, side="right"):
        # Implementation details here
        pass

class SquatDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.counter = 0
        self.stage = None
        
    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        if angle > 180.0:
            angle = 360-angle
        return angle
    
    def process_frame(self, frame):
        # Implementation details here
        pass 