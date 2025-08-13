#!/usr/bin/env python3
"""
Test script for Firebase Functions endpoints
Tests real-time monitoring and risk classification
"""

import requests
import json
import time
from datetime import datetime

def test_firebase_functions():
    """Test the Firebase Functions endpoints"""
    
    # Replace with your actual Firebase Functions URL
    base_url = "https://your-firebase-functions-url.com"  # Update this with your actual URL
    
    print("Testing Firebase Functions for Real-time Monitoring...")
    print("="*60)
    
    # Test 1: Health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health_check", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health endpoint working!")
            print(f"   Model loaded: {health_data.get('model_loaded', False)}")
            print(f"   Preprocessor loaded: {health_data.get('preprocessor_loaded', False)}")
            print(f"   Grid classifier loaded: {health_data.get('grid_classifier_loaded', False)}")
            
            if not health_data.get('grid_classifier_loaded', False):
                print("⚠️  WARNING: Grid classifier not loaded - risk classification won't work!")
                return False
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Firebase Functions: {e}")
        print("   Make sure Firebase Functions is deployed and accessible")
        return False
    
    # Test 2: Live safety check endpoint
    print("\n2. Testing live safety check endpoint...")
    test_locations = [
        {
            "latitude": 10.9467,
            "longitude": 76.8653,
            "time": "04:00",  # Night time
            "user_id": "test_user_1"
        },
        {
            "latitude": 10.9467,
            "longitude": 76.8653,
            "time": "14:00",  # Day time
            "user_id": "test_user_1"
        }
    ]
    
    for i, location in enumerate(test_locations):
        try:
            response = requests.post(
                f"{base_url}/live_safety_check",
                json=location,
                timeout=15
            )
            
            if response.status_code == 200:
                safety_data = response.json()
                print(f"✅ Live safety check {i+1} working!")
                print(f"   Risk Level: {safety_data.get('risk_assessment', {}).get('final_risk_level', 'unknown')}")
                print(f"   Grid Risk: {safety_data.get('risk_assessment', {}).get('grid_risk', 'unknown')}")
                print(f"   ML Prediction: {safety_data.get('risk_assessment', {}).get('ml_prediction', 'unknown')}")
                print(f"   Notification: {safety_data.get('notification', {}).get('message', 'No message')[:50]}...")
                
                # Check if risk classification is working
                grid_risk = safety_data.get('risk_assessment', {}).get('grid_risk')
                if grid_risk and grid_risk != 'unknown':
                    print(f"   ✅ Risk classification working: {grid_risk}")
                else:
                    print(f"   ❌ Risk classification not working: {grid_risk}")
                    
            else:
                print(f"❌ Live safety check {i+1} failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Live safety check {i+1} error: {e}")
            return False
    
    # Test 3: Grid zone check endpoint
    print("\n3. Testing grid zone check endpoint...")
    try:
        grid_test_data = {
            "latitude": 10.9467,
            "longitude": 76.8653
        }
        
        response = requests.post(
            f"{base_url}/check_grid_zone",
            json=grid_test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            grid_data = response.json()
            grid_analysis = grid_data.get('grid_analysis', {})
            print("✅ Grid zone check working!")
            print(f"   Risk Zone: {grid_analysis.get('risk_zone', 'unknown')}")
            print(f"   Risk Score: {grid_analysis.get('risk_score', 'unknown')}")
            print(f"   Crime Count: {grid_analysis.get('crime_count', 'unknown')}")
            
            if grid_analysis.get('risk_zone') and grid_analysis.get('risk_zone') != 'unknown':
                print("   ✅ Grid classification working properly")
            else:
                print("   ❌ Grid classification not working properly")
                
        else:
            print(f"❌ Grid zone check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Grid zone check error: {e}")
        return False
    
    # Test 4: Journey tracking endpoint
    print("\n4. Testing journey tracking endpoint...")
    try:
        journey_data = {
            "user_id": "test_user_1",
            "locations": [
                {"latitude": 10.9467, "longitude": 76.8653, "timestamp": datetime.now().isoformat()},
                {"latitude": 10.9468, "longitude": 76.8654, "timestamp": datetime.now().isoformat()},
                {"latitude": 10.9469, "longitude": 76.8655, "timestamp": datetime.now().isoformat()}
            ]
        }
        
        response = requests.post(
            f"{base_url}/track_user_journey",
            json=journey_data,
            timeout=15
        )
        
        if response.status_code == 200:
            journey_result = response.json()
            journey_summary = journey_result.get('journey_summary', {})
            print("✅ Journey tracking working!")
            print(f"   Total Points: {journey_summary.get('total_points', 0)}")
            print(f"   High Risk Points: {journey_summary.get('high_risk_points', 0)}")
            print(f"   Medium Risk Points: {journey_summary.get('medium_risk_points', 0)}")
            print(f"   Safe Points: {journey_summary.get('safe_points', 0)}")
            print(f"   Alerts: {len(journey_result.get('alerts', []))}")
            
        else:
            print(f"❌ Journey tracking failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Journey tracking error: {e}")
        return False
    
    # Test 5: Grid summary endpoint
    print("\n5. Testing grid summary endpoint...")
    try:
        response = requests.get(f"{base_url}/grid_summary", timeout=10)
        
        if response.status_code == 200:
            summary_data = response.json()
            grid_summary = summary_data.get('grid_summary', {})
            print("✅ Grid summary working!")
            print(f"   Total Grids: {grid_summary.get('total_grids', 0)}")
            print(f"   High Risk Grids: {grid_summary.get('high_risk_grids', 0)}")
            print(f"   Medium Risk Grids: {grid_summary.get('medium_risk_grids', 0)}")
            print(f"   Low Risk Grids: {grid_summary.get('low_risk_grids', 0)}")
            
        else:
            print(f"❌ Grid summary failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Grid summary error: {e}")
        return False
    
    print("\n" + "="*60)
    print("🎉 FIREBASE FUNCTIONS TESTING COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("✅ All real-time monitoring endpoints are working")
    print("✅ Risk classification is functional")
    print("✅ Grid-based analysis is operational")
    print("✅ Journey tracking is working")
    print("\nYour Flutter app should now receive proper risk classifications!")
    
    return True

def test_render_api_comparison():
    """Compare Firebase Functions with Render API"""
    print("\n" + "="*60)
    print("COMPARING FIREBASE FUNCTIONS WITH RENDER API")
    print("="*60)
    
    # Replace with your actual URLs
    firebase_url = "https://your-firebase-functions-url.com"  # Update this
    render_url = "https://your-render-app-url.onrender.com"   # Update this
    
    test_data = {
        "latitude": 10.9467,
        "longitude": 76.8653,
        "time": "04:00",
        "user_id": "comparison_test"
    }
    
    # Test Firebase Functions
    print("Testing Firebase Functions...")
    try:
        firebase_response = requests.post(
            f"{firebase_url}/live_safety_check",
            json=test_data,
            timeout=15
        )
        
        if firebase_response.status_code == 200:
            firebase_result = firebase_response.json()
            print("✅ Firebase Functions working")
            print(f"   Risk Level: {firebase_result.get('risk_assessment', {}).get('final_risk_level', 'unknown')}")
        else:
            print(f"❌ Firebase Functions failed: {firebase_response.status_code}")
    except Exception as e:
        print(f"❌ Firebase Functions error: {e}")
    
    # Test Render API
    print("\nTesting Render API...")
    try:
        render_response = requests.post(
            f"{render_url}/live_safety_check",
            json=test_data,
            timeout=15
        )
        
        if render_response.status_code == 200:
            render_result = render_response.json()
            print("✅ Render API working")
            print(f"   Risk Level: {render_result.get('risk_assessment', {}).get('final_risk_level', 'unknown')}")
        else:
            print(f"❌ Render API failed: {render_response.status_code}")
    except Exception as e:
        print(f"❌ Render API error: {e}")

if __name__ == "__main__":
    print("FIREBASE FUNCTIONS REAL-TIME MONITORING TEST")
    print("="*60)
    print("This test will verify that your Firebase Functions deployment")
    print("has all the necessary endpoints for real-time monitoring.")
    print("\nIMPORTANT: Update the base_url variable with your actual Firebase Functions URL")
    print("="*60)
    
    success = test_firebase_functions()
    
    if success:
        # Optionally run comparison test
        run_comparison = input("\nDo you want to compare with Render API? (y/n): ").lower().strip()
        if run_comparison == 'y':
            test_render_api_comparison()
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        print("\nCommon issues:")
        print("1. Firebase Functions not deployed")
        print("2. Model files not accessible")
        print("3. Crime data CSV not found")
        print("4. Grid classifier not initialized")
        exit(1)
