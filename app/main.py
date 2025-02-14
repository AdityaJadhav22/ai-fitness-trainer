import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration

# Page config
st.set_page_config(
    page_title="AI Fitness Trainer",
    page_icon="💪",
    layout="wide"
)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1
        )

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Convert the BGR image to RGB
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process the image and detect poses
        results = self.pose.process(image)
        
        # Draw the pose annotations on the image
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                img,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
            )
        
        return img

def main():
    st.title("AI Fitness Trainer 💪")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # WebRTC Configuration
        rtc_configuration = RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )
        
        # Create WebRTC streamer
        ctx = webrtc_streamer(
            key="fitness-pose-detection",
            mode=webrtc_streamer.WebRtcMode.SENDRECV,
            rtc_configuration=rtc_configuration,
            video_processor_factory=VideoProcessor,
            media_stream_constraints={
                "video": {"width": {"ideal": 640}, "height": {"ideal": 480}},
                "audio": False
            },
            async_processing=True,
        )
        
        if ctx.state.playing:
            st.success("✅ Camera is running! Move around to test pose detection.")
    
    with col2:
        st.markdown("""
        ### Instructions
        1. Click 'START' to begin
        2. Allow camera access
        3. Position yourself in frame
        4. Move around to test detection
        
        ### Tips
        - Ensure good lighting
        - Keep your full body visible
        - Wear contrasting clothes
        - Clear background helps
        """)
        
        # Status indicator
        if ctx.state.playing:
            st.success("Camera Status: Active")
        else:
            st.warning("Camera Status: Click START")

if __name__ == "__main__":
    main()