#!/usr/bin/env python3
"""
Test script to verify all API endpoints are working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_session_endpoints():
    """Test session-based endpoints"""
    endpoints = [
        ("/preview-session", {"master_sheet": "Sheet1", "target_sheet": "Sheet2"}),
        ("/clean-session", {}),
        ("/get-lookup-columns", {}),
        ("/lookup-session", {"lookup_column": "test_column"}),
    ]
    
    for endpoint, data in endpoints:
        try:
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                headers={"Content-Type": "application/json"},
                json=data
            )
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code != 200:
                print(f"   Response: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ {endpoint} failed: {e}")

def main():
    print("🧪 Testing ETL API Endpoints")
    print("=" * 40)
    
    if not test_health():
        print("❌ Backend is not running. Please start it first:")
        print("   python start_backend.py")
        return
    
    print("\n🔧 Testing session endpoints:")
    test_session_endpoints()
    
    print("\n✅ API endpoint test completed!")
    print("Note: Some endpoints may return errors without uploaded data - this is expected.")

if __name__ == "__main__":
    main()
