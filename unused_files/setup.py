import subprocess
import os
import sys

def setup():
    """Setup the finance tracker application"""
    print("Setting up Finance Tracker...")
    
    # Get the absolute path to the requirements file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(current_dir, "requirements.txt")
    
    if not os.path.exists(requirements_path):
        print(f"Error: Requirements file not found at {requirements_path}")
        # Create the requirements file if it doesn't exist
        with open(requirements_path, "w") as f:
            f.write("streamlit>=1.22.0\n")
            f.write("pandas>=1.5.0\n")
            f.write("plotly>=5.13.0\n")
            f.write("pyyaml>=6.0\n")
            f.write("numpy>=1.24.0\n")
        print("Created requirements.txt file")
    
    # Install dependencies
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False
    
    print("Setup completed successfully!")
    return True

if __name__ == "__main__":
    setup()