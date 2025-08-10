#!/usr/bin/env python3
"""
Debug script to test the enhanced ETL workflow with insights
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test API health"""
    print("🔍 Testing API Health...")
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Health: {response.status_code} - {response.json()}")
    return response.status_code == 200

def test_upload_simulation():
    """Simulate file upload by checking existing files"""
    print("\n🔍 Testing File Upload (checking existing files)...")
    
    # Test preview to see if files exist
    response = requests.post(
        f"{BASE_URL}/preview-session",
        headers={"Content-Type": "application/json"},
        json={"master_sheet": "MasterBOM", "target_sheet": "Sheet2"}
    )
    
    print(f"Preview test: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Files available: {result.get('success', False)}")
        return True
    else:
        print(f"❌ No files available: {response.text}")
        return False

def test_clean_data():
    """Test data cleaning"""
    print("\n🔍 Testing Data Cleaning...")
    
    response = requests.post(
        f"{BASE_URL}/clean-session",
        headers={"Content-Type": "application/json"},
        json={}
    )
    
    print(f"Clean: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Cleaning successful: {result.get('success', False)}")
        if 'master_shape' in result:
            print(f"   Master shape: {result['master_shape']}")
        if 'target_shape' in result:
            print(f"   Target shape: {result['target_shape']}")
        return True
    else:
        print(f"❌ Cleaning failed: {response.text}")
        return False

def test_column_insights():
    """Test new column insights endpoint"""
    print("\n🔍 Testing Column Insights (NEW)...")
    
    response = requests.post(
        f"{BASE_URL}/column-insights",
        headers={"Content-Type": "application/json"},
        json={}
    )
    
    print(f"Column Insights: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Column insights generated: {result.get('success', False)}")
        
        if 'insights' in result:
            insights = result['insights']
            master = insights.get('master_sheet_analysis', {})
            target = insights.get('target_sheet_analysis', {})
            
            print(f"   Master: {master.get('total_rows', 0)} rows, {master.get('total_columns', 0)} cols")
            print(f"   Target: {target.get('total_rows', 0)} rows, {target.get('total_columns', 0)} cols")
            print(f"   YAZAKI PN: {master.get('yazaki_pn_column', False)}")
            
        return True
    else:
        print(f"❌ Column insights failed: {response.text}")
        return False

def test_lookup():
    """Test lookup operation"""
    print("\n🔍 Testing Lookup Operation...")
    
    # First get available columns
    response = requests.post(
        f"{BASE_URL}/get-lookup-columns",
        headers={"Content-Type": "application/json"},
        json={}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get lookup columns: {response.text}")
        return False
    
    columns = response.json().get('columns', [])
    if not columns:
        print("❌ No lookup columns available")
        return False
    
    lookup_column = columns[0]  # Use first available column
    print(f"   Using lookup column: {lookup_column}")
    
    # Perform lookup
    response = requests.post(
        f"{BASE_URL}/lookup-session",
        headers={"Content-Type": "application/json"},
        json={"lookup_column": lookup_column}
    )
    
    print(f"Lookup: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Lookup successful: {result.get('success', False)}")
        
        if 'total_records' in result:
            print(f"   Total records: {result['total_records']}")
        if 'successful_matches' in result:
            print(f"   Successful matches: {result['successful_matches']}")
        if 'failed_matches' in result:
            print(f"   Failed matches: {result['failed_matches']}")
            
        return True
    else:
        print(f"❌ Lookup failed: {response.text}")
        return False

def test_lookup_insights():
    """Test new lookup insights endpoint"""
    print("\n🔍 Testing Lookup Insights (NEW)...")
    
    response = requests.post(
        f"{BASE_URL}/lookup-insights",
        headers={"Content-Type": "application/json"},
        json={}
    )
    
    print(f"Lookup Insights: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Lookup insights generated: {result.get('success', False)}")
        
        if 'insights' in result:
            insights = result['insights']
            summary = insights.get('lookup_summary', {})
            quality = insights.get('data_quality_insights', {})
            recommendations = insights.get('recommendations', [])
            
            print(f"   Total records: {summary.get('total_records', 0)}")
            print(f"   Match rate: {quality.get('match_rate', 0)}%")
            print(f"   Active parts: {quality.get('active_parts', 0)}")
            print(f"   Inactive parts: {quality.get('inactive_parts', 0)}")
            print(f"   Unknown parts: {quality.get('unknown_parts', 0)}")
            print(f"   Recommendations: {len(recommendations)}")
            
        return True
    else:
        print(f"❌ Lookup insights failed: {response.text}")
        return False

def main():
    """Run complete workflow test"""
    print("🧪 ETL Enhanced Workflow Debug Test")
    print("=" * 50)
    
    # Test each step
    steps = [
        ("API Health", test_health),
        ("File Upload/Preview", test_upload_simulation),
        ("Data Cleaning", test_clean_data),
        ("Column Insights", test_column_insights),
        ("Lookup Operation", test_lookup),
        ("Lookup Insights", test_lookup_insights),
    ]
    
    results = {}
    
    for step_name, test_func in steps:
        try:
            results[step_name] = test_func()
            time.sleep(1)  # Brief pause between tests
        except Exception as e:
            print(f"❌ {step_name} failed with exception: {e}")
            results[step_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Test Results Summary:")
    print("=" * 50)
    
    for step_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{step_name:20} {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Enhanced workflow is working!")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
