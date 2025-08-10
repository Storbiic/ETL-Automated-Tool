"""
Streamlit-based launcher for ETL Automation Tool v2.0
This creates a simple UI to launch the main application
"""
import streamlit as st
import subprocess
import sys
import time
import requests

st.set_page_config(
    page_title="ETL Tool Launcher",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 ETL Automation Tool v2.0 Launcher")
st.markdown("---")

# Check if backend is running
def check_backend():
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        return response.status_code == 200
    except:
        return False

# Check if frontend is running
def check_frontend():
    try:
        response = requests.get("http://localhost:8501/", timeout=2)
        return response.status_code == 200
    except:
        return False

# Status checks
st.subheader("📊 Service Status")

col1, col2 = st.columns(2)

with col1:
    if check_backend():
        st.success("✅ Backend Running (Port 8000)")
    else:
        st.error("❌ Backend Not Running")

with col2:
    if check_frontend():
        st.success("✅ Frontend Running (Port 8501)")
    else:
        st.error("❌ Frontend Not Running")

st.markdown("---")

# Launch options
st.subheader("🎯 Launch Options")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚀 Launch Full Application", type="primary"):
        st.info("Starting ETL Automation Tool...")
        st.info("This will open in a new window/tab")
        
        # Use the batch script
        try:
            subprocess.Popen(["run_etl_tool.bat"], shell=True)
            st.success("✅ Application launched!")
            st.info("Check your browser for the ETL tool")
        except Exception as e:
            st.error(f"❌ Launch failed: {e}")

with col2:
    if st.button("🔧 Start Backend Only"):
        try:
            subprocess.Popen([sys.executable, "start_backend.py"])
            st.success("✅ Backend starting...")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Backend start failed: {e}")

with col3:
    if st.button("🎨 Start Frontend Only"):
        try:
            subprocess.Popen([sys.executable, "start_frontend.py"])
            st.success("✅ Frontend starting...")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Frontend start failed: {e}")

st.markdown("---")

# Quick links
st.subheader("🔗 Quick Links")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("[📊 ETL Tool Frontend](http://localhost:8501)")

with col2:
    st.markdown("[🔧 Backend API](http://localhost:8000)")

with col3:
    st.markdown("[📚 API Documentation](http://localhost:8000/docs)")

st.markdown("---")

# Instructions
st.subheader("📋 Instructions")

st.markdown("""
**To use the ETL Automation Tool:**

1. **Click "🚀 Launch Full Application"** - This starts both backend and frontend
2. **Wait for services to start** (about 10-15 seconds)
3. **Use the ETL tool** at http://localhost:8501

**Alternative methods:**
- Double-click `run_etl_tool.bat` in file explorer
- Run `python run_app.py` in command prompt
- Use the individual start buttons above

**If you see this launcher instead of the main tool:**
- You ran `streamlit run run_app.py` (incorrect)
- Use one of the methods above instead
""")

st.markdown("---")
st.caption("ETL Automation Tool v2.0 | Launcher Interface")
