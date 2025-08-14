#!/usr/bin/env python3
"""
Quick API test to see which endpoints work
"""

import requests
import json

def test_endpoints():
    """Test all endpoints to see which ones work"""
    
    base_url = "https://empower-her-ml-model.onrender.com"
    
    print("Testing All Endpoints...")
    print("="*60)
    print(f"Base URL: {base_url}")
    print("="*60)
    
    # Test endpoints that don't require models
    simple_endpoints = [
        ("GET", "/health", None),
        ("GET", "/example_request", None),
        ("GET", "/model_info", None),
        ("GET", "/grid_summary", None)
    ]
    
    print("1. Testing Simple Endpoints (No Models Required):")
    print("-" * 50)
    
    for method, endpoint, data in simple_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=15)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=15)
            
            if response.status_code == 200:
                print(f"✅ {method} {endpoint} - WORKING")
                try:
                    result = response.json()
                    if "error" in result:
                        print(f"   ❌ But returns error: {result['error']}")
                    else:
                        print(f"   ✅ Returns data successfully")
                except:
                    print(f"   ✅ Returns response (not JSON)")
            else:
                print(f"❌ {method} {endpoint} - FAILED ({response.status_code})")
                print(f"   Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ {method} {endpoint} - ERROR: {e}")
    
    print("\n2. Testing Model-Dependent Endpoints:")
    print("-" * 50)
    
    # Test endpoints that require models
    model_endpoints = [
        ("POST", "/live_safety_check", {
            "latitude": 10.9467,
            "longitude": 76.8653,
            "time": "04:00",
            "user_id": "test_user"
        }),
        ("POST", "/predict", {
            "latitude": 10.9467,
            "longitude": 76.8653,
            "time": "04:00",
            "severity": 4,
            "crime_type": "Sexual Harassment"
        }),
        ("POST", "/check_grid_zone", {
            "latitude": 10.9467,
            "longitude": 76.8653
        })
    ]
    
    for method, endpoint, data in model_endpoints:
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(f"{base_url}{endpoint}", json=data, headers=headers, timeout=20)
            
            if response.status_code == 200:
                print(f"✅ {method} {endpoint} - WORKING")
                try:
                    result = response.json()
                    if "error" in result:
                        print(f"   ❌ But returns error: {result['error']}")
                    else:
                        print(f"   ✅ Returns data successfully")
                except:
                    print(f"   ✅ Returns response (not JSON)")
            else:
                print(f"❌ {method} {endpoint} - FAILED ({response.status_code})")
                print(f"   Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ {method} {endpoint} - ERROR: {e}")
    
    print("\n" + "="*60)
    print("ANALYSIS:")
    print("="*60)
    
    print("If only /example_request works, it means:")
    print("❌ Model files are missing or not accessible")
    print("❌ The API can't load the ML models")
    print("❌ Grid classifier is not initialized")
    print("\nSOLUTION:")
    print("1. Check if model files exist in your repository")
    print("2. Add missing files to GitHub")
    print("3. Push changes to trigger Render redeployment")

if __name__ == "__main__":
    test_endpoints()
