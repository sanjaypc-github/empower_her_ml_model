# Railway Crash Debugging Guide

## 🚨 **Your Railway Deployment Crashed - Let's Fix It!**

### **Step 1: Check Railway Logs**
1. Go to [railway.app](https://railway.app)
2. Open your project
3. Click **"Deployments"**
4. Click on the **failed deployment**
5. Check **"Logs"** tab

**Look for these error patterns:**
- `Memory limit exceeded`
- `Model file too large`
- `Import error`
- `File not found`

## 🔍 **Common Crash Causes & Solutions**

### **1. Memory Issues (Most Common)**
**Error**: `Memory limit exceeded` or `Killed`
**Cause**: ML models are too large for Railway's free tier

**Solutions**:
```bash
# Option A: Use lightweight requirements
# Replace requirements.txt with railway-light-requirements.txt

# Option B: Reduce model size
# Compress your .pkl files
```

### **2. Model File Size Issues**
**Error**: `File too large` or `Upload failed`
**Cause**: Your model files exceed Railway's limits

**Check file sizes**:
```bash
# Run this locally to check sizes
ls -lh model/*.pkl
ls -lh data/*.csv
```

**Railway Limits**:
- **Free tier**: ~500MB total
- **Your models**: Likely 100MB+ each

### **3. Dependency Conflicts**
**Error**: `Import error` or `Module not found`
**Cause**: Incompatible package versions

**Solution**: Use `railway-light-requirements.txt`

### **4. File Path Issues**
**Error**: `File not found` or `No such file`
**Cause**: Models not in correct location

**Solution**: Verify file structure

## 🚀 **Quick Fix: Lightweight Deployment**

### **Step 1: Use Lightweight Requirements**
```bash
# Replace requirements.txt with lightweight version
cp railway-light-requirements.txt requirements.txt
```

### **Step 2: Update Procfile for Better Error Handling**
```bash
# Add error logging to Procfile
web: gunicorn api.app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --log-level debug
```

### **Step 3: Push and Redeploy**
```bash
git add .
git commit -m "Fix Railway crash: use lightweight requirements"
git push origin main
```

## 🔧 **Advanced Fixes**

### **Fix 1: Model Compression**
If models are too large:
```python
# Add to your training script
import joblib
import gzip

# Compress model before saving
with gzip.open('model/crime_predictor.pkl.gz', 'wb') as f:
    joblib.dump(model, f)
```

### **Fix 2: Lazy Loading**
Load models only when needed:
```python
# In app.py, load models on first request
_models_loaded = False

def load_models_if_needed():
    global _models_loaded, model, preprocessor, grid_classifier
    if not _models_loaded:
        # Load models here
        _models_loaded = True
```

### **Fix 3: Environment Variables**
Add to Railway dashboard:
```
PYTHONUNBUFFERED=1
GUNICORN_TIMEOUT=300
GUNICORN_WORKERS=1
```

## 📊 **Railway Resource Limits**

| Resource | Free Tier | Paid Tier |
|----------|-----------|-----------|
| **Memory** | 512MB | 1GB+ |
| **Storage** | 1GB | 10GB+ |
| **Build Time** | 45 min | Unlimited |
| **Deployments** | Unlimited | Unlimited |

## 🧪 **Test Lightweight Version**

### **Step 1: Test Locally First**
```bash
# Install lightweight requirements
pip install -r railway-light-requirements.txt

# Test if app starts
python api/app.py
```

### **Step 2: Check Model Loading**
```bash
# Run debug script
python debug_model_loading.py
```

## 🎯 **Expected Results After Fix**

- ✅ **No more crashes**
- ✅ **Faster deployment** (1-2 minutes)
- ✅ **Models load successfully**
- ✅ **All endpoints work**

## 🚨 **If Still Crashing**

### **Option 1: Check Logs Again**
Look for specific error messages in Railway logs

### **Option 2: Use Render Instead**
Railway might be too restrictive for your model size

### **Option 3: Reduce Model Size**
Train smaller models or use model compression

## 📱 **Next Steps**

1. **Check Railway logs** for specific error
2. **Try lightweight requirements**
3. **Push updated code**
4. **Redeploy on Railway**
5. **Test endpoints**

---

**Let me know what the Railway logs show, and I'll help you fix it!** 🚄🔧
