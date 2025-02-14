import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time
from datetime import datetime
from pathlib import Path
import sys

# Add the parent directory to the path to import custom models
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from models.custom_models import BicepModel, SquatDetector

st.set_page_config(
    page_title="Workout - AI Fitness Trainer",
    page_icon="🏋️‍♂️",
    layout="wide"
)

# Initialize session state
if 'processing_active' not in st.session_state:
    st.session_state.processing_active = False
if 'bicep_model' not in st.session_state:
    st.session_state.bicep_model = BicepModel()
if 'squat_detector' not in st.session_state:
    st.session_state.squat_detector = SquatDetector()
if 'pose' not in st.session_state:
    st.session_state.pose = mp.solutions.pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5)
if 'current_exercise' not in st.session_state:
    st.session_state.current_exercise = 'Bicep Curls'
if 'camera' not in st.session_state:
    st.session_state.camera = None
if 'calories_burned' not in st.session_state:
    st.session_state.calories_burned = 0.0
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'exercise_duration' not in st.session_state:
    st.session_state.exercise_duration = 0
if 'last_rep_count' not in st.session_state:
    st.session_state.last_rep_count = 0
if 'selected_hand' not in st.session_state:
    st.session_state.selected_hand = 'Right'

def initialize_camera():
    return cv2.VideoCapture(0)

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def calculate_calories_from_reps(reps, weight_kg, exercise_type):
    if exercise_type == 'Bicep Curls':
        calories_per_rep = 0.2 * (weight_kg / 70)
    else:  # Squats
        calories_per_rep = 0.32 * (weight_kg / 70)
    return reps * calories_per_rep

def save_workout_summary():
    if st.session_state.start_time is not None:
        workout_data = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'exercise_type': st.session_state.current_exercise,
            'reps': st.session_state.last_rep_count,
            'calories': st.session_state.calories_burned,
            'duration_mins': st.session_state.exercise_duration / 60
        }
        
        if 'workout_history' not in st.session_state:
            st.session_state.workout_history = []
        
        st.session_state.workout_history.append(workout_data)

def main():
    st.markdown("""
        <div style='text-align: center; padding: 0.5rem;'>
            <h1 style='color: #FF4B2B; font-size: 1.75rem;'>Workout</h1>
        </div>
    """, unsafe_allow_html=True)

    # Mobile-friendly layout
    # Video feed container
    st.markdown("""
        <div style='background: rgba(22, 27, 34, 0.8); padding: 0.5rem; border-radius: 12px; margin-bottom: 0.75rem;'>
            <h3 style='color: #FF4B2B; margin-bottom: 0.5rem; font-size: 1rem;'>Camera Feed</h3>
        </div>
    """, unsafe_allow_html=True)
    
    stframe = st.empty()
    metrics_container = st.empty()

    # Exercise settings in expandable section
    with st.expander("Workout Settings", expanded=True):
        exercise_type = st.radio(
            "Choose Exercise:",
            options=['Bicep Curls', 'Squats'],
            index=0 if st.session_state.current_exercise == 'Bicep Curls' else 1,
        )

        if exercise_type == 'Bicep Curls':
            selected_hand = st.radio(
                "Select Hand:",
                options=['Left', 'Right', 'Both'],
                index=['Left', 'Right', 'Both'].index(st.session_state.selected_hand)
            )
            st.session_state.selected_hand = selected_hand

        weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
        
        col1, col2 = st.columns(2)
        with col1:
            show_angles = st.checkbox("Show Angles", value=True)
        with col2:
            show_counter = st.checkbox("Show Counter", value=True)

    # Camera controls
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Camera", use_container_width=True):
            st.session_state.processing_active = True
            if st.session_state.camera is None:
                st.session_state.camera = initialize_camera()
                st.session_state.start_time = time.time()
                st.session_state.calories_burned = 0.0
                st.session_state.last_rep_count = 0

    with col2:
        if st.button("Stop Camera", use_container_width=True):
            if st.session_state.processing_active:
                save_workout_summary()
            st.session_state.processing_active = False
            if st.session_state.camera is not None:
                st.session_state.camera.release()
                st.session_state.camera = None

    # Reset button full width
    if st.button("Reset Counter", use_container_width=True):
        if exercise_type == 'Bicep Curls':
            st.session_state.bicep_model.reset_counter()
        else:
            st.session_state.squat_detector.reset_counter()
        st.session_state.calories_burned = 0.0
        st.session_state.last_rep_count = 0
        if st.session_state.processing_active:
            st.session_state.start_time = time.time()

    try:
        while st.session_state.processing_active and st.session_state.camera is not None:
            ret, frame = st.session_state.camera.read()
            if not ret:
                st.error("Failed to read from camera!")
                break

            # Flip frame horizontally
            frame = cv2.flip(frame, 1)

            # Process frame based on selected exercise
            if exercise_type == 'Bicep Curls':
                processed_frame = st.session_state.bicep_model.process_frame(
                    frame,
                    show_angles=show_angles,
                    show_counter=show_counter,
                    weight_kg=weight_kg,
                    selected_hand=selected_hand
                )
                current_reps = st.session_state.bicep_model.counter
            else:  # Squats
                processed_frame = st.session_state.squat_detector.process_frame(
                    frame,
                    show_angles=show_angles,
                    show_counter=show_counter
                )
                current_reps = st.session_state.squat_detector.counter

            # Update calories if rep count increased
            if current_reps > st.session_state.last_rep_count:
                new_calories = calculate_calories_from_reps(
                    current_reps - st.session_state.last_rep_count,
                    weight_kg,
                    exercise_type
                )
                st.session_state.calories_burned += new_calories
                st.session_state.last_rep_count = current_reps

            # Update exercise duration
            if st.session_state.start_time is not None:
                st.session_state.exercise_duration = time.time() - st.session_state.start_time

            # Display metrics
            with metrics_container:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Reps", current_reps)
                with col2:
                    st.metric("Calories Burned", f"{st.session_state.calories_burned:.1f} kcal")
                with col3:
                    st.metric("Exercise Duration", format_time(st.session_state.exercise_duration))

            if processed_frame is not None:
                # Update display
                stframe.image(processed_frame, channels="BGR", use_container_width=True)

            # Small delay to prevent high CPU usage
            time.sleep(0.01)

    except Exception as e:
        st.error(f"Error: {e}")

    finally:
        if not st.session_state.processing_active and st.session_state.camera is not None:
            st.session_state.camera.release()
            st.session_state.camera = None
            st.session_state.start_time = None
            st.session_state.exercise_duration = 0
            st.session_state.last_rep_count = 0
            stframe.empty()
            metrics_container.empty()

if __name__ == "__main__":
    main() 