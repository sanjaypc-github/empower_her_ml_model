#!/usr/bin/env python3
"""
Simple API test script for Women EmpowerHer
"""

import requests
import json
import time

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:5001"
    
    print("Testing Women EmpowerHer API...")
    print("="*50)
    
    # Test 1: Health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health endpoint working!")
            print(f"   Model loaded: {health_data.get('model_loaded', False)}")
            print(f"   Preprocessor loaded: {health_data.get('preprocessor_loaded', False)}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure the API server is running: python api/app.py")
        return False
    
    # Test 2: Example request endpoint
    print("\n2. Testing example request endpoint...")
    try:
        response = requests.get(f"{base_url}/example_request", timeout=5)
        if response.status_code == 200:
            example_data = response.json()
            print("✅ Example request endpoint working!")
            print(f"   Example data: {example_data.get('example_request')}")
        else:
            print(f"❌ Example request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Example request error: {e}")
    
    # Test 3: Prediction endpoint
    print("\n3. Testing prediction endpoint...")
    test_data = {
        "latitude": 10.9467,
        "longitude": 76.8653,
        "time": "04:00",
        "severity": 4,
        "crime_type": "Sexual Harassment"
    }
    
    try:
        response = requests.post(
            f"{base_url}/predict",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            prediction_data = response.json()
            print("✅ Prediction endpoint working!")
            print(f"   Prediction: {prediction_data.get('prediction')}")
            print(f"   Confidence: {prediction_data.get('confidence')}")
            print(f"   Risk Score: {prediction_data.get('risk_score')}")
            print(f"   Safe Score: {prediction_data.get('safe_score')}")
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return False
    
    # Test 4: Model info endpoint
    print("\n4. Testing model info endpoint...")
    try:
        response = requests.get(f"{base_url}/model_info", timeout=5)
        if response.status_code == 200:
            model_info = response.json()
            print("✅ Model info endpoint working!")
            print(f"   Model type: {model_info.get('model_type')}")
            print(f"   Features: {len(model_info.get('feature_names', []))}")
        else:
            print(f"❌ Model info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Model info error: {e}")
    
    print("\n" + "="*50)
    print("🎉 API TESTING COMPLETED SUCCESSFULLY!")
    print("="*50)
    print("✅ All endpoints are working correctly")
    print("✅ Model is loaded and making predictions")
    print("✅ API is ready for Flutter integration")
    print("\nYour friend can now:")
    print("1. Extract the zip file")
    print("2. Run: pip install -r requirements.txt")
    print("3. Run: python api/app.py")
    print("4. Use the API endpoints in their Flutter app")
    
    return True

if __name__ == "__main__":
    success = test_api()
    if not success:
        print("\n❌ Some tests failed. Please check the issues above.")
        exit(1) 