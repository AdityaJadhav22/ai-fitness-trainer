import streamlit as st
import cv2
import numpy as np

# Page config
st.set_page_config(
    page_title="AI Fitness Trainer",
    page_icon="💪",
    layout="wide"
)

def main():
    st.title("AI Fitness Trainer 💪")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Add a camera input
        camera = st.camera_input("Camera Feed")
        
        if camera is not None:
            # Convert the image from the camera to an opencv image
            bytes_data = camera.getvalue()
            img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            # Process the image (for now, just display it)
            st.image(img, channels="BGR", use_column_width=True)
    
    with col2:
        st.markdown("""
        ### Instructions
        1. Allow camera access when prompted
        2. Position yourself in frame
        3. Make sure you have good lighting
        4. Keep your full body visible
        """)
        
        # Add some stats or metrics (placeholder for now)
        st.metric(label="Camera Status", value="Active" if camera else "Waiting")

if __name__ == "__main__":
    main()