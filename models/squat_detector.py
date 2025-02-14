import numpy as np
import cv2
import mediapipe as mp

class SquatDetector:
    def __init__(self):
        self.counter = 0
        self.stage = None
        self.mp_pose = mp.solutions.pose
        
    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle
        
    def detect_squat(self, landmarks):
        if landmarks is None:
            return False, 0
            
        try:
            # Get coordinates for squat detection
            hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            
            # Calculate knee angle
            angle = self.calculate_angle(hip, knee, ankle)
            
            # Squat logic
            if angle > 160:
                self.stage = "up"
            elif angle < 100 and self.stage == "up":
                self.stage = "down"
                self.counter += 1
                
            return True, angle
            
        except Exception as e:
            print(f"Error in squat detection: {e}")
            return False, 0
            
    def reset_counter(self):
        self.counter = 0
        self.stage = None 