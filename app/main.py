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

def main():
    st.title("AI Fitness Trainer 💪")
    
    # Add a simple text explanation
    st.write("Welcome to the AI Fitness Trainer! This app will help you track your exercises.")
    
    # Basic WebRTC implementation
    webrtc_ctx = webrtc_streamer(
        key="basic-example",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    # Add instructions
    st.markdown("""
    ### Instructions:
    1. Click 'START' to begin
    2. Allow camera access when prompted
    3. Click 'STOP' when done
    """)

if __name__ == "__main__":
    main()