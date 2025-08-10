"""
Startup script for FastAPI backend v2.0
"""
import subprocess
import sys
import os
from pathlib import Path

if __name__ == "__main__":
    print("🚀 Starting FastAPI Backend v2.0...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 Interactive API: http://localhost:8000/redoc")
    print("🌐 React Frontend: http://localhost:3000")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    # Check if backend structure exists
    if not Path("backend/main.py").exists():
        print("❌ Backend main.py not found!")
        print("Please ensure the backend directory structure is correct.")
        sys.exit(1)

    try:
        # Use the current Python executable to ensure correct environment
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--reload-dir", "backend"
        ])
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        print("Make sure dependencies are installed:")
        print("  pip install fastapi uvicorn[standard] python-multipart")
        print("  pip install pandas openpyxl pydantic")
