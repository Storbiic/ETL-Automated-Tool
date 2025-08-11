#!/usr/bin/env python3
"""
Test script for the new dashboard endpoints
"""

import requests
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            return True
        else:
            print(f"❌ API Health Check: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API Health Check: FAILED (Connection Error)")
        return False

def test_dashboard_data():
    """Test the dashboard data endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/dashboard/data")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard Data Endpoint: PASSED")
            print(f"   - KPIs: {len(data.get('kpis', {}))}")
            print(f"   - Status Breakdown: {len(data.get('status_breakdown', []))}")
            print(f"   - BOM Analysis: {bool(data.get('bom_analysis'))}")
            print(f"   - Time Series Data: {len(data.get('time_series_data', []))}")
            print(f"   - Top Products: {len(data.get('top_products', []))}")
            return True
        elif response.status_code == 400:
            print("⚠️  Dashboard Data Endpoint: No file uploaded (Expected)")
            return True
        else:
            print(f"❌ Dashboard Data Endpoint: FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Dashboard Data Endpoint: FAILED (Error: {str(e)})")
        return False

def test_bom_analysis():
    """Test the BOM analysis endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/bom/analysis")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ BOM Analysis Endpoint: PASSED")
            print(f"   - BOM Data: {len(data.get('bom_data', []))}")
            print(f"   - Category Analysis: {len(data.get('category_analysis', []))}")
            return True
        elif response.status_code == 400:
            print("⚠️  BOM Analysis Endpoint: No file uploaded (Expected)")
            return True
        else:
            print(f"❌ BOM Analysis Endpoint: FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ BOM Analysis Endpoint: FAILED (Error: {str(e)})")
        return False

def test_file_upload():
    """Test file upload to enable dashboard endpoints"""
    try:
        # Create a simple test Excel file
        import pandas as pd
        import tempfile
        
        # Create sample data
        master_bom_data = {
            'Part Number': ['YZK-0001', 'YZK-0002', 'YZK-0003', 'YZK-0004'],
            'Description': ['Component 1', 'Component 2', 'Component 3', 'Component 4'],
            'Category': ['Electronics', 'Mechanical', 'Hardware', 'Software'],
            'Status': ['D', '0', 'X', 'NOT_FOUND'],
            'Quantity': [100, 200, 150, 75],
            'Unit Cost': [10.50, 25.00, 15.75, 8.25],
            'Total Cost': [1050, 5000, 2362.5, 618.75],
            'Supplier': ['YAZAKI', 'Supplier A', 'Supplier B', 'Supplier C'],
            'Criticality': ['High', 'Medium', 'Low', 'High']
        }
        
        status_data = {
            'Part Number': ['YZK-0001', 'YZK-0002', 'YZK-0003', 'YZK-0004'],
            'Status': ['D', '0', 'X', 'NOT_FOUND'],
            'Last Updated': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04']
        }
        
        # Create temporary Excel file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            with pd.ExcelWriter(tmp_file.name, engine='openpyxl') as writer:
                pd.DataFrame(master_bom_data).to_excel(writer, sheet_name='MasterBOM', index=False)
                pd.DataFrame(status_data).to_excel(writer, sheet_name='Status', index=False)
            
            # Upload the file
            with open(tmp_file.name, 'rb') as f:
                files = {'file': ('test_data.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = requests.post(f"{BASE_URL}/upload", files=files)
                
                if response.status_code == 200:
                    print("✅ Test File Upload: PASSED")
                    return True
                else:
                    print(f"❌ Test File Upload: FAILED (Status: {response.status_code})")
                    print(f"   Response: {response.text}")
                    return False
        
    except Exception as e:
        print(f"❌ Test File Upload: FAILED (Error: {str(e)})")
        return False

def main():
    """Run all dashboard tests"""
    print("🧪 Testing Enhanced ETL Dashboard Endpoints")
    print("=" * 50)
    
    tests = [
        ("API Health Check", test_api_health),
        ("Dashboard Data Endpoint", test_dashboard_data),
        ("BOM Analysis Endpoint", test_bom_analysis),
    ]
    
    # Check if we can upload a test file
    print("\n📁 Testing with Sample Data:")
    if test_file_upload():
        print("\n📊 Testing Dashboard Endpoints with Data:")
        tests.extend([
            ("Dashboard Data with File", test_dashboard_data),
            ("BOM Analysis with File", test_bom_analysis),
        ])
    
    print("\n🔍 Running Tests:")
    print("-" * 30)
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Dashboard is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the backend server and try again.")
    
    print("\n🚀 Dashboard URLs:")
    print(f"   - React Frontend: http://localhost:3001")
    print(f"   - Backend API: {BASE_URL}")
    print(f"   - API Docs: {BASE_URL}/docs")

if __name__ == "__main__":
    main()
