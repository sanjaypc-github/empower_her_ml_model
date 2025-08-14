#!/usr/bin/env python3
"""
Check if model files exist in the repository
"""

import os
import sys

def check_model_files():
    """Check if required model files exist"""
    
    print("Checking Model Files...")
    print("="*50)
    
    # Check model files
    model_files = [
        "model/crime_predictor.pkl",
        "model/preprocessor.pkl",
        "data/crime_data.csv"
    ]
    
    missing_files = []
    
    for file_path in model_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path} - {file_size} bytes")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    print("\n" + "="*50)
    
    if missing_files:
        print("❌ MISSING FILES:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nYou need to add these files to your repository!")
        print("These files are required for the API to work.")
        return False
    else:
        print("✅ All model files are present!")
        print("Your API should work correctly.")
        return True

def check_directory_structure():
    """Check if directory structure is correct"""
    
    print("\nChecking Directory Structure...")
    print("="*50)
    
    required_dirs = [
        "api",
        "model", 
        "data",
        "utils"
    ]
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ - MISSING")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    print("MODEL FILES CHECK")
    print("="*50)
    
    check_directory_structure()
    success = check_model_files()
    
    if not success:
        print("\n❌ You need to add the missing model files to your repository.")
        print("Without these files, your API will not work.")
        print("\nTo fix this:")
        print("1. Make sure you have the model files locally")
        print("2. Add them to your repository")
        print("3. Push to GitHub")
        print("4. Render will automatically redeploy")
    else:
        print("\n🎉 All files are present! Your API should work.")
