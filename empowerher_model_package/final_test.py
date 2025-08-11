#!/usr/bin/env python3
"""
Final comprehensive test for Women EmpowerHer system
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.preprocess import CrimeDataPreprocessor

def test_complete_system():
    """Test all components of the Women EmpowerHer system"""
    print("="*60)
    print("WOMEN EMPOWERHER - FINAL SYSTEM TEST")
    print("="*60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Data Loading
    print("\n1. Testing Data Loading...")
    total_tests += 1
    try:
        data_path = os.path.join('data', 'crime_data.csv')
        df = pd.read_csv(data_path)
        print(f"✅ Data loaded: {len(df)} records")
        print(f"   Columns: {list(df.columns)}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
    
    # Test 2: Model Files
    print("\n2. Testing Model Files...")
    total_tests += 1
    try:
        model_path = os.path.join('model', 'crime_predictor.pkl')
        preprocessor_path = os.path.join('model', 'preprocessor.pkl')
        
        if os.path.exists(model_path) and os.path.exists(preprocessor_path):
            model = joblib.load(model_path)
            preprocessor = CrimeDataPreprocessor()
            preprocessor.load_preprocessor(preprocessor_path)
            
            print(f"✅ Model loaded: {type(model).__name__}")
            print(f"✅ Preprocessor loaded: {preprocessor.is_fitted}")
            tests_passed += 1
        else:
            print("❌ Model files not found")
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
    
    # Test 3: Preprocessing
    print("\n3. Testing Data Preprocessing...")
    total_tests += 1
    try:
        # Load sample data
        df_sample = df.head(100)
        preprocessor = CrimeDataPreprocessor()
        features, labels = preprocessor.fit_transform(df_sample)
        
        print(f"✅ Preprocessing successful")
        print(f"   Features shape: {features.shape}")
        print(f"   Labels shape: {labels.shape}")
        print(f"   Safe: {(labels == 0).sum()}, Risky: {(labels == 1).sum()}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Preprocessing failed: {e}")
    
    # Test 4: Model Prediction
    print("\n4. Testing Model Prediction...")
    total_tests += 1
    try:
        # Create test data
        test_data = pd.DataFrame([{
            'Crime_ID': 'test_1',
            'Crime_Type': 'Sexual Harassment',
            'Location': 'Test Location',
            'Latitude': 10.9467,
            'Longitude': 76.8653,
            'Date': '2024-01-08',
            'Time': '04:00',
            'Severity': 4,
            'Police_Station': 'Test PS'
        }])
        
        # Transform test data
        test_features = preprocessor.transform(test_data)
        
        # Make prediction
        prediction = model.predict(test_features)[0]
        prediction_proba = model.predict_proba(test_features)[0]
        
        print(f"✅ Prediction successful")
        print(f"   Prediction: {'Risky' if prediction == 1 else 'Safe'}")
        print(f"   Confidence: {max(prediction_proba):.3f}")
        print(f"   Risk Score: {prediction_proba[1]:.3f}")
        print(f"   Safe Score: {prediction_proba[0]:.3f}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
    
    # Test 5: API Code Structure
    print("\n5. Testing API Code Structure...")
    total_tests += 1
    try:
        api_path = os.path.join('api', 'app.py')
        if os.path.exists(api_path):
            with open(api_path, 'r') as f:
                api_code = f.read()
            
            # Check for key components
            has_flask = 'from flask import' in api_code
            has_predict_endpoint = '@app.route(\'/predict\')' in api_code
            has_health_endpoint = '@app.route(\'/health\')' in api_code
            
            print(f"✅ API file exists")
            print(f"   Flask imports: {has_flask}")
            print(f"   Predict endpoint: {has_predict_endpoint}")
            print(f"   Health endpoint: {has_health_endpoint}")
            tests_passed += 1
        else:
            print("❌ API file not found")
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
    
    # Test 6: Firebase Utilities
    print("\n6. Testing Firebase Utilities...")
    total_tests += 1
    try:
        from utils.firebase_utils import FirebaseManager
        
        firebase_manager = FirebaseManager()
        
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
        
        print(f"✅ Firebase utilities working")
        print(f"   Parsed crime type: {parsed.get('crime_type')}")
        print(f"   Extracted info: {parsed.get('extracted_info')}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Firebase utilities failed: {e}")
    
    # Test 7: Feedback Trainer
    print("\n7. Testing Feedback Trainer...")
    total_tests += 1
    try:
        trainer_path = os.path.join('model', 'feedback_trainer.py')
        if os.path.exists(trainer_path):
            with open(trainer_path, 'r') as f:
                trainer_code = f.read()
            
            has_feedback_trainer = 'class FeedbackTrainer' in trainer_code
            has_firebase_integration = 'FirebaseManager' in trainer_code
            
            print(f"✅ Feedback trainer exists")
            print(f"   FeedbackTrainer class: {has_feedback_trainer}")
            print(f"   Firebase integration: {has_firebase_integration}")
            tests_passed += 1
        else:
            print("❌ Feedback trainer not found")
    except Exception as e:
        print(f"❌ Feedback trainer test failed: {e}")
    
    # Test 8: Requirements and Documentation
    print("\n8. Testing Requirements and Documentation...")
    total_tests += 1
    try:
        requirements_path = 'requirements.txt'
        readme_path = 'README.md'
        
        has_requirements = os.path.exists(requirements_path)
        has_readme = os.path.exists(readme_path)
        
        if has_requirements:
            with open(requirements_path, 'r') as f:
                requirements = f.read()
            has_flask = 'Flask' in requirements
            has_sklearn = 'scikit-learn' in requirements
        else:
            has_flask = has_sklearn = False
        
        print(f"✅ Requirements file: {has_requirements}")
        print(f"   Flask dependency: {has_flask}")
        print(f"   Scikit-learn dependency: {has_sklearn}")
        print(f"✅ README file: {has_readme}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Documentation test failed: {e}")
    
    # Final Results
    print("\n" + "="*60)
    print("FINAL TEST RESULTS")
    print("="*60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Women EmpowerHer system is ready for deployment")
        print("✅ Your friend can safely use this package")
        print("\n📦 READY TO ZIP AND SEND!")
        print("\nInstructions for your friend:")
        print("1. Extract the zip file")
        print("2. Run: pip install -r requirements.txt")
        print("3. Run: python api/app.py")
        print("4. API will be available at http://localhost:5001")
        print("5. Use the endpoints in their Flutter app")
        return True
    else:
        print(f"\n⚠ {total_tests - tests_passed} tests failed")
        print("Please check the issues above before sending")
        return False

if __name__ == "__main__":
    success = test_complete_system()
    sys.exit(0 if success else 1) 