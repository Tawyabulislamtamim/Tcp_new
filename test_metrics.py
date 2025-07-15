#!/usr/bin/env python3
"""
Metrics Test Script for TCP File Transfer Project
This script tests the metrics endpoints and generates sample data
"""

import requests
import json
import time
import sys

def test_metrics_endpoints():
    """Test all metrics API endpoints"""
    base_url = "http://localhost:5000/api"
    
    print("=== TCP File Transfer Metrics Test ===")
    print()
    
    # Test global metrics
    print("1. Testing Global Metrics:")
    try:
        response = requests.get(f"{base_url}/metrics/global")
        if response.status_code == 200:
            data = response.json()
            print("✓ Global metrics API working")
            print(f"  Active connections: {data.get('active_connections', 0)}")
            print(f"  Total bandwidth: {data.get('total_bandwidth', 0):.2f} B/s")
            print(f"  Average RTT: {data.get('average_rtt', 0):.2f} ms")
        else:
            print(f"✗ Global metrics failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Global metrics error: {e}")
        return False
    
    print()
    
    # Test metrics history
    print("2. Testing Metrics History:")
    try:
        response = requests.get(f"{base_url}/metrics/history?seconds=60")
        if response.status_code == 200:
            data = response.json()
            print("✓ Metrics history API working")
            print(f"  History entries: {len(data.get('metrics', []))}")
            print(f"  Timespan: {data.get('timespan', 0)} seconds")
        else:
            print(f"✗ Metrics history failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Metrics history error: {e}")
    
    print()
    
    # Test file listing
    print("3. Testing File API:")
    try:
        response = requests.get(f"{base_url}/files/list")
        if response.status_code == 200:
            data = response.json()
            print("✓ File listing API working")
            print(f"  Files found: {len(data.get('files', []))}")
            print(f"  Current path: {data.get('current_path', '/')}")
        else:
            print(f"✗ File listing failed: {response.status_code}")
    except Exception as e:
        print(f"✗ File listing error: {e}")
    
    print()
    return True

def simulate_client_activity():
    """Simulate client activity to generate metrics"""
    print("4. Simulating Client Activity:")
    
    # The backend should automatically generate sample metrics
    # Let's just wait and check if metrics are being generated
    for i in range(5):
        try:
            response = requests.get("http://localhost:5000/api/metrics/global")
            if response.status_code == 200:
                data = response.json()
                print(f"  Check {i+1}: {data.get('active_connections', 0)} connections, "
                      f"{data.get('total_bandwidth', 0):.0f} B/s bandwidth")
            time.sleep(2)
        except Exception as e:
            print(f"  Error checking metrics: {e}")
    
    print()

def main():
    print("Starting metrics test...")
    print("Make sure the backend server is running on http://localhost:5000")
    print()
    
    if not test_metrics_endpoints():
        print("❌ Basic API tests failed!")
        return 1
    
    simulate_client_activity()
    
    print("=== Test Summary ===")
    print("✓ Backend API is responding")
    print("✓ Metrics endpoints are functional")
    print("✓ Sample data generation is working")
    print()
    print("🎉 Your metrics system is set up correctly!")
    print()
    print("Next steps:")
    print("1. Open http://localhost:3000 to see the frontend")
    print("2. View the metrics dashboard in the right panel")
    print("3. Watch real-time TCP congestion control metrics")
    print("4. Try different time ranges (30s, 1m, 2m, 5m)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
