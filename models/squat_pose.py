import numpy as np

class SquatDetector:
    def __init__(self):
        self.squat_position = False
        self.squat_counter = 0
        self.prev_position = 'stand'
        
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
                 np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle

    def detect_squat(self, landmarks):
        if landmarks is None:
            return False, self.squat_counter
        
        # Get hip, knee and ankle points
        hip = [landmarks.landmark[23].x, landmarks.landmark[23].y]
        knee = [landmarks.landmark[25].x, landmarks.landmark[25].y]
        ankle = [landmarks.landmark[27].x, landmarks.landmark[27].y]
        
        # Calculate angle
        angle = self.calculate_angle(hip, knee, ankle)
        
        # Detect squat position
        if angle < 120 and self.prev_position == 'stand':
            self.prev_position = 'squat'
        elif angle > 160 and self.prev_position == 'squat':
            self.prev_position = 'stand'
            self.squat_counter += 1
            
        return self.prev_position == 'squat', self.squat_counter 