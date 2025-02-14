import nbformat
import os
import sys
from nbconvert import PythonExporter

def extract_model_from_notebook(notebook_path, output_script_path):
    try:
        # Read the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        # Convert notebook to Python script
        python_exporter = PythonExporter()
        python_code, _ = python_exporter.from_notebook_node(notebook)
        
        # Save the Python script
        with open(output_script_path, 'w', encoding='utf-8') as f:
            f.write(python_code)
            
        print(f"Successfully extracted code to {output_script_path}")
        
        # Add model saving code
        with open(output_script_path, 'a', encoding='utf-8') as f:
            f.write("\n\n# Save the trained model\n")
            f.write("try:\n")
            f.write("    model.save('bicep_model.h5')\n")
            f.write("    print('Model saved successfully as bicep_model.h5')\n")
            f.write("except Exception as e:\n")
            f.write("    print(f'Error saving model: {e}')\n")
            
    except Exception as e:
        print(f"Error extracting model: {e}")

# Use the function
notebook_path = r"C:\Users\adity\Desktop\major_proj\.ipynb_checkpoints\Media Pipe Pose Tutorial-checkpoint-checkpoint-checkpoint.ipynb"  # Update this path
output_script_path = "model_script.py"

extract_model_from_notebook(notebook_path, output_script_path) 