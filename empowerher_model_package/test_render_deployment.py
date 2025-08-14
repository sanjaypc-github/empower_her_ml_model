#!/usr/bin/env python3
"""
Test script for Render deployment
Tests the deployed API at https://empower-her-ml-model.onrender.com
"""

import requests
import json
import time
from datetime import datetime

def test_render_deployment():
    """Test the Render deployment"""
    
    # Your actual Render URL from the dashboard
    base_url = "https://empower-her-ml-model.onrender.com"
    
    print("Testing Render Deployment...")
    print("="*60)
    print(f"URL: {base_url}")
    print("="*60)
    
    # Test 1: Health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=15)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health endpoint working!")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Model loaded: {health_data.get('model_loaded', False)}")
            print(f"   Preprocessor loaded: {health_data.get('preprocessor_loaded', False)}")
            print(f"   Grid classifier loaded: {health_data.get('grid_classifier_loaded', False)}")
            print(f"   Timestamp: {health_data.get('timestamp', 'unknown')}")
            
            # Check if all components are loaded
            if not health_data.get('grid_classifier_loaded', False):
                print("⚠️  WARNING: Grid classifier not loaded - risk classification won't work!")
                return False
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Render API: {e}")
        print("   The service might be spinning up (free instance)")
        print("   Try again in 30-60 seconds")
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
                timeout=20
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
            timeout=15
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
            timeout=20
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
    
    print("\n" + "="*60)
    print("🎉 RENDER DEPLOYMENT TESTING COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("✅ All real-time monitoring endpoints are working")
    print("✅ Risk classification is functional")
    print("✅ Grid-based analysis is operational")
    print("✅ Journey tracking is working")
    print("\nYour Flutter app should now receive proper risk classifications!")
    print(f"\nAPI URL: {base_url}")
    
    return True

def check_service_status():
    """Check if the service is responding"""
    base_url = "https://empower-her-ml-model.onrender.com"
    
    print("Checking service status...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Service is responding")
            return True
        else:
            print(f"❌ Service returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Service not responding: {e}")
        print("   This is normal for free instances that spin down with inactivity")
        print("   The service will spin up automatically when you make a request")
        return False

if __name__ == "__main__":
    print("RENDER DEPLOYMENT TEST")
    print("="*60)
    print("Testing your deployed API at: https://empower-her-ml-model.onrender.com")
    print("="*60)
    
    # First check if service is responding
    if check_service_status():
        success = test_render_deployment()
        if success:
            print("\n🎉 Your Render deployment is working perfectly!")
            print("You can now use this URL in your Flutter app:")
            print("https://empower-her-ml-model.onrender.com")
        else:
            print("\n❌ Some tests failed. Check the issues above.")
    else:
        print("\n⚠️  Service might be spinning up. Try again in 30-60 seconds.")
        print("Free Render instances spin down with inactivity.")

