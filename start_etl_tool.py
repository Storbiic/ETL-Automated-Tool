#!/usr/bin/env python3
"""
Complete startup script for ETL Automation Tool
Starts both FastAPI backend and React frontend
"""

import subprocess
import sys
import os
import time
import webbrowser
import threading
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    print("🔧 Starting FastAPI Backend...")
    
    try:
        # Activate conda environment and start backend
        process = subprocess.Popen(
            ["conda", "run", "-n", "etl", "python", "start_backend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream backend output with prefix
        for line in process.stdout:
            print(f"[BACKEND] {line.strip()}")
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

def start_frontend():
    """Start the React frontend server"""
    print("🚀 Starting React Frontend...")
    
    frontend_dir = Path(__file__).parent / "react-frontend"
    
    try:
        # Change to frontend directory
        os.chdir(frontend_dir)
        
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        # Start the development server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream frontend output with prefix
        for line in process.stdout:
            print(f"[FRONTEND] {line.strip()}")
            
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")

def main():
    """Start both backend and frontend servers"""
    
    print("🚀 ETL Automation Tool v2.0 - Complete Startup")
    print("=" * 60)
    print("🔧 Backend: FastAPI v2.0 (http://localhost:8000)")
    print("🌐 Frontend: React + Next.js (http://localhost:3000)")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)
    
    try:
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Wait a moment for backend to start
        time.sleep(5)
        
        # Start frontend in a separate thread
        frontend_thread = threading.Thread(target=start_frontend, daemon=True)
        frontend_thread.start()
        
        # Wait a moment for frontend to start
        time.sleep(8)
        
        # Open browser to frontend
        try:
            webbrowser.open("http://localhost:3000")
            print("🌐 Opened browser at http://localhost:3000")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print("Please manually open http://localhost:3000")
        
        print("\n✅ Both servers are starting up...")
        print("📊 Backend API: http://localhost:8000")
        print("🎨 Frontend UI: http://localhost:3000")
        print("\n🔄 Monitoring both services...")
        print("Press Ctrl+C to stop both servers")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down ETL Tool...")
        print("Stopping both backend and frontend servers...")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
