import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av

# Page config
st.set_page_config(
    page_title="AI Fitness Trainer",
    page_icon="💪",
    layout="wide"
)

def video_frame_callback(frame):
    try:
        img = frame.to_ndarray(format="bgr24")
        
        # Initialize pose detection only when processing frames
        with mp.solutions.pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=0
        ) as pose:
            # Convert to RGB
            rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Process the frame
            results = pose.process(rgb_frame)
            
            # Draw landmarks if detected
            if results.pose_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    rgb_frame,
                    results.pose_landmarks,
                    mp.solutions.pose.POSE_CONNECTIONS
                )
            
            # Convert back to BGR
            output_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
            return av.VideoFrame.from_ndarray(output_frame, format="bgr24")
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
            {
                "urls": "turn:openrelay.metered.ca:80",
                "username": "openrelayproject",
                "credential": "openrelayproject",
            }
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
                        "frameRate": {"max": 15}
                    },
                    "audio": False
                },
                async_processing=True,
            )
            
            if webrtc_ctx.state.playing:
                st.success("✅ Camera connected successfully!")
            else:
                st.warning("⚠️ Click 'START' to begin camera stream")
            
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