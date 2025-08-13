import functions_framework
from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
import tempfile
import zipfile

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.preprocess import CrimeDataPreprocessor
from utils.grid_classifier import GridClassifier

# Global variables for model and preprocessor
model = None
preprocessor = None
grid_classifier = None

def load_model_and_preprocessor():
    """Load the trained model and preprocessor"""
    global model, preprocessor, grid_classifier
    
    try:
        # Load model from Firebase Storage or bundled with function
        model_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'crime_predictor.pkl')
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            print(f"Model loaded from {model_path}")
        else:
            print(f"Model file not found at {model_path}")
            model = None
        
        # Load preprocessor
        preprocessor_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'preprocessor.pkl')
        preprocessor = CrimeDataPreprocessor()
        if os.path.exists(preprocessor_path):
            preprocessor.load_preprocessor(preprocessor_path)
            print(f"Preprocessor loaded from {preprocessor_path}")
        else:
            print(f"Preprocessor file not found at {preprocessor_path}")
            preprocessor = None
        
        # Initialize grid classifier
        try:
            # Load crime data for grid classification
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'crime_data.csv')
            if os.path.exists(data_path):
                crime_data = pd.read_csv(data_path)
                grid_classifier = GridClassifier(grid_size=0.01)  # 1.1 km grids
                grid_summary = grid_classifier.create_grid(crime_data)
                print(f"Grid classifier initialized with {grid_summary['total_grids']} grids")
                print(f"High risk zones: {grid_summary['high_risk_grids']}")
                print(f"Medium risk zones: {grid_summary['medium_risk_grids']}")
                print(f"Low risk zones: {grid_summary['low_risk_grids']}")
            else:
                print(f"Crime data not found at {data_path}")
                grid_classifier = None
        except Exception as e:
            print(f"Error initializing grid classifier: {e}")
            grid_classifier = None
            
    except Exception as e:
        print(f"Error loading model and preprocessor: {e}")
        model = None
        preprocessor = None
        grid_classifier = None

@functions_framework.http
def predict_safety(request):
    """Firebase Cloud Function for safety prediction"""
    # Set CORS headers
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    try:
        # Load model if not loaded
        if model is None or preprocessor is None:
            load_model_and_preprocessor()
        
        # Get request data
        request_json = request.get_json(silent=True)
        
        if not request_json:
            return (jsonify({'error': 'No data provided'}), 400, headers)
        
        # Extract required fields
        required_fields = ['latitude', 'longitude', 'time', 'severity', 'crime_type']
        missing_fields = [field for field in required_fields if field not in request_json]
        
        if missing_fields:
            return (jsonify({
                'error': f'Missing required fields: {missing_fields}'
            }), 400, headers)
        
        # Validate data types
        try:
            lat = float(request_json['latitude'])
            lon = float(request_json['longitude'])
            severity = int(request_json['severity'])
            time = str(request_json['time'])
            crime_type = str(request_json['crime_type'])
        except (ValueError, TypeError) as e:
            return (jsonify({'error': f'Invalid data types: {str(e)}'}), 400, headers)
        
        # Validate ranges
        if not (-90 <= lat <= 90):
            return (jsonify({'error': 'Latitude must be between -90 and 90'}), 400, headers)
        
        if not (-180 <= lon <= 180):
            return (jsonify({'error': 'Longitude must be between -180 and 180'}), 400, headers)
        
        if not (1 <= severity <= 5):
            return (jsonify({'error': 'Severity must be between 1 and 5'}), 400, headers)
        
        # Check if model and preprocessor are loaded
        if model is None or preprocessor is None or not preprocessor.is_fitted:
            return (jsonify({
                'error': 'Model or preprocessor not loaded. Please ensure the model is trained.'
            }), 500, headers)
        
        # Create input DataFrame
        input_data = pd.DataFrame([{
            'Crime_ID': 'prediction_request',
            'Crime_Type': crime_type,
            'Location': 'Prediction Location',
            'Latitude': lat,
            'Longitude': lon,
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Time': time,
            'Severity': severity,
            'Police_Station': 'Unknown PS'
        }])
        
        # Preprocess input data
        features = preprocessor.transform(input_data)
        
        # Make prediction
        prediction = model.predict(features)[0]
        prediction_proba = model.predict_proba(features)[0]
        
        # Get confidence score
        confidence = max(prediction_proba)
        
        # Determine safety status
        safety_status = 'safe' if prediction == 0 else 'risky'
        
        # Create response
        response = {
            'prediction': safety_status,
            'confidence': round(confidence, 3),
            'risk_score': round(prediction_proba[1], 3),  # Probability of being risky
            'safe_score': round(prediction_proba[0], 3),  # Probability of being safe
            'input_data': {
                'latitude': lat,
                'longitude': lon,
                'time': time,
                'severity': severity,
                'crime_type': crime_type
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return (jsonify(response), 200, headers)
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return (jsonify({'error': f'Prediction failed: {str(e)}'}), 500, headers)

@functions_framework.http
def live_safety_check(request):
    """
    Real-time safety check for live location tracking
    Provides instant notification based on current location
    """
    # Set CORS headers
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    try:
        # Load model if not loaded
        if model is None or preprocessor is None:
            load_model_and_preprocessor()
        
        # Get request data
        data = request.get_json(silent=True)
        
        if not data:
            return (jsonify({'error': 'No data provided'}), 400, headers)
        
        # Required fields
        if 'latitude' not in data or 'longitude' not in data:
            return (jsonify({'error': 'latitude and longitude are required'}), 400, headers)
        
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        
        # Optional parameters with defaults
        current_time = data.get('time', datetime.now().strftime('%H:%M'))
        severity = int(data.get('severity', 3))  # Default medium severity
        crime_type = data.get('crime_type', 'General Safety')  # Default type
        user_id = data.get('user_id', 'anonymous')  # For tracking multiple users
        
        # Check if models are loaded
        if model is None or preprocessor is None:
            return (jsonify({'error': 'ML model not loaded'}), 500, headers)
        
        # 1. GRID-BASED RISK ASSESSMENT
        grid_risk = None
        if grid_classifier is not None:
            grid_result = grid_classifier.check_location_in_grid(lat, lon)
            grid_risk = grid_result.get('risk_zone', 'unknown')
        
        # 2. ML MODEL PREDICTION
        input_data = pd.DataFrame([{
            'Crime_ID': f'live_check_{user_id}',
            'Crime_Type': crime_type,
            'Location': 'Live Location',
            'Latitude': lat,
            'Longitude': lon,
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Time': current_time,
            'Severity': severity,
            'Police_Station': 'Unknown PS'
        }])
        
        features = preprocessor.transform(input_data)
        ml_prediction = model.predict(features)[0]
        ml_proba = model.predict_proba(features)[0]
        ml_safety = 'safe' if ml_prediction == 0 else 'risky'
        
        # 3. COMBINED RISK ASSESSMENT
        final_risk_level, notification_text, alert_color = _generate_live_notification(
            grid_risk, ml_safety, ml_proba, current_time, lat, lon
        )
        
        # 4. SAFETY RECOMMENDATIONS
        recommendations = _get_safety_recommendations(final_risk_level, current_time)
        
        response = {
            'user_id': user_id,
            'location': {
                'latitude': lat,
                'longitude': lon,
                'timestamp': datetime.now().isoformat()
            },
            'risk_assessment': {
                'grid_risk': grid_risk,
                'ml_prediction': ml_safety,
                'ml_confidence': round(max(ml_proba), 3),
                'final_risk_level': final_risk_level
            },
            'notification': {
                'message': notification_text,
                'alert_color': alert_color,
                'should_notify': final_risk_level in ['high', 'critical']
            },
            'safety_recommendations': recommendations,
            'detailed_scores': {
                'risk_score': round(ml_proba[1], 3),
                'safe_score': round(ml_proba[0], 3)
            }
        }
        
        return (jsonify(response), 200, headers)
        
    except Exception as e:
        print(f"Error in live safety check: {e}")
        return (jsonify({'error': f'Live safety check failed: {str(e)}'}), 500, headers)

@functions_framework.http
def track_user_journey(request):
    """
    Track a user's journey with multiple location points
    For continuous location monitoring
    """
    # Set CORS headers
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    try:
        # Load model if not loaded
        if grid_classifier is None:
            load_model_and_preprocessor()
        
        # Get request data
        data = request.get_json(silent=True)
        
        if not data or 'locations' not in data:
            return (jsonify({'error': 'locations array is required'}), 400, headers)
        
        locations = data['locations']
        user_id = data.get('user_id', 'anonymous')
        
        journey_analysis = []
        alerts = []
        
        for i, location in enumerate(locations):
            lat = float(location['latitude'])
            lon = float(location['longitude'])
            timestamp = location.get('timestamp', datetime.now().isoformat())
            
            # Quick safety check for each location
            if grid_classifier is not None:
                grid_result = grid_classifier.check_location_in_grid(lat, lon)
                risk_zone = grid_result.get('risk_zone', 'unknown')
                
                location_analysis = {
                    'point_index': i,
                    'location': {'latitude': lat, 'longitude': lon},
                    'timestamp': timestamp,
                    'risk_zone': risk_zone
                }
                
                journey_analysis.append(location_analysis)
                
                # Generate alerts for high-risk areas
                if risk_zone == 'high_risk':
                    alerts.append({
                        'point_index': i,
                        'alert_type': 'high_risk_area',
                        'message': f"High risk area detected at point {i+1}",
                        'location': {'latitude': lat, 'longitude': lon}
                    })
        
        return (jsonify({
            'user_id': user_id,
            'journey_summary': {
                'total_points': len(locations),
                'high_risk_points': len([p for p in journey_analysis if p['risk_zone'] == 'high_risk']),
                'medium_risk_points': len([p for p in journey_analysis if p['risk_zone'] == 'medium_risk']),
                'safe_points': len([p for p in journey_analysis if p['risk_zone'] == 'low_risk'])
            },
            'alerts': alerts,
            'journey_analysis': journey_analysis,
            'timestamp': datetime.now().isoformat()
        }), 200, headers)
        
    except Exception as e:
        print(f"Error in user journey tracking: {e}")
        return (jsonify({'error': f'Journey tracking failed: {str(e)}'}), 500, headers)

@functions_framework.http
def check_grid_zone(request):
    """Check which risk zone a location falls into"""
    # Set CORS headers
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    try:
        # Load model if not loaded
        if grid_classifier is None:
            load_model_and_preprocessor()
        
        data = request.get_json(silent=True)
        
        if not data:
            return (jsonify({'error': 'No data provided'}), 400, headers)
        
        if 'latitude' not in data or 'longitude' not in data:
            return (jsonify({'error': 'latitude and longitude are required'}), 400, headers)
        
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        
        if grid_classifier is None:
            return (jsonify({'error': 'Grid classifier not loaded'}), 500, headers)
        
        result = grid_classifier.check_location_in_grid(lat, lon)
        
        return (jsonify({
            'grid_analysis': result,
            'timestamp': datetime.now().isoformat()
        }), 200, headers)
        
    except Exception as e:
        print(f"Error in grid zone check: {e}")
        return (jsonify({'error': f'Grid zone check failed: {str(e)}'}), 500, headers)

@functions_framework.http
def nearby_risk_zones(request):
    """Get risk zones within a certain radius"""
    # Set CORS headers
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    try:
        # Load model if not loaded
        if grid_classifier is None:
            load_model_and_preprocessor()
        
        data = request.get_json(silent=True)
        
        if not data:
            return (jsonify({'error': 'No data provided'}), 400, headers)
        
        if 'latitude' not in data or 'longitude' not in data:
            return (jsonify({'error': 'latitude and longitude are required'}), 400, headers)
        
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        radius = float(data.get('radius_km', 2))  # Default 2km radius
        
        if grid_classifier is None:
            return (jsonify({'error': 'Grid classifier not loaded'}), 500, headers)
        
        result = grid_classifier.get_nearby_risk_zones(lat, lon, radius)
        
        return (jsonify({
            'nearby_analysis': result,
            'timestamp': datetime.now().isoformat()
        }), 200, headers)
        
    except Exception as e:
        print(f"Error in nearby risk zones: {e}")
        return (jsonify({'error': f'Nearby risk zones failed: {str(e)}'}), 500, headers)

@functions_framework.http
def grid_summary(request):
    """Get summary of grid classification"""
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    try:
        # Load model if not loaded
        if grid_classifier is None:
            load_model_and_preprocessor()
        
        if grid_classifier is None:
            return (jsonify({'error': 'Grid classifier not loaded'}), 500, headers)
        
        summary = grid_classifier._get_grid_summary()
        
        return (jsonify({
            'grid_summary': summary,
            'timestamp': datetime.now().isoformat()
        }), 200, headers)
        
    except Exception as e:
        print(f"Error getting grid summary: {e}")
        return (jsonify({'error': f'Grid summary failed: {str(e)}'}), 500, headers)

@functions_framework.http
def health_check(request):
    """Health check endpoint"""
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    if model is None or preprocessor is None or grid_classifier is None:
        load_model_and_preprocessor()
    
    return (jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'preprocessor_loaded': preprocessor is not None and preprocessor.is_fitted,
        'grid_classifier_loaded': grid_classifier is not None,
        'timestamp': datetime.now().isoformat()
    }), 200, headers) 

def _generate_live_notification(grid_risk, ml_safety, ml_proba, current_time, lat, lon):
    """Generate notification text based on combined risk assessment"""
    
    # Time-based risk factor
    hour = int(current_time.split(':')[0])
    is_night = hour >= 22 or hour <= 6
    is_late_evening = 18 <= hour <= 21
    
    # Combined risk assessment
    if grid_risk == 'high_risk' and ml_safety == 'risky':
        risk_level = 'critical'
        if is_night:
            notification = "🚨 CRITICAL ALERT: You're in a high-risk area during night hours. Consider leaving immediately or finding a safe location."
        else:
            notification = "⚠️ HIGH RISK ZONE: You're currently in a dangerous area. Stay alert and consider moving to a safer location."
        color = 'red'
        
    elif grid_risk == 'high_risk' or ml_safety == 'risky':
        risk_level = 'high'
        if is_night:
            notification = "⚠️ CAUTION: Elevated risk detected during night hours. Stay vigilant and avoid isolated areas."
        else:
            notification = "⚠️ CAUTION: You're in an area with elevated safety concerns. Stay alert."
        color = 'orange'
        
    elif grid_risk == 'medium_risk' and (is_night or is_late_evening):
        risk_level = 'medium'
        notification = "📍 ADVISORY: Medium risk area during evening/night. Stay with groups if possible."
        color = 'yellow'
        
    elif grid_risk == 'medium_risk':
        risk_level = 'low'
        notification = "📍 Safe area, but stay aware of your surroundings."
        color = 'green'
        
    else:  # Low risk or safe
        risk_level = 'safe'
        if is_night:
            notification = "✅ Safe area, but take standard night-time precautions."
        else:
            notification = "✅ You're in a safe area. Enjoy your time!"
        color = 'green'
    
    return risk_level, notification, color

def _get_safety_recommendations(risk_level, current_time):
    """Get contextual safety recommendations"""
    
    hour = int(current_time.split(':')[0])
    is_night = hour >= 22 or hour <= 6
    
    base_recommendations = [
        "Keep your phone charged and accessible",
        "Share your location with trusted contacts",
        "Stay in well-lit, populated areas"
    ]
    
    if risk_level == 'critical':
        return base_recommendations + [
            "Leave the area immediately if possible",
            "Call emergency services if you feel threatened",
            "Find the nearest police station or safe building",
            "Avoid walking alone"
        ]
    elif risk_level == 'high':
        return base_recommendations + [
            "Consider changing your route",
            "Stay with groups if possible",
            "Avoid displaying valuables",
            "Trust your instincts"
        ]
    elif risk_level == 'medium':
        return base_recommendations + [
            "Be extra vigilant",
            "Avoid shortcuts through isolated areas"
        ]
    else:
        if is_night:
            return base_recommendations + [
                "Take standard night-time precautions"
            ]
        else:
            return [
                "Enjoy your time while staying aware",
                "Standard safety practices apply"
            ] 