# Railway Deployment Guide for Women EmpowerHer ML API

## 🚄 **Why Railway is Better Than Render for ML Models**

- ✅ **Faster deployments** (2-3 minutes vs 10+ minutes)
- ✅ **Better ML model handling** (large file support)
- ✅ **More reliable** Python deployments
- ✅ **Better resource allocation** for model loading
- ✅ **Automatic scaling** and health checks

## 📋 **Prerequisites**

1. **GitHub account** with your repository
2. **Railway account** (free tier available)
3. **All model files** in your repository

## 🔧 **Step-by-Step Railway Setup**

### **Step 1: Create Railway Account**
1. Go to [railway.app](https://railway.app)
2. Click **"Start for Free"**
3. Sign up with **GitHub**
4. Authorize Railway to access your repositories

### **Step 2: Create New Project**
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `sanjaypc-github/empower_her_ml_model`
4. **IMPORTANT**: Select subdirectory `empowerher_model_package`
5. Click **"Deploy Now"**

### **Step 3: Wait for Deployment**
- **Build time**: 2-3 minutes
- **Model loading**: 1-2 minutes
- **Total**: ~5 minutes

## 📁 **Railway Configuration Files (Already Created)**

### **1. requirements.txt** ✅
Updated with Railway-compatible versions

### **2. Procfile** ✅
```
web: gunicorn api.app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1
```

### **3. runtime.txt** ✅
```
python-3.9.18
```

### **4. railway.json** ✅
Advanced Railway configuration

## 🚀 **Deployment Process**

### **Automatic Detection**
Railway will automatically:
1. **Detect Python project** from `requirements.txt`
2. **Use Python 3.9.18** from `runtime.txt`
3. **Install dependencies** from `requirements.txt`
4. **Use start command** from `Procfile`
5. **Deploy your API**

### **Start Command Explanation**
```bash
gunicorn api.app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1
```

**Why this command:**
- `--timeout 300`: 5 minutes for model loading
- `--workers 1`: Single worker for ML models (memory efficient)
- `--bind 0.0.0.0:$PORT`: Bind to Railway's port

## 📊 **Railway vs Render Comparison**

| Feature | Railway | Render |
|---------|---------|---------|
| **Deployment Speed** | 2-3 minutes | 10+ minutes |
| **ML Model Support** | ✅ Excellent | ⚠️ Limited |
| **Large File Handling** | ✅ Good | ❌ Poor |
| **Python Support** | ✅ Excellent | ✅ Good |
| **Free Tier** | ✅ Available | ✅ Available |
| **Auto-scaling** | ✅ Yes | ❌ No |

## 🧪 **Testing Your Railway Deployment**

### **Step 1: Get Your Railway URL**
After deployment, Railway will give you a URL like:
```
https://your-app-name.railway.app
```

### **Step 2: Test Health Endpoint**
```bash
curl https://your-app-name.railway.app/health
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

### **Step 3: Test Live Safety Check**
```bash
curl -X POST "https://your-app-name.railway.app/live_safety_check" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 10.9467,
    "longitude": 76.8653,
    "time": "04:00",
    "user_id": "test_user"
  }'
```

## 🔍 **Monitoring Your Deployment**

### **Railway Dashboard Features**
1. **Real-time logs** - See model loading progress
2. **Deployment status** - Monitor build and deployment
3. **Environment variables** - Manage configuration
4. **Custom domains** - Add your own domain
5. **Metrics** - Monitor performance

### **Health Checks**
Railway automatically checks `/health` endpoint:
- **Success**: Service is healthy
- **Failure**: Automatic restart

## 🚨 **Troubleshooting**

### **Common Issues**

**Issue 1: "No start command could be found"** ❌
- **Solution**: Use `Procfile` (already created)
- **Why**: Railway needs explicit start command

**Issue 2: Build Fails**
- Check `requirements.txt` for compatibility
- Ensure all dependencies are available

**Issue 3: Models Don't Load**
- Check file paths in code
- Verify model files are in repository
- Check Railway logs for errors

**Issue 4: Timeout Errors**
- Check `Procfile` timeout setting
- Check model loading time

### **Debug Commands**
```bash
# Check Railway logs
railway logs

# Check deployment status
railway status

# Restart deployment
railway up
```

## 📱 **Flutter Integration**

### **Update Your Flutter App**
```dart
// Replace Render URL with Railway URL
static const String _baseUrl = 'https://your-app-name.railway.app';
```

### **Test All Endpoints**
1. **Health check** - Verify models loaded
2. **Live safety check** - Test real-time monitoring
3. **Grid zone check** - Test risk classification
4. **Journey tracking** - Test multiple locations

## 🎯 **Expected Results**

After Railway deployment:
- ✅ **Fast deployment** (2-3 minutes)
- ✅ **All models load** successfully
- ✅ **Health endpoint** shows all components loaded
- ✅ **Real-time monitoring** works
- ✅ **Risk classification** works
- ✅ **Flutter integration** works

## 🚀 **Next Steps**

1. **Push updated code** to GitHub
2. **Create Railway account**
3. **Deploy from GitHub** (select subdirectory)
4. **Test endpoints**
5. **Update Flutter app**
6. **Enjoy fast, reliable ML API!**

## ⚠️ **Important Notes**

- **Subdirectory**: Must select `empowerher_model_package` in Railway
- **Procfile**: Essential for Railway to find start command
- **runtime.txt**: Ensures correct Python version
- **requirements.txt**: Must have exact versions for Railway

---

**Railway will give you a much better deployment experience than Render for ML models!** 🚄✨
