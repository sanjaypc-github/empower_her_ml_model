import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime
import pandas as pd

class FirebaseManager:
    def __init__(self, service_account_path=None):
        """Initialize Firebase connection"""
        self.db = None
        self.is_initialized = False
        
        if service_account_path and os.path.exists(service_account_path):
            self.initialize_with_service_account(service_account_path)
        else:
            print("Warning: No Firebase service account file provided. Using default credentials.")
            self.initialize_default()
    
    def initialize_with_service_account(self, service_account_path):
        """Initialize Firebase with service account credentials"""
        try:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self.is_initialized = True
            print("Firebase initialized with service account")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            self.is_initialized = False
    
    def initialize_default(self):
        """Initialize Firebase with default credentials (for testing)"""
        try:
            # This will use default credentials if available
            firebase_admin.initialize_app()
            self.db = firestore.client()
            self.is_initialized = True
            print("Firebase initialized with default credentials")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            self.is_initialized = False
    
    def get_feedback_collection(self, collection_name='feedbacks'):
        """Get feedback collection from Firebase"""
        if not self.is_initialized:
            print("Firebase not initialized")
            return []
        
        try:
            feedbacks = []
            docs = self.db.collection(collection_name).stream()
            
            for doc in docs:
                feedback_data = doc.to_dict()
                feedback_data['id'] = doc.id
                feedbacks.append(feedback_data)
            
            return feedbacks
        except Exception as e:
            print(f"Error fetching feedbacks: {e}")
            return []
    
    def get_new_bad_feedbacks(self, collection_name='feedbacks', processed_ids=None):
        """Get new 'Bad' feedbacks that haven't been processed"""
        if processed_ids is None:
            processed_ids = set()
        
        all_feedbacks = self.get_feedback_collection(collection_name)
        new_bad_feedbacks = []
        
        for feedback in all_feedbacks:
            feedback_id = feedback.get('id')
            
            # Check if feedback is 'Bad' and hasn't been processed
            if (feedback.get('feedback') == 'Bad' and 
                feedback_id not in processed_ids):
                new_bad_feedbacks.append(feedback)
        
        return new_bad_feedbacks
    
    def mark_feedback_processed(self, feedback_id, collection_name='feedbacks'):
        """Mark a feedback as processed by adding a processed timestamp"""
        if not self.is_initialized:
            print("Firebase not initialized")
            return False
        
        try:
            doc_ref = self.db.collection(collection_name).document(feedback_id)
            doc_ref.update({
                'processed_at': datetime.now().isoformat(),
                'processed': True
            })
            return True
        except Exception as e:
            print(f"Error marking feedback as processed: {e}")
            return False
    
    def parse_feedback_suggestion(self, feedback):
        """Parse feedback suggestion to extract actionable information"""
        suggestion = feedback.get('suggestion', '')
        lat = feedback.get('lat')
        lon = feedback.get('lon')
        time = feedback.get('time')
        crime_type = feedback.get('crime_type')
        
        parsed_data = {
            'lat': lat,
            'lon': lon,
            'time': time,
            'crime_type': crime_type,
            'suggestion_text': suggestion,
            'extracted_info': {}
        }
        
        # Extract information from suggestion text
        if suggestion:
            suggestion_lower = suggestion.lower()
            
            # Extract time information
            if 'night' in suggestion_lower or 'night time' in suggestion_lower:
                parsed_data['extracted_info']['time_period'] = 'night'
            elif 'evening' in suggestion_lower:
                parsed_data['extracted_info']['time_period'] = 'evening'
            elif 'morning' in suggestion_lower:
                parsed_data['extracted_info']['time_period'] = 'morning'
            
            # Extract location information
            if 'ps' in suggestion_lower or 'police station' in suggestion_lower:
                # Extract police station name
                words = suggestion.split()
                for i, word in enumerate(words):
                    if 'ps' in word.lower() or 'police' in word.lower():
                        if i > 0:
                            parsed_data['extracted_info']['police_station'] = words[i-1]
                        break
            
            # Extract crime type if mentioned
            crime_types = [
                'sexual harassment', 'kidnapping', 'murder', 'assault',
                'chain snatching', 'robbery', 'domestic violence', 'theft',
                'burglary', 'vandalism', 'drug abuse', 'illegal gambling'
            ]
            
            for crime in crime_types:
                if crime in suggestion_lower:
                    parsed_data['extracted_info']['crime_type'] = crime
                    break
        
        return parsed_data
    
    def create_training_data_from_feedback(self, feedbacks):
        """Create training data from feedback for model retraining"""
        training_data = []
        
        for feedback in feedbacks:
            parsed = self.parse_feedback_suggestion(feedback)
            
            # Create a new data point based on feedback
            if parsed['lat'] and parsed['lon']:
                new_data_point = {
                    'Crime_ID': f"feedback_{feedback['id']}",
                    'Crime_Type': parsed['crime_type'] or parsed['extracted_info'].get('crime_type', 'Unknown'),
                    'Location': 'Feedback Location',
                    'Latitude': parsed['lat'],
                    'Longitude': parsed['lon'],
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Time': parsed['time'] or '12:00',
                    'Severity': 4,  # High severity for bad feedback
                    'Police_Station': parsed['extracted_info'].get('police_station', 'Unknown PS')
                }
                
                training_data.append(new_data_point)
        
        return pd.DataFrame(training_data) if training_data else pd.DataFrame()
    
    def test_connection(self):
        """Test Firebase connection"""
        if not self.is_initialized:
            return False
        
        try:
            # Try to access a collection
            docs = self.db.collection('test').limit(1).stream()
            list(docs)  # Consume the generator
            return True
        except Exception as e:
            print(f"Firebase connection test failed: {e}")
            return False
    
    def create_mock_feedback(self, collection_name='feedbacks'):
        """Create mock feedback data for testing"""
        if not self.is_initialized:
            print("Firebase not initialized")
            return False
        
        try:
            mock_feedback = {
                'feedback': 'Bad',
                'suggestion': 'Add Madukkarai PS at night time for Sexual Harassment',
                'lat': 10.9467,
                'lon': 76.8653,
                'time': '04:00',
                'crime_type': 'Sexual Harassment',
                'timestamp': datetime.now().isoformat(),
                'processed': False
            }
            
            doc_ref = self.db.collection(collection_name).add(mock_feedback)
            print(f"Mock feedback created with ID: {doc_ref[1].id}")
            return True
        except Exception as e:
            print(f"Error creating mock feedback: {e}")
            return False 