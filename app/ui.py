import streamlit as st

def setup_sidebar():
    st.sidebar.title("Settings")
    detection_confidence = st.sidebar.slider(
        "Detection Confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1
    )
    return detection_confidence

def setup_main_area():
    st.title("Pose Estimation & Squat Counter")
    st.write("Upload a video or use your webcam to detect squats!") 