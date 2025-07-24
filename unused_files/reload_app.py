#!/usr/bin/env python3
"""
Simple script to reload the Streamlit app
"""
import os
import time

def touch_file(file_path):
    """Touch a file to update its modification time"""
    with open(file_path, 'a'):
        os.utime(file_path, None)
    print(f"Touched {file_path}")

if __name__ == "__main__":
    # Touch the main file
    touch_file("finance_tracker.py")
    
    # Touch all pages
    pages_dir = "pages"
    if os.path.exists(pages_dir):
        for file in os.listdir(pages_dir):
            if file.endswith(".py"):
                touch_file(os.path.join(pages_dir, file))
    
    print("App reload triggered")