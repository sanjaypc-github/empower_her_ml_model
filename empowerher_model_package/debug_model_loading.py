#!/usr/bin/env python3
"""
Debug script to test model loading locally
"""

import os
import sys
import joblib
import pandas as pd

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

def test_model_loading():
    """Test if models can be loaded locally"""
    
    print("Testing Model Loading Locally...")
    print("="*50)
    
    # Test 1: Check if files exist
    print("1. Checking if model files exist:")
    model_files = [
        "model/crime_predictor.pkl",
        "model/preprocessor.pkl", 
        "data/crime_data.csv"
    ]
    
    for file_path in model_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} - {file_size} bytes")
        else:
            print(f"   ❌ {file_path} - MISSING")
    
    print("\n2. Testing model loading:")
    
    # Test 2: Load ML model
    try:
        model_path = "model/crime_predictor.pkl"
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            print(f"   ✅ ML Model loaded successfully: {type(model).__name__}")
        else:
            print(f"   ❌ ML Model file not found")
    except Exception as e:
        print(f"   ❌ Error loading ML model: {e}")
    
    # Test 3: Load preprocessor
    try:
        from utils.preprocess import CrimeDataPreprocessor
        preprocessor = CrimeDataPreprocessor()
        preprocessor_path = "model/preprocessor.pkl"
        if os.path.exists(preprocessor_path):
            preprocessor.load_preprocessor(preprocessor_path)
            print(f"   ✅ Preprocessor loaded successfully")
            print(f"      Is fitted: {preprocessor.is_fitted}")
        else:
            print(f"   ❌ Preprocessor file not found")
    except Exception as e:
        print(f"   ❌ Error loading preprocessor: {e}")
    
    # Test 4: Load grid classifier
    try:
        from utils.grid_classifier import GridClassifier
        data_path = "data/crime_data.csv"
        if os.path.exists(data_path):
            crime_data = pd.read_csv(data_path)
            print(f"   ✅ Crime data loaded: {len(crime_data)} records")
            
            grid_classifier = GridClassifier(grid_size=0.01)
            grid_summary = grid_classifier.create_grid(crime_data)
            print(f"   ✅ Grid classifier initialized: {grid_summary['total_grids']} grids")
        else:
            print(f"   ❌ Crime data file not found")
    except Exception as e:
        print(f"   ❌ Error loading grid classifier: {e}")
    
    print("\n3. Testing file paths that the API uses:")
    
    # Test 5: Test the exact paths the API uses
    api_dir = "api"
    if os.path.exists(api_dir):
        print(f"   ✅ API directory exists: {api_dir}")
        
        # Test relative paths from API directory
        api_model_path = os.path.join(api_dir, "..", "model", "crime_predictor.pkl")
        api_data_path = os.path.join(api_dir, "..", "data", "crime_data.csv")
        
        print(f"   API model path: {api_model_path}")
        print(f"   API data path: {api_data_path}")
        
        if os.path.exists(api_model_path):
            print(f"   ✅ API model path accessible")
        else:
            print(f"   ❌ API model path NOT accessible")
            
        if os.path.exists(api_data_path):
            print(f"   ✅ API data path accessible")
        else:
            print(f"   ❌ API data path NOT accessible")
    else:
        print(f"   ❌ API directory not found: {api_dir}")
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print("="*50)
    
    print("If all tests pass locally but fail on Render:")
    print("1. File paths might be different on Render")
    print("2. Dependencies might not be installed correctly")
    print("3. File permissions might be different")
    print("4. Working directory might be different")

if __name__ == "__main__":
    test_model_loading()

