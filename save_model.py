import tensorflow as tf  # or import torch for PyTorch
import os

def save_model_from_checkpoint(checkpoint_path, save_path):
    try:
        # Load model architecture (you'll need to define the same architecture as in training)
        model = tf.keras.Sequential([
            # Add your model layers here
            # For example:
            tf.keras.layers.Conv2D(32, 3, activation='relu', input_shape=(224, 224, 3)),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        # Load weights from checkpoint
        model.load_weights(checkpoint_path)
        
        # Save the complete model
        model.save(save_path)
        print(f"Model saved successfully to {save_path}")
        
    except Exception as e:
        print(f"Error saving model: {e}")

# Use the function
checkpoint_path = r"C:\Users\adity\Desktop\major_proj\.ipynb_checkpoints"
save_path = r"C:\Users\adity\Desktop\major_proj\bicep_model.h5"

save_model_from_checkpoint(checkpoint_path, save_path) 