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
        # Simple image upload for testing
        uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_file is not None:
            # Convert the file to an opencv image.
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            
            # Display the image
            st.image(image, channels="BGR", use_column_width=True)
            st.success("✅ Image processed successfully!")
    
    with col2:
        st.markdown("""
        ### Basic Test
        1. Upload an image
        2. Wait for processing
        3. See results
        
        Once this works, we'll add camera support.
        """)

if __name__ == "__main__":
    main()