import cv2
import numpy as np

class VideoProcessor:
    def __init__(self, pose_model, squat_detector, bicep_model):
        self.pose_model = pose_model
        self.squat_detector = squat_detector
        self.bicep_model = bicep_model
        
    def process_frame(self, frame):
        # Detect pose
        frame, landmarks = self.pose_model.detect_pose(frame)
        
        # Detect squat
        is_squat, squat_count = self.squat_detector.detect_squat(landmarks)
        
        # Use bicep model
        if self.bicep_model is not None:
            bicep_result = self.bicep_model.predict(frame)
            if bicep_result is not None:
                # Add bicep detection results to frame
                cv2.putText(frame, f'Bicep: {bicep_result}', (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add squat counter to frame
        cv2.putText(frame, f'Squats: {squat_count}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame