import streamlit as st
import cv2
import av
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# Page config
st.set_page_config(
    page_title="AI Fitness Trainer",
    page_icon="💪",
    layout="wide"
)

def video_frame_callback(frame):
    """Simple callback that just returns the frame as is"""
    return frame

def main():
    st.title("AI Fitness Trainer 💪")
    
    # Configure RTC with minimal STUN servers
    rtc_configuration = RTCConfiguration(
        {"iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]}
        ]}
    )
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        try:
            webrtc_ctx = webrtc_streamer(
                key="test-camera",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=rtc_configuration,
                video_frame_callback=video_frame_callback,
                media_stream_constraints={
                    "video": {
                        "width": {"ideal": 480},
                        "height": {"ideal": 360},
                        "frameRate": {"max": 10}
                    },
                    "audio": False
                },
                async_processing=False,
            )
            
            if webrtc_ctx.state.playing:
                st.success("✅ Camera connected!")
            else:
                st.warning("⚠️ Click 'START' to begin")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Please check camera permissions")
    
    with col2:
        st.markdown("""
        ### Basic Test
        1. Click 'START'
        2. Allow camera
        3. Wait for connection
        
        If this works, we'll add pose detection next.
        """)

if __name__ == "__main__":
    main()