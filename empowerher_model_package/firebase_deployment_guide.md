# Firebase Functions Deployment Guide

## 🚀 **Updated Firebase Functions with Real-time Monitoring**

This guide will help you deploy the updated Firebase Functions that now include all the real-time monitoring endpoints and risk classification features.

## 📋 **What's Been Fixed**

### ✅ **Added Missing Endpoints**
- `/live_safety_check` - Real-time safety monitoring
- `/track_user_journey` - Journey tracking with multiple points
- `/check_grid_zone` - Grid-based risk zone checking
- `/nearby_risk_zones` - Nearby risk zone analysis
- `/grid_summary` - Grid classification summary

### ✅ **Added Grid Classifier**
- Grid-based risk classification (high/medium/low risk zones)
- Crime data analysis and zone mapping
- Combined risk assessment with ML predictions

### ✅ **Enhanced Health Check**
- Now includes grid classifier status
- Better error reporting and diagnostics

## 🔧 **Deployment Steps**

### **Step 1: Prepare Your Files**

Ensure you have the following file structure in your Firebase Functions directory:

```
firebase_functions/
├── main.py                    # Updated with all endpoints
├── requirements.txt           # Dependencies
├── model/                     # Model files (copy from parent)
│   ├── crime_predictor.pkl
│   └── preprocessor.pkl
├── data/                      # Crime data (copy from parent)
│   └── crime_data.csv
└── utils/                     # Utility modules (copy from parent)
    ├── preprocess.py
    └── grid_classifier.py
```

### **Step 2: Copy Required Files**

```bash
# Copy model files
cp ../model/crime_predictor.pkl model/
cp ../model/preprocessor.pkl model/

# Copy data files
cp ../data/crime_data.csv data/

# Copy utility modules
cp -r ../utils/ .
```

### **Step 3: Update requirements.txt**

Make sure your `firebase_functions/requirements.txt` includes:

```txt
functions-framework==3.*
flask==2.*
flask-cors==3.*
scikit-learn>=1.0.0
pandas>=1.3.0
numpy>=1.20.0
joblib>=1.1.0
folium>=0.12.0
```

### **Step 4: Deploy to Firebase**

```bash
# Navigate to firebase_functions directory
cd firebase_functions

# Deploy the functions
firebase deploy --only functions
```

### **Step 5: Test the Deployment**

Use the provided test script:

```bash
# Update the URL in test_firebase_functions.py
python test_firebase_functions.py
```

## 🧪 **Testing Your Deployment**

### **1. Health Check**
```bash
curl -X GET "https://your-firebase-functions-url.com/health_check"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "preprocessor_loaded": true,
  "grid_classifier_loaded": true,
  "timestamp": "2024-01-08T19:30:00"
}
```

### **2. Live Safety Check**
```bash
curl -X POST "https://your-firebase-functions-url.com/live_safety_check" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 10.9467,
    "longitude": 76.8653,
    "time": "04:00",
    "user_id": "test_user"
  }'
```

**Expected Response:**
```json
{
  "user_id": "test_user",
  "location": {
    "latitude": 10.9467,
    "longitude": 76.8653,
    "timestamp": "2024-01-08T19:30:00"
  },
  "risk_assessment": {
    "grid_risk": "high_risk",
    "ml_prediction": "risky",
    "ml_confidence": 0.892,
    "final_risk_level": "critical"
  },
  "notification": {
    "message": "🚨 CRITICAL ALERT: You're in a high-risk area during night hours...",
    "alert_color": "red",
    "should_notify": true
  },
  "safety_recommendations": [
    "Keep your phone charged and accessible",
    "Share your location with trusted contacts",
    "Leave the area immediately if possible"
  ]
}
```

### **3. Grid Zone Check**
```bash
curl -X POST "https://your-firebase-functions-url.com/check_grid_zone" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 10.9467,
    "longitude": 76.8653
  }'
```

## 🔍 **Troubleshooting**

### **Issue 1: Grid Classifier Not Loaded**
**Symptoms:** `"grid_classifier_loaded": false` in health check

**Solutions:**
1. Ensure `crime_data.csv` is in the `data/` directory
2. Check file permissions
3. Verify the CSV file is not corrupted

### **Issue 2: Model Files Not Found**
**Symptoms:** `"model_loaded": false` or `"preprocessor_loaded": false`

**Solutions:**
1. Copy model files to `model/` directory
2. Check file paths in `main.py`
3. Verify file permissions

### **Issue 3: Import Errors**
**Symptoms:** Deployment fails with import errors

**Solutions:**
1. Ensure `utils/` directory is copied
2. Check `requirements.txt` has all dependencies
3. Verify Python version compatibility

### **Issue 4: CORS Errors**
**Symptoms:** Flutter app can't connect

**Solutions:**
1. CORS headers are already configured in the code
2. Check Firebase Functions URL is correct
3. Verify HTTPS is being used

## 📱 **Flutter Integration**

Update your Flutter app to use the new endpoints:

```dart
// Update your base URL
static const String _baseUrl = 'https://your-firebase-functions-url.com';

// Use the live_safety_check endpoint
final response = await http.post(
  Uri.parse('$_baseUrl/live_safety_check'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'latitude': latitude,
    'longitude': longitude,
    'time': currentTime,
    'user_id': userId,
  }),
);
```

## 🎯 **Expected Results**

After successful deployment, your Flutter app should:

1. ✅ **Receive proper risk classifications** (high/medium/low risk zones)
2. ✅ **Get real-time safety notifications** based on location and time
3. ✅ **Show contextual safety recommendations**
4. ✅ **Track journey with risk analysis**
5. ✅ **Provide grid-based risk assessment**

## 📊 **Performance Notes**

- **Cold Start**: First request may take 10-15 seconds to load models
- **Warm Start**: Subsequent requests should be under 2 seconds
- **Memory Usage**: Models and grid data use ~100-200MB RAM
- **Timeout**: Set to 120 seconds for complex operations

## 🔄 **Monitoring**

Check Firebase Functions logs for:
- Model loading status
- Grid classifier initialization
- Request processing times
- Error messages

```bash
firebase functions:log
```

## 🎉 **Success Indicators**

Your deployment is successful when:
- Health check shows all components loaded
- Live safety check returns proper risk levels
- Grid zone check returns zone classifications
- Journey tracking works with multiple points
- Flutter app receives real-time notifications

---

**Next Steps:**
1. Deploy the updated Firebase Functions
2. Test with the provided test script
3. Update your Flutter app to use the new endpoints
4. Verify real-time monitoring is working
5. Test journey tracking functionality
