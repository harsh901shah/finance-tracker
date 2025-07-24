#!/usr/bin/env python3
import os
import sys
import subprocess
import platform

def run_app():
    """Run the finance tracker application"""
    print("Starting Finance Tracker...")
    
    # Get the absolute path to the finance_tracker.py file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "finance_tracker.py")
    
    if not os.path.exists(app_path):
        print(f"Error: app.py not found at {app_path}")
        return False
    
    # Determine the Python command to use
    python_cmd = sys.executable
    
    # Run the Streamlit app
    try:
        # Try running streamlit directly first
        try:
            print("Running Streamlit app...")
            subprocess.run(["streamlit", "run", app_path], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # If streamlit command fails, try using python/python3 -m streamlit
            print("Streamlit command not found, trying with Python module...")
            subprocess.run([python_cmd, "-m", "streamlit", "run", app_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        return False
    except FileNotFoundError:
        print("Error: Streamlit not found. Please install it using 'pip3 install streamlit'")
        print("If you're on macOS, make sure to use 'python3' and 'pip3' commands.")
        return False
    
    return True

if __name__ == "__main__":
    run_app()