import pandas as pd
import numpy as np
import joblib
import os
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.preprocess import CrimeDataPreprocessor

def load_data(data_path):
    """Load crime data from CSV file"""
    try:
        print(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        print(f"Loaded {len(df)} records")
        print(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def train_model(X_train, y_train, model_type='random_forest'):
    """Train the machine learning model"""
    if model_type == 'random_forest':
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    print(f"Training {model_type} model...")
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """Evaluate the trained model"""
    print("\n" + "="*50)
    print("MODEL EVALUATION")
    print("="*50)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Accuracy Percentage: {accuracy * 100:.2f}%")
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Safe', 'Risky']))
    
    # Confusion matrix
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print("Predicted:")
    print("         Safe  Risky")
    print(f"Actual Safe   {cm[0,0]:4d}  {cm[0,1]:4d}")
    print(f"      Risky   {cm[1,0]:4d}  {cm[1,1]:4d}")
    
    # Cross-validation score
    cv_scores = cross_val_score(model, X_test, y_test, cv=5)
    print(f"\nCross-validation scores: {cv_scores}")
    print(f"CV Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    return {
        'accuracy': accuracy,
        'classification_report': classification_report(y_test, y_pred, output_dict=True),
        'confusion_matrix': cm.tolist(),
        'cv_scores': cv_scores.tolist(),
        'cv_mean': cv_scores.mean(),
        'cv_std': cv_scores.std()
    }

def save_model_and_preprocessor(model, preprocessor, model_path, preprocessor_path):
    """Save the trained model and preprocessor"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save model
        joblib.dump(model, model_path)
        print(f"Model saved to {model_path}")
        
        # Save preprocessor
        preprocessor.save_preprocessor(preprocessor_path)
        print(f"Preprocessor saved to {preprocessor_path}")
        
        return True
    except Exception as e:
        print(f"Error saving model and preprocessor: {e}")
        return False

def analyze_data(df):
    """Analyze the crime data"""
    print("\n" + "="*50)
    print("DATA ANALYSIS")
    print("="*50)
    
    print(f"Total records: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Crime type distribution
    print("\nCrime Type Distribution:")
    crime_counts = df['Crime_Type'].value_counts()
    print(crime_counts.head(10))
    
    # Severity distribution
    print("\nSeverity Distribution:")
    severity_counts = df['Severity'].value_counts().sort_index()
    print(severity_counts)
    
    # Time analysis
    print("\nTime Analysis:")
    df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M').dt.hour
    hour_counts = df['Hour'].value_counts().sort_index()
    print("Crimes by hour:")
    for hour, count in hour_counts.items():
        print(f"  {hour:02d}:00 - {count:4d} crimes")
    
    # Location analysis
    print("\nTop 10 Police Stations:")
    station_counts = df['Police_Station'].value_counts().head(10)
    print(station_counts)
    
    # Risk analysis
    preprocessor = CrimeDataPreprocessor()
    risk_labels = preprocessor.create_risk_labels(df)
    safe_count = (risk_labels == 0).sum()
    risky_count = (risk_labels == 1).sum()
    
    print(f"\nRisk Distribution:")
    print(f"  Safe locations: {safe_count} ({safe_count/len(df)*100:.1f}%)")
    print(f"  Risky locations: {risky_count} ({risky_count/len(df)*100:.1f}%)")

def main():
    """Main training function"""
    print("="*60)
    print("WOMEN EMPOWERHER - CRIME PREDICTION MODEL TRAINING")
    print("="*60)
    
    # Set paths
    data_path = os.path.join('data', 'crime_data.csv')
    model_path = os.path.join('model', 'crime_predictor.pkl')
    preprocessor_path = os.path.join('model', 'preprocessor.pkl')
    
    # Load data
    df = load_data(data_path)
    if df is None:
        print("Failed to load data. Exiting.")
        return
    
    # Analyze data
    analyze_data(df)
    
    # Initialize preprocessor
    print("\n" + "="*50)
    print("PREPROCESSING DATA")
    print("="*50)
    
    preprocessor = CrimeDataPreprocessor()
    
    # Preprocess data
    features, labels = preprocessor.fit_transform(df)
    
    print(f"Features shape: {features.shape}")
    print(f"Labels shape: {labels.shape}")
    print(f"Feature names: {list(features.columns)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Train model
    print("\n" + "="*50)
    print("TRAINING MODEL")
    print("="*50)
    
    model = train_model(X_train, y_train)
    
    # Evaluate model
    evaluation_results = evaluate_model(model, X_test, y_test)
    
    # Save model and preprocessor
    print("\n" + "="*50)
    print("SAVING MODEL")
    print("="*50)
    
    success = save_model_and_preprocessor(model, preprocessor, model_path, preprocessor_path)
    
    if success:
        print("\n" + "="*50)
        print("TRAINING COMPLETED SUCCESSFULLY")
        print("="*50)
        print(f"Model saved to: {model_path}")
        print(f"Preprocessor saved to: {preprocessor_path}")
        print(f"Model accuracy: {evaluation_results['accuracy']:.4f} ({evaluation_results['accuracy']*100:.2f}%)")
        
        # Save evaluation results
        eval_path = os.path.join('model', 'evaluation_results.json')
        import json
        with open(eval_path, 'w') as f:
            json.dump(evaluation_results, f, indent=2)
        print(f"Evaluation results saved to: {eval_path}")
        
    else:
        print("Failed to save model and preprocessor")

if __name__ == "__main__":
    main() 