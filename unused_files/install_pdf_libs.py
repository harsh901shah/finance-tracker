#!/usr/bin/env python3
"""
Simple script to install PDF parsing libraries
"""
import subprocess
import sys

def install_pdf_libraries():
    print("Installing PDF parsing libraries...")
    
    libraries = [
        "PyPDF2",
        "pdfplumber",  # Added pdfplumber as primary PDF parser
        "tabula-py",
        "pdfminer.six"
    ]
    
    for lib in libraries:
        print(f"Installing {lib}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            print(f"Successfully installed {lib}")
        except Exception as e:
            print(f"Error installing {lib}: {e}")
            if lib == "tabula-py":
                print("Note: tabula-py requires Java to be installed.")
            return False
    
    print("\nAll PDF libraries installed successfully!")
    return True

if __name__ == "__main__":
    install_pdf_libraries()