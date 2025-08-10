#!/usr/bin/env python3
"""
ETL Automation Tool v2.0 Launcher
Starts both backend and frontend services
"""
import subprocess
import time
import webbrowser
import sys
import os
import signal
import socket
from pathlib import Path

def check_port(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False  # Port is available
        except OSError:
            return True   # Port is in use

def print_banner():
    """Print startup banner"""
    print("=" * 50)
    print("   ETL Automation Tool v2.0 Launcher")
    print("=" * 50)
    print()

def main():
    print_banner()
    
    # Configuration
    python_path = r"C:/Users/Saad/anaconda3/envs/myenv/python.exe"
    backend_port = 8000
    frontend_port = 8501
    
    # Check if ports are available
    print("🔍 Checking ports...")
    if check_port(backend_port):
        print(f"⚠️  Port {backend_port} is already in use. Backend might already be running.")
    if check_port(frontend_port):
        print(f"⚠️  Port {frontend_port} is already in use. Frontend might already be running.")
    
    processes = []
    
    try:
        # Start backend
        print("🚀 Starting FastAPI Backend...")
        backend_cmd = [
            python_path, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", str(backend_port),
            "--reload"
        ]
        
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=os.getcwd(),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        processes.append(("Backend", backend_process))
        
        # Wait for backend to start
        print("⏳ Waiting for backend to initialize...")
        time.sleep(5)
        
        # Start frontend
        print("🎨 Starting Streamlit Frontend...")
        frontend_cmd = [
            python_path, "-m", "streamlit", "run",
            "frontend/app.py",
            "--server.port", str(frontend_port),
            "--server.address", "0.0.0.0"
        ]
        
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=os.getcwd(),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        processes.append(("Frontend", frontend_process))
        
        # Wait for frontend to start
        print("⏳ Waiting for frontend to initialize...")
        time.sleep(8)
        
        # Open browser
        print("🌐 Opening browser...")
        webbrowser.open(f"http://localhost:{frontend_port}")
        
        print()
        print("=" * 50)
        print("✅ ETL Automation Tool v2.0 is running!")
        print("=" * 50)
        print()
        print(f"📊 Frontend: http://localhost:{frontend_port}")
        print(f"🔧 Backend API: http://localhost:{backend_port}")
        print(f"📚 API Docs: http://localhost:{backend_port}/docs")
        print()
        print("Press Ctrl+C to stop both services...")
        
        # Keep script running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            for name, process in processes:
                if process.poll() is not None:
                    print(f"❌ {name} process has stopped!")
                    return
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        # Cleanup processes
        for name, process in processes:
            try:
                if process.poll() is None:  # Process is still running
                    print(f"🛑 Stopping {name}...")
                    if sys.platform == "win32":
                        process.terminate()
                    else:
                        process.send_signal(signal.SIGTERM)
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        print(f"🔨 Force killing {name}...")
                        process.kill()
                        
            except Exception as e:
                print(f"⚠️  Error stopping {name}: {e}")
        
        print("✅ Services stopped.")

if __name__ == "__main__":
    main()
