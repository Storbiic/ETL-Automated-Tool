# 🔧 ETL Tool - Troubleshooting Guide

## 🚨 **Common Issues & Solutions**

### **Issue: "Backend API Unavailable"**

#### **Symptoms:**
- React frontend shows "Backend API Unavailable" message
- Red connection indicator in header
- 422 Unprocessable Entity errors

#### **Solutions:**

1. **Check if Backend is Running:**
   ```bash
   # Test backend health
   curl http://localhost:8000/
   
   # Should return: {"message": "ETL Automation Tool API is running", "version": "2.0.0"}
   ```

2. **Start Backend if Not Running:**
   ```bash
   python start_backend.py
   ```

3. **Check for Port Conflicts:**
   ```bash
   # Check if port 8000 is in use
   lsof -i :8000
   
   # Kill process if needed
   kill -9 <PID>
   ```

4. **Verify Dependencies:**
   ```bash
   pip install fastapi uvicorn[standard] python-multipart
   pip install pandas openpyxl pydantic pydantic-settings
   ```

---

### **Issue: 422 Unprocessable Entity**

#### **Cause:**
- API endpoint mismatch between frontend and backend
- Wrong request format

#### **Solution:**
The React frontend now uses session-based endpoints:
- `/preview-session` (instead of `/preview`)
- `/clean-session` (instead of `/clean`)
- `/lookup-session` (instead of `/lookup`)

These are automatically handled by the updated frontend.

---

### **Issue: React Frontend Not Loading**

#### **Solutions:**

1. **Check if React is Running:**
   ```bash
   cd react-frontend
   npm run dev
   ```

2. **Install Dependencies:**
   ```bash
   cd react-frontend
   npm install
   ```

3. **Clear Cache:**
   ```bash
   cd react-frontend
   rm -rf .next
   npm run dev
   ```

---

## 🧪 **Testing & Debugging**

### **1. Test API Endpoints:**
```bash
python test_api_endpoints.py
```

### **2. Manual API Testing:**
```bash
# Health check
curl http://localhost:8000/

# Test preview (will fail without file - expected)
curl -X POST http://localhost:8000/preview-session \
  -H "Content-Type: application/json" \
  -d '{"master_sheet": "Sheet1", "target_sheet": "Sheet2"}'
```

### **3. Check Logs:**
- **Backend logs:** Check terminal running `start_backend.py`
- **Frontend logs:** Check browser console (F12)
- **Network requests:** Check browser Network tab

---

## 🚀 **Startup Sequence**

### **Option 1: Start Everything**
```bash
python start_etl_tool.py
```

### **Option 2: Start Individually**
```bash
# Terminal 1: Backend
python start_backend.py

# Terminal 2: Frontend
cd react-frontend && npm run dev
```

### **Expected URLs:**
- **🌐 React Frontend:** http://localhost:3000
- **📊 Backend API:** http://localhost:8000
- **📚 API Docs:** http://localhost:8000/docs

---

## 🔍 **Development Tools**

### **API Debugger (Development Mode):**
- Available in React frontend when `NODE_ENV=development`
- Click the bug icon in the header
- Test API endpoints directly from the UI

### **Browser Console:**
- Press F12 to open developer tools
- Check Console tab for JavaScript errors
- Check Network tab for failed API requests

---

## 📋 **Checklist for Issues**

When experiencing problems, check:

- [ ] Backend is running on port 8000
- [ ] React frontend is running on port 3000
- [ ] No port conflicts
- [ ] All dependencies installed
- [ ] API health check passes
- [ ] Browser console shows no errors
- [ ] Network requests are successful

---

## 🆘 **Getting Help**

### **Error Messages to Look For:**

1. **"EADDRINUSE"** - Port already in use
2. **"Module not found"** - Missing dependencies
3. **"422 Unprocessable Entity"** - API format mismatch
4. **"CORS error"** - Cross-origin request blocked
5. **"Connection refused"** - Backend not running

### **Quick Fixes:**

1. **Restart everything:**
   ```bash
   # Kill all processes
   pkill -f "uvicorn\|next"
   
   # Restart
   python start_etl_tool.py
   ```

2. **Reset React cache:**
   ```bash
   cd react-frontend
   rm -rf .next node_modules
   npm install
   npm run dev
   ```

3. **Check Python environment:**
   ```bash
   which python
   pip list | grep fastapi
   ```

---

## ✅ **Verification Steps**

After fixing issues:

1. **Backend Health:** `curl http://localhost:8000/`
2. **Frontend Loading:** Open http://localhost:3000
3. **API Connection:** Green indicator in React header
4. **File Upload:** Try uploading a test file
5. **Workflow:** Test the complete ETL process

---

## 🔧 **Advanced Debugging**

### **Backend Debug Mode:**
```bash
# Start with debug logging
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

### **React Debug Mode:**
```bash
cd react-frontend
npm run dev -- --debug
```

### **API Response Inspection:**
Use the built-in API debugger in the React frontend or tools like:
- Postman
- curl
- Browser Network tab

This troubleshooting guide should help resolve most common issues with the ETL tool setup and operation.
