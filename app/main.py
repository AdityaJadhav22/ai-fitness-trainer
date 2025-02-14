import streamlit as st
from pathlib import Path
import time
from datetime import datetime
import os
import base64
import cv2
import mediapipe as mp
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av

# Must be the first Streamlit command
st.set_page_config(
    page_title="AI Fitness Trainer",
    page_icon="💪",
    layout="wide"
)

import sys

# Add the project root directory to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.append(str(project_root))

try:
    from models.custom_models import BicepModel
    from models.squat_detector import SquatDetector
except ImportError as e:
    st.error(f"Import error: {e}")
    raise

# Get the absolute path to the assets directory
ASSETS_DIR = Path(__file__).parent / "assets"
STYLES_DIR = ASSETS_DIR / "styles"
IMAGES_DIR = ASSETS_DIR / "images"

# Create directories if they don't exist
ASSETS_DIR.mkdir(exist_ok=True)
STYLES_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)

# Custom CSS for gym theme
def local_css():
    st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --main-color: #FF4B2B;
            --secondary-color: #252529;
            --text-color: #ffffff;
            --accent-color: #FF416C;
        }
        
        /* Overall page styling */
        .stApp {
            background: linear-gradient(135deg, #252529 0%, #1C1C1F 100%);
            color: var(--text-color);
        }
        
        /* Header styling */
        .main-header {
            background: linear-gradient(90deg, var(--main-color), var(--accent-color));
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .main-header h1 {
            color: white;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #1C1C1F 0%, #252529 100%);
            padding: 2rem 1rem;
        }
        
        /* Sidebar title */
        .sidebar-title {
            background: linear-gradient(90deg, var(--main-color), var(--accent-color));
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .sidebar-title h2 {
            color: white;
            font-size: 1.5rem;
            font-weight: 600;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Settings containers */
        .settings-container {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255, 75, 43, 0.2);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }
        
        .settings-container:hover {
            transform: translateY(-2px);
            border: 1px solid rgba(255, 75, 43, 0.4);
        }
        
        /* Settings headers */
        .settings-header {
            color: var(--main-color);
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid rgba(255, 75, 43, 0.3);
        }
        
        /* Radio buttons */
        .stRadio > div {
            background: rgba(255, 255, 255, 0.05);
            padding: 0.5rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
        }
        
        .stRadio > div:hover {
            background: rgba(255, 75, 43, 0.1);
        }
        
        .stRadio > div > label {
            color: white !important;
            font-weight: 500;
        }
        
        /* Number input */
        .stNumberInput > div > div > input {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 75, 43, 0.3);
            color: white;
            border-radius: 5px;
        }
        
        /* Checkbox styling */
        .stCheckbox > div > div > label {
            color: white !important;
        }
        
        .stCheckbox > div > div > div > div {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 75, 43, 0.3);
        }
        
        /* Icons */
        .sidebar-icon {
            font-size: 1.5rem;
            margin-right: 0.5rem;
            color: var(--main-color);
        }
        
        /* Settings groups */
        .settings-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        /* Tooltip */
        .tooltip {
            position: relative;
            display: inline-block;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            text-align: center;
            padding: 5px 10px;
            border-radius: 6px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        /* Button styling */
        .stButton>button {
            background: linear-gradient(45deg, var(--main-color), var(--accent-color));
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            font-weight: 600;
            transition: transform 0.2s;
            width: 100%;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255,75,43,0.4);
        }
        
        /* Metric containers */
        .metric-container {
            background: rgba(37,37,41,0.9);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            border: 1px solid rgba(255,75,43,0.3);
        }
        
        /* Summary styling */
        .summary-header {
            background: linear-gradient(45deg, var(--main-color), var(--accent-color));
            color: white;
            padding: 1rem;
            border-radius: 10px 10px 0 0;
            margin-top: 2rem;
        }
        
        .summary-content {
            background: rgba(37,37,41,0.9);
            padding: 1.5rem;
            border-radius: 0 0 10px 10px;
            border: 1px solid rgba(255,75,43,0.3);
        }
        
        /* Metric value styling */
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--main-color);
        }
        
        /* Exercise type badge */
        .exercise-badge {
            background: var(--main-color);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            display: inline-block;
            margin: 1rem 0;
        }
        
        /* Video container */
        .video-container {
            border: 3px solid var(--main-color);
            border-radius: 10px;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        /* Separator */
        .separator {
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--main-color), transparent);
            margin: 2rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

# Create a pose detection instance
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=1  # Use a simpler model for better performance
)

def video_frame_callback(frame):
    try:
        img = frame.to_ndarray(format="bgr24")
        
        # Flip the frame horizontally for a later selfie-view display
        img = cv2.flip(img, 1)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = pose.process(rgb_frame)
        
        # Draw pose landmarks
        if results.pose_landmarks:
            mp_draw.draw_landmarks(
                rgb_frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_draw.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                mp_draw.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
            )
        
        # Convert back to BGR for display
        return av.VideoFrame.from_ndarray(
            cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR),
            format="bgr24"
        )
    except Exception as e:
        st.error(f"Error processing video frame: {str(e)}")
        return None

def format_time(seconds):
    """Convert seconds to MM:SS format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def calculate_calories_from_reps(reps, weight_kg, exercise_type):
    """Calculate calories burned based on number of reps and exercise type"""
    if exercise_type == 'Bicep Curls':
        # Calories per rep for bicep curls
        calories_per_rep = 0.2 * (weight_kg / 70)
    else:  # Squats
        # Squats burn more calories per rep
        calories_per_rep = 0.32 * (weight_kg / 70)
    return reps * calories_per_rep

def display_summary(exercise_type, reps, calories, duration, show_time=None):
    """Display exercise summary in a formatted way"""
    st.markdown("### Exercise Summary")
    st.markdown(f"**Session completed at:** {show_time}")
    
    summary_data = {
        "Exercise Type": exercise_type,
        "Total Reps": reps,
        "Calories Burned": f"{calories:.1f} kcal",
        "Exercise Duration": duration
    }
    
    # Create two columns for summary
    col1, col2 = st.columns(2)
    
    # Distribute data across columns
    for i, (metric, value) in enumerate(summary_data.items()):
        if i % 2 == 0:
            with col1:
                st.metric(metric, value)
        else:
            with col2:
                st.metric(metric, value)

def reset_all_states():
    """Reset all session states to initial values"""
    if 'bicep_model' in st.session_state:
        st.session_state.bicep_model.reset_counter()
    if 'squat_detector' in st.session_state:
        st.session_state.squat_detector.reset_counter()
    st.session_state.calories_burned = 0.0
    st.session_state.last_rep_count = 0
    st.session_state.exercise_duration = 0
    st.session_state.show_summary = False
    st.session_state.summary_data = None
    st.session_state.start_time = None

def load_css():
    css_file = STYLES_DIR / "main.css"
    if not css_file.exists():
        # Create main.css if it doesn't exist
        with open(css_file, "w") as f:
            f.write("""
/* Dark Aesthetic Theme */
:root {
    --primary-color: #FF4B2B;
    --secondary-color: #FF416C;
    --dark-bg: rgba(13, 17, 23, 0.95);
    --card-bg: rgba(22, 27, 34, 0.8);
    --text-primary: #ffffff;
    --text-secondary: #8b949e;
    --accent-gradient: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
}

/* Rest of the CSS content */
/* ... (previous CSS code) ... */
            """)
    
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def add_bg_from_local():
    # Use a default background color if no image is available
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(45deg, #1a1a1a, #2d2d2d);
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def main():
    st.title("AI Fitness Trainer 💪")
    
    # Add a sidebar
    with st.sidebar:
        st.header("Settings")
        st.write("Adjust your camera settings here")
        
        # Add quality options
        quality = st.select_slider(
            "Video Quality",
            options=["Low", "Medium", "High"],
            value="Medium"
        )

    # Configure RTC
    rtc_configuration = RTCConfiguration(
        {"iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]}
        ]}
    )
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Add WebRTC streamer with error handling
        try:
            webrtc_ctx = webrtc_streamer(
                key="pose-detection",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=rtc_configuration,
                video_frame_callback=video_frame_callback,
                media_stream_constraints={
                    "video": {
                        "width": {"ideal": 1280 if quality == "High" else 640},
                        "height": {"ideal": 720 if quality == "High" else 480},
                        "frameRate": {"ideal": 30 if quality == "High" else 20}
                    },
                    "audio": False
                },
                async_processing=True
            )
        except Exception as e:
            st.error(f"Error initializing camera: {str(e)}")
            st.info("Please check your camera permissions and try again.")
    
    with col2:
        # Add instructions
        st.markdown("""
        ### Instructions:
        1. Click 'START' to begin
        2. Allow camera access
        3. Adjust quality if needed
        4. Click 'STOP' when done
        
        ### Troubleshooting:
        - Ensure camera permissions
        - Try refreshing the page
        - Lower quality if laggy
        - Check internet connection
        """)

if __name__ == "__main__":
    main()