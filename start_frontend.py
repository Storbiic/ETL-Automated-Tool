"""
Startup script for Streamlit frontend
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    print("🎨 Starting Streamlit frontend on http://localhost:8501")
    print("Make sure the backend is running on http://localhost:8000")
    print("Press Ctrl+C to stop the application")
    print("-" * 50)

    try:
        # Start Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "frontend/app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Frontend application stopped")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        print("Make sure streamlit is installed: pip install streamlit")
