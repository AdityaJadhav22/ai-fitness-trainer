import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# Page config
st.set_page_config(
    page_title="AI Fitness Trainer",
    page_icon="💪",
    layout="wide"
)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=0  # Use simplest model for better performance
)

def video_frame_callback(frame):
    try:
        img = frame.to_ndarray(format="bgr24")
        return frame
    except Exception as e:
        st.error(f"Error processing frame: {str(e)}")
        return frame

def main():
    st.title("AI Fitness Trainer 💪")
    
    # Configure RTC with multiple STUN/TURN servers
    rtc_configuration = RTCConfiguration(
        {"iceServers": [
            {"urls": "stun:stun.l.google.com:19302"},
            {"urls": "stun:stun1.l.google.com:19302"},
            {"urls": "stun:stun2.l.google.com:19302"},
            {"urls": "stun:stun3.l.google.com:19302"},
            {"urls": "stun:stun4.l.google.com:19302"},
            {
                "urls": "turn:openrelay.metered.ca:80",
                "username": "openrelayproject",
                "credential": "openrelayproject",
            },
            {
                "urls": "turn:openrelay.metered.ca:443",
                "username": "openrelayproject",
                "credential": "openrelayproject",
            },
        ]}
    )
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        try:
            webrtc_ctx = webrtc_streamer(
                key="fitness-camera",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=rtc_configuration,
                video_frame_callback=video_frame_callback,
                media_stream_constraints={
                    "video": {
                        "width": {"ideal": 640},
                        "height": {"ideal": 480},
                        "frameRate": {"ideal": 15, "max": 30}
                    },
                    "audio": False
                },
                async_processing=True,
                video_html_attrs={
                    "style": {"width": "100%", "margin": "0 auto", "border": "2px solid red"},
                    "controls": False,
                    "autoPlay": True,
                },
            )
            
            if not webrtc_ctx.state.playing:
                st.warning("⚠️ Camera stream not started. Click 'START' to begin.")
            
        except Exception as e:
            st.error(f"Error initializing camera: {str(e)}")
            st.info("Please check your camera permissions and try again.")
    
    with col2:
        st.markdown("""
        ### Instructions:
        1. Click 'START' to begin
        2. Allow camera access
        3. Wait a few seconds for connection
        4. Click 'STOP' when done
        
        ### Troubleshooting:
        - Ensure camera permissions
        - Try refreshing the page
        - Use Chrome browser
        - Check internet connection
        - Wait 10-15 seconds for connection
        """)

if __name__ == "__main__":
    main()