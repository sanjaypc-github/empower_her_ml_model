import os
import sys
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.firebase_utils import FirebaseManager
from utils.preprocess import CrimeDataPreprocessor

class FeedbackTrainer:
    def __init__(self, model_path='crime_predictor.pkl', preprocessor_path='preprocessor.pkl'):
        """Initialize the feedback trainer"""
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.model = None
        self.preprocessor = None
        self.firebase_manager = None
        self.processed_feedback_ids = set()
        
        # Load existing model and preprocessor
        self.load_model()
        self.load_preprocessor()
        
        # Initialize Firebase connection
        self.initialize_firebase()
    
    def initialize_firebase(self, service_account_path=None):
        """Initialize Firebase connection"""
        try:
            self.firebase_manager = FirebaseManager(service_account_path)
            if self.firebase_manager.test_connection():
                print("Firebase connection established successfully")
            else:
                print("Warning: Firebase connection test failed")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
    
    def load_model(self):
        """Load the trained model"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print(f"Model loaded from {self.model_path}")
            else:
                print(f"Model file not found at {self.model_path}")
                self.model = None
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def load_preprocessor(self):
        """Load the fitted preprocessor"""
        try:
            self.preprocessor = CrimeDataPreprocessor()
            if os.path.exists(self.preprocessor_path):
                self.preprocessor.load_preprocessor(self.preprocessor_path)
                print(f"Preprocessor loaded from {self.preprocessor_path}")
            else:
                print(f"Preprocessor file not found at {self.preprocessor_path}")
        except Exception as e:
            print(f"Error loading preprocessor: {e}")
    
    def save_model(self):
        """Save the updated model"""
        try:
            if self.model is not None:
                joblib.dump(self.model, self.model_path)
                print(f"Model saved to {self.model_path}")
                return True
            else:
                print("No model to save")
                return False
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def save_preprocessor(self):
        """Save the updated preprocessor"""
        try:
            if self.preprocessor is not None:
                self.preprocessor.save_preprocessor(self.preprocessor_path)
                return True
            else:
                print("No preprocessor to save")
                return False
        except Exception as e:
            print(f"Error saving preprocessor: {e}")
            return False
    
    def get_new_feedbacks(self):
        """Get new 'Bad' feedbacks from Firebase"""
        if not self.firebase_manager or not self.firebase_manager.is_initialized:
            print("Firebase not initialized")
            return []
        
        try:
            new_feedbacks = self.firebase_manager.get_new_bad_feedbacks(
                processed_ids=self.processed_feedback_ids
            )
            print(f"Found {len(new_feedbacks)} new bad feedbacks")
            return new_feedbacks
        except Exception as e:
            print(f"Error getting new feedbacks: {e}")
            return []
    
    def process_feedback(self, feedback):
        """Process a single feedback and update model if needed"""
        feedback_id = feedback.get('id')
        
        if feedback.get('feedback') != 'Bad':
            return False
        
        print(f"Processing feedback ID: {feedback_id}")
        
        # Parse feedback suggestion
        parsed_data = self.firebase_manager.parse_feedback_suggestion(feedback)
        
        # Create training data from feedback
        feedback_df = self.firebase_manager.create_training_data_from_feedback([feedback])
        
        if feedback_df.empty:
            print("No valid training data created from feedback")
            return False
        
        # Update model with new data
        success = self.update_model_with_feedback(feedback_df)
        
        if success:
            # Mark feedback as processed
            self.firebase_manager.mark_feedback_processed(feedback_id)
            self.processed_feedback_ids.add(feedback_id)
            print(f"Feedback {feedback_id} processed successfully")
            return True
        else:
            print(f"Failed to process feedback {feedback_id}")
            return False
    
    def update_model_with_feedback(self, new_data_df):
        """Update the model with new feedback data"""
        try:
            if self.model is None or self.preprocessor is None:
                print("Model or preprocessor not loaded")
                return False
            
            # Preprocess new data
            if not self.preprocessor.is_fitted:
                print("Preprocessor not fitted. Cannot process new data.")
                return False
            
            # Transform new data
            new_features = self.preprocessor.transform(new_data_df)
            
            # Create labels for new data (all risky since they're from 'Bad' feedback)
            new_labels = np.ones(len(new_features))
            
            # Perform partial fit for incremental learning
            if hasattr(self.model, 'partial_fit'):
                # For models that support partial_fit (like SGDClassifier)
                self.model.partial_fit(new_features, new_labels, classes=[0, 1])
                print("Model updated using partial_fit")
            else:
                # For models that don't support partial_fit, we need to retrain
                print("Model doesn't support partial_fit. Retraining required.")
                return self.retrain_model_with_feedback(new_data_df)
            
            # Save updated model
            self.save_model()
            return True
            
        except Exception as e:
            print(f"Error updating model with feedback: {e}")
            return False
    
    def retrain_model_with_feedback(self, new_data_df):
        """Retrain the entire model with original data plus feedback data"""
        try:
            # Load original training data
            original_data_path = os.path.join(os.path.dirname(self.model_path), '..', 'data', 'crime_data.csv')
            
            if not os.path.exists(original_data_path):
                print("Original training data not found")
                return False
            
            # Load original data
            original_df = pd.read_csv(original_data_path)
            
            # Combine original data with feedback data
            combined_df = pd.concat([original_df, new_data_df], ignore_index=True)
            
            # Create new preprocessor and fit on combined data
            new_preprocessor = CrimeDataPreprocessor()
            features, labels = new_preprocessor.fit_transform(combined_df)
            
            # Retrain model
            from sklearn.ensemble import RandomForestClassifier
            new_model = RandomForestClassifier(n_estimators=100, random_state=42)
            new_model.fit(features, labels)
            
            # Update model and preprocessor
            self.model = new_model
            self.preprocessor = new_preprocessor
            
            # Save updated model and preprocessor
            self.save_model()
            self.save_preprocessor()
            
            print("Model retrained successfully with feedback data")
            return True
            
        except Exception as e:
            print(f"Error retraining model: {e}")
            return False
    
    def run_feedback_loop(self, interval_seconds=300):
        """Run continuous feedback processing loop"""
        import time
        
        print("Starting feedback processing loop...")
        print(f"Checking for new feedbacks every {interval_seconds} seconds")
        
        try:
            while True:
                # Get new feedbacks
                new_feedbacks = self.get_new_feedbacks()
                
                if new_feedbacks:
                    print(f"Processing {len(new_feedbacks)} new feedbacks...")
                    
                    for feedback in new_feedbacks:
                        self.process_feedback(feedback)
                    
                    print("Feedback processing completed")
                else:
                    print("No new feedbacks found")
                
                # Wait before next check
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("Feedback processing loop stopped by user")
        except Exception as e:
            print(f"Error in feedback loop: {e}")
    
    def test_feedback_processing(self):
        """Test feedback processing with mock data"""
        if not self.firebase_manager or not self.firebase_manager.is_initialized:
            print("Firebase not initialized. Cannot test feedback processing.")
            return False
        
        try:
            # Create mock feedback
            success = self.firebase_manager.create_mock_feedback()
            
            if success:
                # Get the mock feedback
                feedbacks = self.firebase_manager.get_new_bad_feedbacks()
                
                if feedbacks:
                    # Process the mock feedback
                    result = self.process_feedback(feedbacks[0])
                    print(f"Test feedback processing result: {result}")
                    return result
                else:
                    print("No mock feedback found")
                    return False
            else:
                print("Failed to create mock feedback")
                return False
                
        except Exception as e:
            print(f"Error in test feedback processing: {e}")
            return False

if __name__ == "__main__":
    # Example usage
    trainer = FeedbackTrainer()
    
    # Test feedback processing
    print("Testing feedback processing...")
    trainer.test_feedback_processing()
    
    # Run feedback loop (uncomment to run continuously)
    # trainer.run_feedback_loop() 