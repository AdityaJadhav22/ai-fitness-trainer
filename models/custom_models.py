import cv2
import mediapipe as mp
import numpy as np
import time

class BicepModel:
    def __init__(self):
        self.counter = 0
        self.stage = None
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.start_time = time.time()
        self.MET = 3.5  # Metabolic Equivalent for bicep curls
        self.left_counter = 0
        self.right_counter = 0
        self.left_stage = None
        self.right_stage = None
        
    def calculate_calories(self, weight_kg, elapsed_time_hrs):
        return self.MET * weight_kg * elapsed_time_hrs
        
    def reset_counter(self):
        self.counter = 0
        self.stage = None
        self.left_counter = 0
        self.right_counter = 0
        self.left_stage = None
        self.right_stage = None
        self.start_time = time.time()
        
    def process_frame(self, frame, show_angles=True, show_counter=True, weight_kg=70, selected_hand='Right'):
        if frame is None:
            return None
            
        try:
            # Convert BGR to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Make detection
            results = self.pose.process(image)
            
            # Convert back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            if results.pose_landmarks:
                # Draw landmarks
                self.mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                )
                
                try:
                    landmarks = results.pose_landmarks.landmark
                    
                    # Process right arm (appears on left side of flipped image)
                    right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                   landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                 landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    right_wrist = [landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                 landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    
                    # Process left arm (appears on right side of flipped image)
                    left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                  landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    
                    # Calculate angles
                    right_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
                    left_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
                    
                    # Process based on selected hand
                    if selected_hand == 'Right':
                        # Right hand only
                        if right_angle > 160:
                            self.right_stage = "down"
                        if right_angle < 30 and self.right_stage == 'down':
                            self.right_stage = "up"
                            self.right_counter += 1
                        self.counter = self.right_counter
                        self.stage = self.right_stage
                        
                        if show_angles:
                            cv2.putText(image, str(int(right_angle)), 
                                      tuple(np.multiply(right_elbow, [640, 480]).astype(int)), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    
                    elif selected_hand == 'Left':
                        # Left hand only
                        if left_angle > 160:
                            self.left_stage = "down"
                        if left_angle < 30 and self.left_stage == 'down':
                            self.left_stage = "up"
                            self.left_counter += 1
                        self.counter = self.left_counter
                        self.stage = self.left_stage
                        
                        if show_angles:
                            cv2.putText(image, str(int(left_angle)), 
                                      tuple(np.multiply(left_elbow, [640, 480]).astype(int)), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    
                    else:  # Both hands
                        # Track both arms
                        if right_angle > 160 and left_angle > 160:
                            self.right_stage = "down"
                            self.left_stage = "down"
                        if right_angle < 30 and left_angle < 30 and self.right_stage == 'down' and self.left_stage == 'down':
                            self.right_stage = "up"
                            self.left_stage = "up"
                            self.right_counter += 1
                            self.left_counter += 1
                            self.counter = min(self.left_counter, self.right_counter)
                        
                        if show_angles:
                            # Show angles for both arms
                            cv2.putText(image, str(int(right_angle)), 
                                      tuple(np.multiply(right_elbow, [640, 480]).astype(int)), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                            cv2.putText(image, str(int(left_angle)), 
                                      tuple(np.multiply(left_elbow, [640, 480]).astype(int)), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                        
                        # Set stage for display
                        if self.left_stage == self.right_stage:
                            self.stage = self.left_stage
                        else:
                            self.stage = "async"
                    
                    if show_counter:
                        # Draw counter box
                        cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
                        
                        # Rep data
                        cv2.putText(image, 'REPS', (15,12), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
                        cv2.putText(image, str(self.counter), 
                                  (10,60), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
                        
                        # Stage data
                        cv2.putText(image, 'STAGE', (65,12), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
                        cv2.putText(image, self.stage or "", 
                                  (60,60), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
                    
                except Exception as e:
                    print(f"Error processing landmarks: {e}")
            
            return image
            
        except Exception as e:
            print(f"Error in process_frame: {e}")
            return frame
            
    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle

class CustomModel1:
    def __init__(self, model_path):
        # Load your first trained model
        self.model = tf.keras.models.load_model(model_path)  # or your specific loading method
        
    def predict(self, input_data):
        # Preprocess input data if needed
        predictions = self.model.predict(input_data)
        return predictions

class CustomModel2:
    def __init__(self, model_path):
        # Load your second trained model
        self.model = tf.keras.models.load_model(model_path)  # or your specific loading method
        
    def predict(self, input_data):
        # Preprocess input data if needed
        predictions = self.model.predict(input_data)
        return predictions 

class SquatDetector:
    def __init__(self):
        self.counter = 0
        self.stage = None
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.start_time = time.time()
        self.MET = 5.0  # Higher MET value for squats
        
    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def reset_counter(self):
        self.counter = 0
        self.stage = None
        self.start_time = time.time()
        
    def process_frame(self, frame, show_angles=True, show_counter=True):
        if frame is None:
            return None
            
        try:
            # Convert BGR to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Make detection
            results = self.pose.process(image)
            
            # Convert back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            if results.pose_landmarks:
                # Draw landmarks
                self.mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                )
                
                try:
                    # Get coordinates for right leg
                    right_hip = [results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                               results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    right_knee = [results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                    right_ankle = [results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                 results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                    
                    # Get coordinates for left leg
                    left_hip = [results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                              results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    left_knee = [results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                               results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                    left_ankle = [results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                    
                    # Calculate angles
                    right_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
                    left_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
                    
                    # Average angle of both legs
                    avg_angle = (right_angle + left_angle) / 2
                    
                    # Counter logic
                    if avg_angle > 160:
                        self.stage = "up"
                    if avg_angle < 90 and self.stage == 'up':
                        self.stage = "down"
                        self.counter += 1
                    
                    if show_angles:
                        # Display angles
                        cv2.putText(image, str(int(right_angle)), 
                                  tuple(np.multiply(right_knee, [640, 480]).astype(int)), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(image, str(int(left_angle)), 
                                  tuple(np.multiply(left_knee, [640, 480]).astype(int)), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    
                    if show_counter:
                        # Draw counter box
                        cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
                        
                        # Rep data
                        cv2.putText(image, 'REPS', (15,12), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
                        cv2.putText(image, str(self.counter), 
                                  (10,60), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
                        
                        # Stage data
                        cv2.putText(image, 'STAGE', (65,12), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
                        cv2.putText(image, self.stage or "", 
                                  (60,60), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
                    
                except Exception as e:
                    print(f"Error processing landmarks: {e}")
            
            return image
            
        except Exception as e:
            print(f"Error in process_frame: {e}")
            return frame 