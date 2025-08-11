#!/usr/bin/env python3
"""
Test script for Women EmpowerHer Crime Prediction System
"""

import os
import sys
import json
import requests
import pandas as pd
import joblib
from datetime import datetime

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.preprocess import CrimeDataPreprocessor

def test_data_loading():
    """Test if crime data can be loaded"""
    print("Testing data loading...")
    
    data_path = os.path.join('data', 'crime_data.csv')
    if not os.path.exists(data_path):
        print("✗ Data file not found")
        return False
    
    try:
        df = pd.read_csv(data_path)
        print(f"✓ Data loaded successfully: {len(df)} records")
        print(f"  Columns: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return False

def test_preprocessing():
    """Test data preprocessing"""
    print("\nTesting data preprocessing...")
    
    data_path = os.path.join('data', 'crime_data.csv')
    if not os.path.exists(data_path):
        print("✗ Data file not found")
        return False
    
    try:
        # Load sample data
        df = pd.read_csv(data_path).head(100)  # Use first 100 records for testing
        
        # Test preprocessor
        preprocessor = CrimeDataPreprocessor()
        features, labels = preprocessor.fit_transform(df)
        
        print(f"✓ Preprocessing successful")
        print(f"  Features shape: {features.shape}")
        print(f"  Labels shape: {labels.shape}")
        print(f"  Feature names: {list(features.columns)}")
        
        # Test risk classification
        safe_count = (labels == 0).sum()
        risky_count = (labels == 1).sum()
        print(f"  Safe: {safe_count}, Risky: {risky_count}")
        
        return True
    except Exception as e:
        print(f"✗ Error in preprocessing: {e}")
        return False

def test_model_training():
    """Test model training"""
    print("\nTesting model training...")
    
    data_path = os.path.join('data', 'crime_data.csv')
    if not os.path.exists(data_path):
        print("✗ Data file not found")
        return False
    
    try:
        # Load and preprocess data
        df = pd.read_csv(data_path).head(500)  # Use 500 records for testing
        preprocessor = CrimeDataPreprocessor()
        features, labels = preprocessor.fit_transform(df)
        
        # Train a simple model
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42
        )
        
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        accuracy = model.score(X_test, y_test)
        print(f"✓ Model training successful")
        print(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        # Test prediction
        sample_prediction = model.predict(X_test[:1])
        sample_proba = model.predict_proba(X_test[:1])
        print(f"  Sample prediction: {sample_prediction[0]}")
        print(f"  Sample probabilities: {sample_proba[0]}")
        
        return True
    except Exception as e:
        print(f"✗ Error in model training: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\nTesting API endpoints...")
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✓ Health endpoint working")
            print(f"  Model loaded: {health_data.get('model_loaded', False)}")
            print(f"  Preprocessor loaded: {health_data.get('preprocessor_loaded', False)}")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ API server not running: {e}")
        print("  Start the API server with: python api/app.py")
        return False
    
    # Test prediction endpoint
    try:
        test_data = {
            "latitude": 10.9467,
            "longitude": 76.8653,
            "time": "04:00",
            "severity": 4,
            "crime_type": "Sexual Harassment"
        }
        
        response = requests.post(
            f"{base_url}/predict",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            prediction_data = response.json()
            print("✓ Prediction endpoint working")
            print(f"  Prediction: {prediction_data.get('prediction')}")
            print(f"  Confidence: {prediction_data.get('confidence')}")
            print(f"  Risk score: {prediction_data.get('risk_score')}")
        else:
            print(f"✗ Prediction endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Prediction endpoint error: {e}")
        return False
    
    return True

def test_model_files():
    """Test if model files exist and can be loaded"""
    print("\nTesting model files...")
    
    model_path = os.path.join('model', 'crime_predictor.pkl')
    preprocessor_path = os.path.join('model', 'preprocessor.pkl')
    
    # Check if files exist
    if not os.path.exists(model_path):
        print("✗ Model file not found")
        print("  Run training first: python train_model.py")
        return False
    
    if not os.path.exists(preprocessor_path):
        print("✗ Preprocessor file not found")
        print("  Run training first: python train_model.py")
        return False
    
    # Test loading model
    try:
        model = joblib.load(model_path)
        print("✓ Model file can be loaded")
        print(f"  Model type: {type(model).__name__}")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return False
    
    # Test loading preprocessor
    try:
        preprocessor = CrimeDataPreprocessor()
        preprocessor.load_preprocessor(preprocessor_path)
        print("✓ Preprocessor file can be loaded")
        print(f"  Is fitted: {preprocessor.is_fitted}")
    except Exception as e:
        print(f"✗ Error loading preprocessor: {e}")
        return False
    
    return True

def test_firebase_utils():
    """Test Firebase utilities"""
    print("\nTesting Firebase utilities...")
    
    try:
        from utils.firebase_utils import FirebaseManager
        
        # Test Firebase manager initialization
        firebase_manager = FirebaseManager()
        
        if firebase_manager.is_initialized:
            print("✓ Firebase manager initialized")
        else:
            print("⚠ Firebase manager not initialized (expected without credentials)")
        
        # Test feedback parsing
        mock_feedback = {
            'feedback': 'Bad',
            'suggestion': 'Add Madukkarai PS at night time for Sexual Harassment',
            'lat': 10.9467,
            'lon': 76.8653,
            'time': '04:00',
            'crime_type': 'Sexual Harassment'
        }
        
        parsed = firebase_manager.parse_feedback_suggestion(mock_feedback)
        print("✓ Feedback parsing working")
        print(f"  Parsed crime type: {parsed.get('crime_type')}")
        print(f"  Extracted info: {parsed.get('extracted_info')}")
        
        return True
    except Exception as e:
        print(f"✗ Error in Firebase utilities: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("="*60)
    print("WOMEN EMPOWERHER - SYSTEM COMPREHENSIVE TEST")
    print("="*60)
    
    tests = [
        ("Data Loading", test_data_loading),
        ("Data Preprocessing", test_preprocessing),
        ("Model Training", test_model_training),
        ("Model Files", test_model_files),
        ("Firebase Utilities", test_firebase_utils),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
    else:
        print("⚠ Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 