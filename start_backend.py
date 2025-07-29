"""
Startup script for FastAPI backend
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    print("🚀 Starting FastAPI backend on http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    try:
        # Use the current Python executable to ensure correct environment
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        print("Make sure uvicorn is installed: pip install uvicorn[standard]")
