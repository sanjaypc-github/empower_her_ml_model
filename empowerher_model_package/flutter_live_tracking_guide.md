# Real-Time Location Tracking Integration Guide

## 🚀 **Live Safety Monitoring for Flutter App**

This guide shows you how to integrate real-time location tracking with safety notifications in your Flutter application.

## 📱 **Flutter Implementation**

### **1. Live Safety Service**

```dart
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class LiveSafetyService {
  static const String _baseUrl = 'http://10.181.131.103:5001';
  
  // Location tracking
  StreamSubscription<Position>? _locationSubscription;
  Position? _lastKnownPosition;
  String? _lastRiskLevel;
  
  // Notification plugin
  final FlutterLocalNotificationsPlugin _notifications = 
      FlutterLocalNotificationsPlugin();
  
  // User identification
  String userId;
  
  LiveSafetyService({required this.userId}) {
    _initializeNotifications();
  }
  
  /// Initialize local notifications
  Future<void> _initializeNotifications() async {
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings();
    
    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );
    
    await _notifications.initialize(initSettings);
  }
  
  /// Start continuous location monitoring
  Future<void> startLiveTracking() async {
    // Check location permissions
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('Location permissions are denied');
      }
    }
    
    // Start location stream
    const locationSettings = LocationSettings(
      accuracy: LocationAccuracy.high,
      distanceFilter: 10, // Update every 10 meters
    );
    
    _locationSubscription = Geolocator.getPositionStream(
      locationSettings: locationSettings,
    ).listen(_onLocationUpdate);
    
    print('Live safety tracking started for user: $userId');
  }
  
  /// Stop location monitoring
  void stopLiveTracking() {
    _locationSubscription?.cancel();
    _locationSubscription = null;
    print('Live safety tracking stopped');
  }
  
  /// Handle location updates
  Future<void> _onLocationUpdate(Position position) async {
    _lastKnownPosition = position;
    
    try {
      // Check safety for current location
      final safetyResult = await checkLocationSafety(
        latitude: position.latitude,
        longitude: position.longitude,
      );
      
      // Process safety notification
      await _processSafetyResult(safetyResult);
      
    } catch (e) {
      print('Error checking location safety: $e');
    }
  }
  
  /// Check safety for specific coordinates
  Future<SafetyResult> checkLocationSafety({
    required double latitude,
    required double longitude,
    String? customTime,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/live_safety_check'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'latitude': latitude,
          'longitude': longitude,
          'time': customTime ?? _getCurrentTime(),
          'user_id': userId,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return SafetyResult.fromJson(data);
      } else {
        throw Exception('Safety check failed: ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
  
  /// Process safety result and send notifications
  Future<void> _processSafetyResult(SafetyResult result) async {
    final currentRiskLevel = result.riskAssessment.finalRiskLevel;
    
    // Only notify for risk level changes or high/critical risks
    if (_shouldNotify(currentRiskLevel)) {
      await _showSafetyNotification(result);
    }
    
    _lastRiskLevel = currentRiskLevel;
  }
  
  /// Determine if notification should be shown
  bool _shouldNotify(String currentRiskLevel) {
    // Always notify for high/critical risks
    if (currentRiskLevel == 'high' || currentRiskLevel == 'critical') {
      return true;
    }
    
    // Notify for risk level changes
    if (_lastRiskLevel != currentRiskLevel) {
      return true;
    }
    
    return false;
  }
  
  /// Show safety notification to user
  Future<void> _showSafetyNotification(SafetyResult result) async {
    final notification = result.notification;
    
    // Determine notification priority
    NotificationPriority priority;
    String channelId;
    
    switch (result.riskAssessment.finalRiskLevel) {
      case 'critical':
        priority = NotificationPriority.max;
        channelId = 'critical_safety';
        break;
      case 'high':
        priority = NotificationPriority.high;
        channelId = 'high_safety';
        break;
      default:
        priority = NotificationPriority.defaultPriority;
        channelId = 'general_safety';
    }
    
    // Android notification details
    final androidDetails = AndroidNotificationDetails(
      channelId,
      'Safety Alerts',
      channelDescription: 'Real-time safety notifications',
      importance: Importance.max,
      priority: priority,
      showWhen: true,
      color: _getColorFromString(notification.alertColor),
      icon: '@mipmap/ic_launcher',
    );
    
    // iOS notification details
    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );
    
    final platformDetails = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );
    
    // Show notification
    await _notifications.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      'Safety Alert',
      notification.message,
      platformDetails,
    );
    
    print('Safety notification shown: ${notification.message}');
  }
  
  /// Get current time in HH:MM format
  String _getCurrentTime() {
    final now = DateTime.now();
    return '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';
  }
  
  /// Convert color string to Color
  Color? _getColorFromString(String colorName) {
    switch (colorName.toLowerCase()) {
      case 'red': return Colors.red;
      case 'orange': return Colors.orange;
      case 'yellow': return Colors.yellow;
      case 'green': return Colors.green;
      default: return null;
    }
  }
}

/// Safety result data model
class SafetyResult {
  final String userId;
  final LocationData location;
  final RiskAssessment riskAssessment;
  final NotificationData notification;
  final List<String> safetyRecommendations;
  
  SafetyResult({
    required this.userId,
    required this.location,
    required this.riskAssessment,
    required this.notification,
    required this.safetyRecommendations,
  });
  
  factory SafetyResult.fromJson(Map<String, dynamic> json) {
    return SafetyResult(
      userId: json['user_id'],
      location: LocationData.fromJson(json['location']),
      riskAssessment: RiskAssessment.fromJson(json['risk_assessment']),
      notification: NotificationData.fromJson(json['notification']),
      safetyRecommendations: List<String>.from(json['safety_recommendations']),
    );
  }
}

class LocationData {
  final double latitude;
  final double longitude;
  final String timestamp;
  
  LocationData({
    required this.latitude,
    required this.longitude,
    required this.timestamp,
  });
  
  factory LocationData.fromJson(Map<String, dynamic> json) {
    return LocationData(
      latitude: json['latitude'].toDouble(),
      longitude: json['longitude'].toDouble(),
      timestamp: json['timestamp'],
    );
  }
}

class RiskAssessment {
  final String? gridRisk;
  final String mlPrediction;
  final double mlConfidence;
  final String finalRiskLevel;
  
  RiskAssessment({
    this.gridRisk,
    required this.mlPrediction,
    required this.mlConfidence,
    required this.finalRiskLevel,
  });
  
  factory RiskAssessment.fromJson(Map<String, dynamic> json) {
    return RiskAssessment(
      gridRisk: json['grid_risk'],
      mlPrediction: json['ml_prediction'],
      mlConfidence: json['ml_confidence'].toDouble(),
      finalRiskLevel: json['final_risk_level'],
    );
  }
}

class NotificationData {
  final String message;
  final String alertColor;
  final bool shouldNotify;
  
  NotificationData({
    required this.message,
    required this.alertColor,
    required this.shouldNotify,
  });
  
  factory NotificationData.fromJson(Map<String, dynamic> json) {
    return NotificationData(
      message: json['message'],
      alertColor: json['alert_color'],
      shouldNotify: json['should_notify'],
    );
  }
}
```

### **2. Usage in Your Flutter App**

```dart
class SafetyTrackingScreen extends StatefulWidget {
  @override
  _SafetyTrackingScreenState createState() => _SafetyTrackingScreenState();
}

class _SafetyTrackingScreenState extends State<SafetyTrackingScreen> {
  late LiveSafetyService _safetyService;
  bool _isTracking = false;
  SafetyResult? _currentSafety;
  
  @override
  void initState() {
    super.initState();
    _safetyService = LiveSafetyService(userId: 'user_12345');
  }
  
  @override
  void dispose() {
    _safetyService.stopLiveTracking();
    super.dispose();
  }
  
  Future<void> _toggleTracking() async {
    try {
      if (_isTracking) {
        _safetyService.stopLiveTracking();
      } else {
        await _safetyService.startLiveTracking();
      }
      
      setState(() {
        _isTracking = !_isTracking;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }
  
  Future<void> _checkCurrentLocation() async {
    try {
      final position = await Geolocator.getCurrentPosition();
      final result = await _safetyService.checkLocationSafety(
        latitude: position.latitude,
        longitude: position.longitude,
      );
      
      setState(() {
        _currentSafety = result;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error checking location: $e')),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Live Safety Tracking'),
        backgroundColor: _getAppBarColor(),
      ),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            // Tracking Status
            Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(
                      _isTracking ? Icons.location_on : Icons.location_off,
                      color: _isTracking ? Colors.green : Colors.grey,
                      size: 32,
                    ),
                    SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _isTracking ? 'Live Tracking Active' : 'Tracking Stopped',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            _isTracking 
                              ? 'Monitoring your safety in real-time'
                              : 'Tap to start safety monitoring',
                          ),
                        ],
                      ),
                    ),
                    Switch(
                      value: _isTracking,
                      onChanged: (_) => _toggleTracking(),
                    ),
                  ],
                ),
              ),
            ),
            
            SizedBox(height: 16),
            
            // Manual Check Button
            ElevatedButton.icon(
              onPressed: _checkCurrentLocation,
              icon: Icon(Icons.my_location),
              label: Text('Check Current Location'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
            ),
            
            SizedBox(height: 16),
            
            // Current Safety Status
            if (_currentSafety != null) ...[
              Card(
                color: _getSafetyCardColor(),
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            _getSafetyIcon(),
                            color: _getSafetyIconColor(),
                            size: 24,
                          ),
                          SizedBox(width: 8),
                          Text(
                            'Current Safety Status',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 12),
                      
                      Text(
                        _currentSafety!.notification.message,
                        style: TextStyle(fontSize: 14),
                      ),
                      
                      SizedBox(height: 12),
                      
                      // Risk Level Indicator
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: _getRiskLevelColor(),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          _currentSafety!.riskAssessment.finalRiskLevel.toUpperCase(),
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ),
                      
                      SizedBox(height: 12),
                      
                      // Safety Recommendations
                      Text(
                        'Safety Recommendations:',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      SizedBox(height: 4),
                      ...(_currentSafety!.safetyRecommendations.take(3).map(
                        (rec) => Padding(
                          padding: EdgeInsets.only(left: 8, top: 2),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('• ', style: TextStyle(fontSize: 12)),
                              Expanded(
                                child: Text(rec, style: TextStyle(fontSize: 12)),
                              ),
                            ],
                          ),
                        ),
                      )),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
  
  Color _getAppBarColor() {
    if (_currentSafety == null) return Colors.blue;
    
    switch (_currentSafety!.riskAssessment.finalRiskLevel) {
      case 'critical': return Colors.red[700]!;
      case 'high': return Colors.orange[700]!;
      case 'medium': return Colors.yellow[700]!;
      default: return Colors.green[700]!;
    }
  }
  
  Color _getSafetyCardColor() {
    if (_currentSafety == null) return Colors.grey[100]!;
    
    switch (_currentSafety!.riskAssessment.finalRiskLevel) {
      case 'critical': return Colors.red[50]!;
      case 'high': return Colors.orange[50]!;
      case 'medium': return Colors.yellow[50]!;
      default: return Colors.green[50]!;
    }
  }
  
  IconData _getSafetyIcon() {
    if (_currentSafety == null) return Icons.help;
    
    switch (_currentSafety!.riskAssessment.finalRiskLevel) {
      case 'critical': return Icons.dangerous;
      case 'high': return Icons.warning;
      case 'medium': return Icons.info;
      default: return Icons.check_circle;
    }
  }
  
  Color _getSafetyIconColor() {
    if (_currentSafety == null) return Colors.grey;
    
    switch (_currentSafety!.riskAssessment.finalRiskLevel) {
      case 'critical': return Colors.red;
      case 'high': return Colors.orange;
      case 'medium': return Colors.yellow[700]!;
      default: return Colors.green;
    }
  }
  
  Color _getRiskLevelColor() {
    if (_currentSafety == null) return Colors.grey;
    
    switch (_currentSafety!.riskAssessment.finalRiskLevel) {
      case 'critical': return Colors.red;
      case 'high': return Colors.orange;
      case 'medium': return Colors.yellow[700]!;
      default: return Colors.green;
    }
  }
}
```

### **3. Required Dependencies**

Add these to your `pubspec.yaml`:

```yaml
dependencies:
  geolocator: ^9.0.2
  flutter_local_notifications: ^16.3.2
  http: ^1.1.0
  permission_handler: ^11.0.1
```

## 🔧 **API Endpoints for Live Tracking**

### **1. Live Safety Check**
```bash
POST http://10.181.131.103:5001/live_safety_check
{
  "latitude": 10.9467,
  "longitude": 76.8653,
  "user_id": "user_12345"
}
```

**Response:**
```json
{
  "user_id": "user_12345",
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
    "message": "🚨 CRITICAL ALERT: You're in a high-risk area during night hours. Consider leaving immediately or finding a safe location.",
    "alert_color": "red",
    "should_notify": true
  },
  "safety_recommendations": [
    "Keep your phone charged and accessible",
    "Share your location with trusted contacts",
    "Leave the area immediately if possible",
    "Call emergency services if you feel threatened"
  ]
}
```

### **2. Journey Tracking**
```bash
POST http://10.181.131.103:5001/track_user_journey
{
  "user_id": "user_12345",
  "locations": [
    {"latitude": 10.9467, "longitude": 76.8653, "timestamp": "2024-01-08T19:30:00"},
    {"latitude": 10.9468, "longitude": 76.8654, "timestamp": "2024-01-08T19:31:00"}
  ]
}
```

## 🚀 **How It Works**

1. **Location Updates**: Your Flutter app continuously tracks GPS location
2. **Real-time API Calls**: Every location update is sent to the API
3. **Risk Assessment**: The model analyzes location against crime data and grid zones
4. **Smart Notifications**: Only shows notifications for risk changes or high-risk areas
5. **Contextual Messages**: Different messages based on time of day and risk level

## 📱 **Notification Examples**

- **Critical**: "🚨 CRITICAL ALERT: You're in a high-risk area during night hours. Consider leaving immediately."
- **High**: "⚠️ CAUTION: Elevated risk detected. Stay vigilant and avoid isolated areas."
- **Medium**: "📍 ADVISORY: Medium risk area during evening. Stay with groups if possible."
- **Safe**: "✅ You're in a safe area. Enjoy your time!"

This system provides **real-time safety monitoring** with **intelligent notifications** based on your location data!

