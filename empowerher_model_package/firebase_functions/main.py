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

# Global variables for model and preprocessor
model = None
preprocessor = None

def load_model_and_preprocessor():
    """Load the trained model and preprocessor"""
    global model, preprocessor
    
    try:
        # Load model from Firebase Storage or bundled with function
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'crime_predictor.pkl')
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            print(f"Model loaded from {model_path}")
        else:
            print(f"Model file not found at {model_path}")
            model = None
        
        # Load preprocessor
        preprocessor_path = os.path.join(os.path.dirname(__file__), 'model', 'preprocessor.pkl')
        preprocessor = CrimeDataPreprocessor()
        if os.path.exists(preprocessor_path):
            preprocessor.load_preprocessor(preprocessor_path)
            print(f"Preprocessor loaded from {preprocessor_path}")
        else:
            print(f"Preprocessor file not found at {preprocessor_path}")
            preprocessor = None
            
    except Exception as e:
        print(f"Error loading model and preprocessor: {e}")
        model = None
        preprocessor = None

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
def health_check(request):
    """Health check endpoint"""
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    
    if model is None or preprocessor is None:
        load_model_and_preprocessor()
    
    return (jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'preprocessor_loaded': preprocessor is not None and preprocessor.is_fitted,
        'timestamp': datetime.now().isoformat()
    }), 200, headers) 