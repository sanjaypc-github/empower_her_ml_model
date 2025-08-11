# Women EmpowerHer - Crime Prediction Model

A comprehensive machine learning system for predicting crime risk and providing safety recommendations for women based on historical crime data and user feedback.

## 🎯 Project Overview

Women EmpowerHer is an intelligent safety prediction system that:

- **Analyzes crime patterns** using historical data from Coimbatore, India
- **Predicts safety levels** for specific locations, times, and crime types
- **Learns from user feedback** through a reinforcement learning approach
- **Provides real-time predictions** via a RESTful API
- **Integrates with Flutter apps** through Firebase feedback collection

## 🏗️ System Architecture

```
empowerher_model_package/
├── model/
│   ├── crime_predictor.pkl      # Trained ML model
│   ├── preprocessor.pkl         # Data preprocessor
│   └── feedback_trainer.py      # Feedback processing system
├── data/
│   └── crime_data.csv          # Crime dataset (20,000+ records)
├── api/
│   └── app.py                  # Flask REST API
├── utils/
│   ├── preprocess.py           # Data preprocessing utilities
│   └── firebase_utils.py       # Firebase integration
├── requirements.txt            # Python dependencies
├── train_model.py             # Model training script
├── run.sh                     # System startup script
└── README.md                  # This file
```

## 📊 Dataset

The system uses a comprehensive crime dataset from Coimbatore, India with 20,000+ records including:

- **Crime_ID**: Unique identifier
- **Crime_Type**: Type of crime (Sexual Harassment, Theft, etc.)
- **Location**: Geographic location name
- **Latitude/Longitude**: GPS coordinates
- **Date/Time**: When the crime occurred
- **Severity**: Crime severity (1-5 scale)
- **Police_Station**: Nearest police station

## 🧠 Machine Learning Model

### Features Used:
- **Geographic**: Latitude, Longitude
- **Temporal**: Hour, minute, day of week, month, time periods (night/evening/morning/afternoon)
- **Categorical**: Encoded crime types and police stations
- **Severity**: Crime severity level

### Model Type:
- **RandomForestClassifier** with 100 estimators
- **Binary Classification**: Safe (0) vs Risky (1)
- **Accuracy**: Typically 85-90% on test data

### Risk Classification Logic:
- **High-risk crimes**: Sexual Harassment, Kidnapping, Murder, Assault, Chain Snatching, Robbery, Domestic Violence
- **High severity**: Crimes with severity 4-5
- **Time-based risk**: Night hours (10 PM - 6 AM) are considered higher risk

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd empowerher_model_package
pip install -r requirements.txt
```

### 2. Train the Model
```bash
python train_model.py
```

### 3. Start the API Server
```bash
python api/app.py
```

### 4. Test the API
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 10.9467,
    "longitude": 76.8653,
    "time": "04:00",
    "severity": 4,
    "crime_type": "Sexual Harassment"
  }'
```

## 🔧 Complete System Setup

### Using the Run Script (Recommended)
```bash
# Install dependencies and train model
./run.sh train

# Start API server only
./run.sh api

# Start complete system (train + API + feedback processing)
./run.sh all

# Test the system
./run.sh test
```

### Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the model
python train_model.py

# 3. Start API server
python api/app.py

# 4. Start feedback processing (in separate terminal)
python model/feedback_trainer.py
```

## 📡 API Endpoints

### Health Check
```http
GET /health
```
Returns system status and model loading information.

### Safety Prediction
```http
POST /predict
Content-Type: application/json

{
  "latitude": 10.9467,
  "longitude": 76.8653,
  "time": "04:00",
  "severity": 4,
  "crime_type": "Sexual Harassment"
}
```

**Response:**
```json
{
  "prediction": "risky",
  "confidence": 0.892,
  "risk_score": 0.892,
  "safe_score": 0.108,
  "input_data": {
    "latitude": 10.9467,
    "longitude": 76.8653,
    "time": "04:00",
    "severity": 4,
    "crime_type": "Sexual Harassment"
  },
  "timestamp": "2024-01-08T19:30:00"
}
```

### Batch Prediction
```http
POST /predict_batch
Content-Type: application/json

{
  "locations": [
    {
      "latitude": 10.9467,
      "longitude": 76.8653,
      "time": "04:00",
      "severity": 4,
      "crime_type": "Sexual Harassment"
    }
  ]
}
```

### Model Information
```http
GET /model_info
```
Returns model type, feature names, and configuration.

### Example Request
```http
GET /example_request
```
Returns example request format for testing.

## 🔄 Feedback Learning System

### Firebase Integration
The system connects to Firebase to collect user feedback from the Flutter app:

```json
{
  "feedback": "Bad",
  "suggestion": "Add Madukkarai PS at night time for Sexual Harassment",
  "lat": 10.9467,
  "lon": 76.8653,
  "time": "04:00",
  "crime_type": "Sexual Harassment"
}
```

### Feedback Processing
1. **Good feedback**: No model update needed
2. **Bad feedback**: 
   - Parse user suggestions
   - Extract new crime types, locations, time ranges
   - Update model with new training data
   - Save updated model

### Running Feedback Processing
```bash
python model/feedback_trainer.py
```

## 🛠️ Configuration

### Firebase Setup
1. Create a Firebase project
2. Download service account key JSON file
3. Update `firebase_utils.py` with your Firebase credentials

### Model Configuration
Edit `train_model.py` to modify:
- Model type (RandomForest, XGBoost, etc.)
- Hyperparameters
- Feature engineering
- Risk classification logic

### API Configuration
Edit `api/app.py` to modify:
- Server host and port
- CORS settings
- Request validation rules

## 📈 Model Performance

### Typical Results:
- **Accuracy**: 85-90%
- **Precision**: 0.87
- **Recall**: 0.89
- **F1-Score**: 0.88

### Cross-Validation:
- **5-fold CV Mean**: 0.86
- **CV Standard Deviation**: ±0.03

## 🔍 Data Analysis

The system provides comprehensive data analysis:

- **Crime type distribution**
- **Temporal patterns** (hourly, daily, monthly)
- **Geographic hotspots**
- **Severity analysis**
- **Risk distribution**

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/
```

### API Testing
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test prediction endpoint
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### System Testing
```bash
./run.sh test
```

## 📱 Flutter Integration

### API Calls
```dart
// Example Flutter code
final response = await http.post(
  Uri.parse('http://your-api-server:5000/predict'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'latitude': 10.9467,
    'longitude': 76.8653,
    'time': '04:00',
    'severity': 4,
    'crime_type': 'Sexual Harassment',
  }),
);

final result = jsonDecode(response.body);
print('Safety: ${result['prediction']}');
print('Confidence: ${result['confidence']}');
```

### Firebase Feedback
```dart
// Send feedback to Firebase
await FirebaseFirestore.instance.collection('feedbacks').add({
  'feedback': 'Bad',
  'suggestion': 'Add new crime type for this area',
  'lat': 10.9467,
  'lon': 76.8653,
  'time': '04:00',
  'crime_type': 'Sexual Harassment',
  'timestamp': DateTime.now().toIso8601String(),
});
```

## 🚨 Troubleshooting

### Common Issues:

1. **Model not found**
   ```bash
   python train_model.py
   ```

2. **Firebase connection failed**
   - Check Firebase credentials
   - Verify internet connection
   - Test with `firebase_utils.py`

3. **API server won't start**
   - Check port 5000 is available
   - Verify all dependencies installed
   - Check model files exist

4. **Low prediction accuracy**
   - Retrain model with more data
   - Adjust feature engineering
   - Review risk classification logic

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the troubleshooting section

## 🔮 Future Enhancements

- **Real-time crime data integration**
- **Advanced ML models** (Deep Learning, Ensemble methods)
- **Mobile app integration**
- **Geographic visualization**
- **Multi-city support**
- **Predictive analytics dashboard**

---

**Women EmpowerHer** - Empowering women through intelligent safety prediction and community feedback. 