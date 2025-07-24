#!/usr/bin/env python3
"""
PDF Parser Setup Script

This script installs the necessary dependencies for PDF parsing.
"""

import subprocess
import sys
import os
import platform

def check_java():
    """Check if Java is installed"""
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def install_pdf_dependencies():
    """Install PDF parsing dependencies"""
    print("Installing PDF parsing dependencies...")
    
    # Check if Java is installed (required for tabula-py)
    java_installed = check_java()
    if not java_installed:
        print("\nWARNING: Java JRE not detected. tabula-py requires Java to be installed.")
        print("Please install Java before continuing.")
        
        # Provide platform-specific instructions
        system = platform.system()
        if system == "Darwin":  # macOS
            print("\nOn macOS, you can install Java with:")
            print("  brew install --cask java")
        elif system == "Windows":
            print("\nOn Windows, download and install Java from:")
            print("  https://www.java.com/download/")
        elif system == "Linux":
            print("\nOn Linux, install Java with your package manager:")
            print("  sudo apt install default-jre  # Debian/Ubuntu")
            print("  sudo yum install java-11-openjdk  # CentOS/RHEL")
        
        user_input = input("\nDo you want to continue with installation anyway? (y/n): ")
        if user_input.lower() != 'y':
            print("Installation aborted. Please install Java and try again.")
            return False
    
    dependencies = [
        "pypdf2>=3.0.0",
        "tabula-py>=2.7.0",
        "pdfminer.six>=20221105"
    ]
    
    success = True
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except subprocess.CalledProcessError as e:
            print(f"Error installing {dep}: {e}")
            success = False
    
    if success:
        print("\nPDF parsing dependencies installed successfully!")
        print("You can now use the document upload feature to parse PDF statements.")
        return True
    else:
        print("\nSome dependencies could not be installed.")
        print("You may need to install them manually:")
        for dep in dependencies:
            print(f"  pip install {dep}")
        return False

if __name__ == "__main__":
    install_pdf_dependencies()