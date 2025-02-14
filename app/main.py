import streamlit as st
from pathlib import Path
import time
from datetime import datetime
import os

# Must be the first Streamlit command
st.set_page_config(
    page_title="AI Fitness Trainer",
    page_icon="🏋️‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

import cv2
import sys
import base64

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

def initialize_camera():
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            return cap
    except Exception as e:
        st.error(f"Camera initialization error: {e}")
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
    # Initialize session state
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'workout_history' not in st.session_state:
        st.session_state.workout_history = []
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    # Hero Section
    st.markdown("""
        <div class="hero-section">
            <h1>AI FITNESS</h1>
            <p class="subtitle">Your Personal AI Trainer</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <h3>Form Check</h3>
                <p>Real-time feedback</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>Progress</h3>
                <p>Track your gains</p>
            </div>
        """, unsafe_allow_html=True)
        
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔥</div>
                <h3>Calories</h3>
                <p>Track burned</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📱</div>
                <h3>Exercises</h3>
                <p>Multiple types</p>
            </div>
        """, unsafe_allow_html=True)

    # Navigation Buttons
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Workout", use_container_width=True, key="start_workout"):
            st.switch_page("pages/1_Workout.py")
    
    with col2:
        if st.button("View History", use_container_width=True, key="view_history"):
            st.switch_page("pages/2_History.py")

    # Custom CSS
    st.markdown("""
        <style>
        /* Hero Section */
        .hero-section {
            text-align: center;
            padding: 2rem 1rem;
            margin: -1rem -1rem 1rem -1rem;
            background: linear-gradient(45deg, #FF4B2B, #FF416C);
            border-radius: 0 0 20px 20px;
        }
        
        .hero-section h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            color: white;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .subtitle {
            font-size: 1rem;
            color: rgba(255, 255, 255, 0.9);
            margin: 0.5rem 0 0 0;
        }
        
        /* Feature Cards */
        .feature-card {
            background: rgba(22, 27, 34, 0.8);
            padding: 1rem;
            border-radius: 15px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 0.75rem;
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .feature-card h3 {
            font-size: 1rem;
            margin: 0.5rem 0;
            color: #FF4B2B;
        }
        
        .feature-card p {
            font-size: 0.8rem;
            margin: 0;
            color: #8b949e;
        }
        
        /* Button Styling */
        .stButton button {
            background: linear-gradient(45deg, #FF4B2B, #FF416C);
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 12px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
        }
        
        .stButton button:active {
            transform: scale(0.98);
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()