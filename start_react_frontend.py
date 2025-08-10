#!/usr/bin/env python3
"""
Startup script for React + Next.js frontend
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def main():
    """Start the React frontend development server"""
    
    # Change to react-frontend directory
    frontend_dir = Path(__file__).parent / "react-frontend"
    
    if not frontend_dir.exists():
        print("❌ React frontend directory not found!")
        print("Please ensure the react-frontend directory exists.")
        sys.exit(1)
    
    print("🚀 Starting React + Next.js Frontend...")
    print("=" * 50)
    
    try:
        # Change to frontend directory
        os.chdir(frontend_dir)
        
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        print("🔧 Starting development server...")
        print("Frontend will be available at: http://localhost:3000")
        print("=" * 50)
        
        # Start the development server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open browser
        try:
            webbrowser.open("http://localhost:3000")
            print("🌐 Opened browser at http://localhost:3000")
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print("Please manually open http://localhost:3000")
        
        # Stream output
        for line in process.stdout:
            print(line.strip())
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down React frontend...")
        if 'process' in locals():
            process.terminate()
        sys.exit(0)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting React frontend: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
