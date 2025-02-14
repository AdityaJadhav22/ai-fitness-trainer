import cv2

def test_webcam():
    print("Testing webcam access...")
    
    # Try different camera indices
    for index in range(3):
        print(f"\nTrying camera index {index}")
        cap = cv2.VideoCapture(index)
        
        if not cap.isOpened():
            print(f"Failed to open camera {index}")
            continue
            
        ret, frame = cap.read()
        if ret:
            print(f"Successfully accessed camera {index}")
            print(f"Frame shape: {frame.shape}")
            
            # Try to show the frame
            cv2.imshow(f'Camera {index} Test', frame)
            cv2.waitKey(2000)  # Wait for 2 seconds
            cv2.destroyAllWindows()
        else:
            print(f"Failed to read frame from camera {index}")
            
        cap.release()
    
    print("\nWebcam test completed")

if __name__ == "__main__":
    test_webcam() 