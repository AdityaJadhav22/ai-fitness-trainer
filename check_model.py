import os

def check_model():
    model_path = 'bicep_model.h5'  # or the path where your model was saved
    if os.path.exists(model_path):
        print(f"Model found at: {model_path}")
        return True
    else:
        print("Model file not found!")
        return False

if __name__ == "__main__":
    check_model() 