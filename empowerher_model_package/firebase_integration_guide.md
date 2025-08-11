# Firebase Integration Guide for Women EmpowerHer Model

## 🚀 **Firebase Integration Options**

### **Option 1: Firebase Cloud Functions (Recommended)**

Your current API can be easily deployed as Firebase Cloud Functions. Here's how:

#### **Step 1: Setup Firebase Project**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase project
firebase init functions
```

#### **Step 2: Deploy Model Files**
```bash
# Copy your trained model files to Firebase Functions
cp model/crime_predictor.pkl firebase_functions/model/
cp model/preprocessor.pkl firebase_functions/model/
cp -r utils/ firebase_functions/
```

#### **Step 3: Deploy to Firebase**
```bash
cd firebase_functions
firebase deploy --only functions
```

#### **Step 4: Use in Your App**
```dart
// Flutter/Dart code
final response = await http.post(
  Uri.parse('https://your-region-your-project.cloudfunctions.net/predict_safety'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'latitude': 10.9467,
    'longitude': 76.8653,
    'time': '04:00',
    'severity': 4,
    'crime_type': 'Sexual Harassment',
  }),
);
```

### **Option 2: Firebase Hosting + External API**

Keep your Flask API on a separate server and use Firebase for:
- User authentication
- Data storage
- Real-time updates

#### **Step 1: Firebase Authentication**
```dart
// Flutter authentication
final userCredential = await FirebaseAuth.instance.signInAnonymously();
final user = userCredential.user;
```

#### **Step 2: API Calls with Authentication**
```dart
// Get Firebase ID token
final idToken = await user?.getIdToken();

// Call your API with authentication
final response = await http.post(
  Uri.parse('https://your-api-server.com/predict'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $idToken',
  },
  body: jsonEncode(predictionData),
);
```

### **Option 3: Firebase Storage for Model Files**

Store your model files in Firebase Storage and load them dynamically:

```python
# In your Firebase Function
import firebase_admin
from firebase_admin import storage
import tempfile

def load_model_from_storage():
    bucket = storage.bucket()
    blob = bucket.blob('models/crime_predictor.pkl')
    
    with tempfile.NamedTemporaryFile() as temp_file:
        blob.download_to_filename(temp_file.name)
        model = joblib.load(temp_file.name)
    return model
```

## 📱 **Flutter Integration Examples**

### **Complete Flutter Service**
```dart
class SafetyPredictionService {
  static const String _baseUrl = 'https://your-firebase-function-url';
  
  static Future<SafetyPrediction> predictSafety({
    required double latitude,
    required double longitude,
    required String time,
    required int severity,
    required String crimeType,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/predict_safety'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'latitude': latitude,
          'longitude': longitude,
          'time': time,
          'severity': severity,
          'crime_type': crimeType,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return SafetyPrediction.fromJson(data);
      } else {
        throw Exception('Prediction failed: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}

class SafetyPrediction {
  final String prediction;
  final double confidence;
  final double riskScore;
  final double safeScore;
  final Map<String, dynamic> inputData;
  final String timestamp;
  
  SafetyPrediction({
    required this.prediction,
    required this.confidence,
    required this.riskScore,
    required this.safeScore,
    required this.inputData,
    required this.timestamp,
  });
  
  factory SafetyPrediction.fromJson(Map<String, dynamic> json) {
    return SafetyPrediction(
      prediction: json['prediction'],
      confidence: json['confidence'].toDouble(),
      riskScore: json['risk_score'].toDouble(),
      safeScore: json['safe_score'].toDouble(),
      inputData: json['input_data'],
      timestamp: json['timestamp'],
    );
  }
}
```

### **Usage in Flutter Widget**
```dart
class SafetyCheckWidget extends StatefulWidget {
  @override
  _SafetyCheckWidgetState createState() => _SafetyCheckWidgetState();
}

class _SafetyCheckWidgetState extends State<SafetyCheckWidget> {
  SafetyPrediction? _prediction;
  bool _isLoading = false;
  
  Future<void> _checkSafety() async {
    setState(() => _isLoading = true);
    
    try {
      final prediction = await SafetyPredictionService.predictSafety(
        latitude: 10.9467,
        longitude: 76.8653,
        time: '04:00',
        severity: 4,
        crimeType: 'Sexual Harassment',
      );
      
      setState(() {
        _prediction = prediction;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ElevatedButton(
          onPressed: _isLoading ? null : _checkSafety,
          child: _isLoading 
            ? CircularProgressIndicator() 
            : Text('Check Safety'),
        ),
        if (_prediction != null) ...[
          Text('Safety: ${_prediction!.prediction}'),
          Text('Confidence: ${(_prediction!.confidence * 100).toStringAsFixed(1)}%'),
          Text('Risk Score: ${(_prediction!.riskScore * 100).toStringAsFixed(1)}%'),
        ],
      ],
    );
  }
}
```

## 🔄 **Feedback Integration with Firebase**

### **Firebase Firestore for Feedback**
```dart
class FeedbackService {
  static Future<void> submitFeedback({
    required String feedback,
    required String suggestion,
    required double latitude,
    required double longitude,
    required String time,
    required String crimeType,
  }) async {
    try {
      await FirebaseFirestore.instance.collection('feedbacks').add({
        'feedback': feedback, // 'Good' or 'Bad'
        'suggestion': suggestion,
        'lat': latitude,
        'lon': longitude,
        'time': time,
        'crime_type': crimeType,
        'timestamp': DateTime.now().toIso8601String(),
        'processed': false,
      });
    } catch (e) {
      throw Exception('Failed to submit feedback: $e');
    }
  }
}
```

## 🛠️ **Deployment Steps**

### **1. Prepare Your Model**
```bash
# Train your model first
cd empowerher_model_package
python train_model.py
```

### **2. Setup Firebase Project**
```bash
# Create Firebase project in console
# Enable Cloud Functions, Firestore, Storage
```

### **3. Deploy Functions**
```bash
cd firebase_functions
firebase deploy --only functions
```

### **4. Test Integration**
```bash
# Test the deployed function
curl -X POST https://your-region-your-project.cloudfunctions.net/predict_safety \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 10.9467,
    "longitude": 76.8653,
    "time": "04:00",
    "severity": 4,
    "crime_type": "Sexual Harassment"
  }'
```

## ✅ **Benefits of Firebase Integration**

1. **Scalability**: Automatic scaling based on demand
2. **Security**: Built-in authentication and authorization
3. **Real-time**: Firestore for real-time data updates
4. **Cost-effective**: Pay only for what you use
5. **Easy deployment**: Simple CLI commands
6. **Global CDN**: Fast response times worldwide

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Set in Firebase Functions
firebase functions:config:set model.bucket="your-model-bucket"
firebase functions:config:set model.path="models/"
```

### **CORS Configuration**
```python
# Already included in the Firebase Function
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}
```

## 🚨 **Important Notes**

1. **Model Size**: Firebase Functions have memory limits (1GB default)
2. **Cold Starts**: First request may be slower
3. **Dependencies**: Include all required packages in requirements.txt
4. **Authentication**: Consider adding Firebase Auth for security
5. **Monitoring**: Use Firebase Console to monitor function performance

Your current API structure is **perfectly compatible** with Firebase integration! 