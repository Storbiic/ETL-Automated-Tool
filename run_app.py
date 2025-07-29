"""
Main application runner - starts both backend and frontend
"""
import subprocess
import sys
import time
import os
from threading import Thread


def start_backend():
    """Start FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    subprocess.run([sys.executable, "start_backend.py"])


def start_frontend():
    """Start Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    time.sleep(3)  # Wait for backend to start
    subprocess.run([sys.executable, "start_frontend.py"])


if __name__ == "__main__":
    print("🔧 ETL Automation Tool v2.0")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in main thread
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n👋 Shutting down application...")
        sys.exit(0)
