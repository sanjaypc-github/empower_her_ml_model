import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from datetime import datetime
import joblib
import os

class CrimeDataPreprocessor:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def extract_time_features(self, time_str):
        """Extract time-based features from time string"""
        try:
            time_obj = datetime.strptime(time_str, '%H:%M')
            hour = time_obj.hour
            minute = time_obj.minute
            
            # Create time-based features
            is_night = 1 if hour >= 22 or hour <= 6 else 0
            is_evening = 1 if 18 <= hour <= 21 else 0
            is_morning = 1 if 6 <= hour <= 11 else 0
            is_afternoon = 1 if 12 <= hour <= 17 else 0
            
            return {
                'hour': hour,
                'minute': minute,
                'is_night': is_night,
                'is_evening': is_evening,
                'is_morning': is_morning,
                'is_afternoon': is_afternoon
            }
        except:
            return {
                'hour': 12,
                'minute': 0,
                'is_night': 0,
                'is_evening': 0,
                'is_morning': 0,
                'is_afternoon': 0
            }
    
    def extract_date_features(self, date_str):
        """Extract date-based features"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_of_week = date_obj.weekday()
            month = date_obj.month
            day = date_obj.day
            
            return {
                'day_of_week': day_of_week,
                'month': month,
                'day': day,
                'is_weekend': 1 if day_of_week >= 5 else 0
            }
        except:
            return {
                'day_of_week': 0,
                'month': 1,
                'day': 1,
                'is_weekend': 0
            }
    
    def create_risk_labels(self, df):
        """Create binary risk labels based on crime severity and type"""
        # High-risk crime types
        high_risk_crimes = [
            'Sexual Harassment', 'Kidnapping', 'Murder', 'Assault', 
            'Chain Snatching', 'Robbery', 'Domestic Violence'
        ]
        
        # Create risk labels
        risk_labels = []
        for _, row in df.iterrows():
            # High severity (4-5) or high-risk crime types are considered risky
            if row['Severity'] >= 4 or row['Crime_Type'] in high_risk_crimes:
                risk_labels.append(1)  # Risky
            else:
                risk_labels.append(0)  # Safe
        
        return np.array(risk_labels)
    
    def fit_transform(self, df):
        """Fit the preprocessor and transform the data"""
        print("Preprocessing crime data...")
        
        # Create risk labels
        risk_labels = self.create_risk_labels(df)
        
        # Extract time features
        time_features = df['Time'].apply(self.extract_time_features)
        time_df = pd.DataFrame(time_features.tolist())
        
        # Extract date features
        date_features = df['Date'].apply(self.extract_date_features)
        date_df = pd.DataFrame(date_features.tolist())
        
        # Prepare features for encoding
        features_to_encode = ['Crime_Type', 'Police_Station']
        
        # Fit label encoders
        encoded_features = {}
        for feature in features_to_encode:
            if feature in df.columns:
                le = LabelEncoder()
                encoded_features[f'encoded_{feature}'] = le.fit_transform(df[feature])
                self.label_encoders[feature] = le
        
        # Combine all features
        feature_df = pd.DataFrame({
            'Latitude': df['Latitude'],
            'Longitude': df['Longitude'],
            'Severity': df['Severity']
        })
        
        # Add time features
        feature_df = pd.concat([feature_df, time_df], axis=1)
        
        # Add date features
        feature_df = pd.concat([feature_df, date_df], axis=1)
        
        # Add encoded features
        for feature_name, encoded_values in encoded_features.items():
            feature_df[feature_name] = encoded_values
        
        # Scale numerical features
        numerical_features = ['Latitude', 'Longitude', 'Severity', 'hour', 'minute', 
                           'day_of_week', 'month', 'day']
        feature_df[numerical_features] = self.scaler.fit_transform(feature_df[numerical_features])
        
        self.is_fitted = True
        
        return feature_df, risk_labels
    
    def transform(self, df):
        """Transform new data using fitted preprocessor"""
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")
        
        # Extract time features
        time_features = df['Time'].apply(self.extract_time_features)
        time_df = pd.DataFrame(time_features.tolist())
        
        # Extract date features
        date_features = df['Date'].apply(self.extract_date_features)
        date_df = pd.DataFrame(date_features.tolist())
        
        # Encode categorical features
        encoded_features = {}
        for feature, encoder in self.label_encoders.items():
            if feature in df.columns:
                # Handle unseen categories by using a default value
                try:
                    encoded_features[f'encoded_{feature}'] = encoder.transform(df[feature])
                except:
                    # For unseen categories, use the most common category
                    encoded_features[f'encoded_{feature}'] = [0] * len(df)
        
        # Combine all features
        feature_df = pd.DataFrame({
            'Latitude': df['Latitude'],
            'Longitude': df['Longitude'],
            'Severity': df['Severity']
        })
        
        # Add time features
        feature_df = pd.concat([feature_df, time_df], axis=1)
        
        # Add date features
        feature_df = pd.concat([feature_df, date_df], axis=1)
        
        # Add encoded features
        for feature_name, encoded_values in encoded_features.items():
            feature_df[feature_name] = encoded_values
        
        # Scale numerical features
        numerical_features = ['Latitude', 'Longitude', 'Severity', 'hour', 'minute', 
                           'day_of_week', 'month', 'day']
        feature_df[numerical_features] = self.scaler.transform(feature_df[numerical_features])
        
        return feature_df
    
    def save_preprocessor(self, filepath):
        """Save the fitted preprocessor"""
        preprocessor_data = {
            'label_encoders': self.label_encoders,
            'scaler': self.scaler,
            'is_fitted': self.is_fitted
        }
        joblib.dump(preprocessor_data, filepath)
        print(f"Preprocessor saved to {filepath}")
    
    def load_preprocessor(self, filepath):
        """Load a fitted preprocessor"""
        if os.path.exists(filepath):
            preprocessor_data = joblib.load(filepath)
            self.label_encoders = preprocessor_data['label_encoders']
            self.scaler = preprocessor_data['scaler']
            self.is_fitted = preprocessor_data['is_fitted']
            print(f"Preprocessor loaded from {filepath}")
        else:
            print(f"Preprocessor file not found at {filepath}")
    
    def get_feature_names(self):
        """Get the names of all features used in the model"""
        base_features = ['Latitude', 'Longitude', 'Severity']
        time_features = ['hour', 'minute', 'is_night', 'is_evening', 'is_morning', 'is_afternoon']
        date_features = ['day_of_week', 'month', 'day', 'is_weekend']
        encoded_features = [f'encoded_{feature}' for feature in self.label_encoders.keys()]
        
        return base_features + time_features + date_features + encoded_features 