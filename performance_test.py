#!/usr/bin/env python3
"""
Advanced Performance Testing for Questionnaire Management System
"""

import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor
import statistics

BASE_URL = "https://sb-4uc1nby759cn.vercel.run"

def test_endpoint(endpoint, method="GET", data=None, headers=None):
    """Test a single endpoint and return response time"""
    url = f"{BASE_URL}{endpoint}"
    start_time = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "response_time_ms": round(response_time, 2),
            "success": response.status_code < 400,
            "content_length": len(response.content)
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status_code": 0,
            "response_time_ms": 0,
            "success": False,
            "error": str(e)
        }

def run_performance_tests():
    """Run comprehensive performance tests"""
    print("🚀 ADVANCED PERFORMANCE TESTING")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        {"endpoint": "/", "method": "GET"},
        {"endpoint": "/auth/login", "method": "GET"},
        {"endpoint": "/auth/register", "method": "GET"},
        {"endpoint": "/questionnaires", "method": "GET"},
        {"endpoint": "/questionnaire/1", "method": "GET"},
        {"endpoint": "/api/questionnaire/1/respond", "method": "POST", 
         "data": {"answers": {"1": ["option1"], "6": ["riab cardiologica"]}},
         "headers": {"Content-Type": "application/json"}},
    ]
    
    results = []
    
    print("Testing individual endpoints...")
    for test_config in endpoints:
        result = test_endpoint(
            test_config["endpoint"], 
            test_config.get("method", "GET"),
            test_config.get("data"),
            test_config.get("headers")
        )
        results.append(result)
        
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} {result['endpoint']}: {result['response_time_ms']}ms (HTTP {result.get('status_code', 'ERR')})")
    
    # Concurrent testing
    print(f"\n🔄 CONCURRENT LOAD TESTING")
    print("-" * 30)
    
    def load_test_homepage():
        return test_endpoint("/")
    
    # Test with multiple concurrent requests
    concurrent_results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(load_test_homepage) for _ in range(20)]
        for future in futures:
            concurrent_results.append(future.result())
    
    successful_requests = [r for r in concurrent_results if r["success"]]
    response_times = [r["response_time_ms"] for r in successful_requests]
    
    if response_times:
        print(f"Total Requests: {len(concurrent_results)}")
        print(f"Successful: {len(successful_requests)}")
        print(f"Average Response Time: {statistics.mean(response_times):.2f}ms")
        print(f"Median Response Time: {statistics.median(response_times):.2f}ms")
        print(f"Min Response Time: {min(response_times):.2f}ms")
        print(f"Max Response Time: {max(response_times):.2f}ms")
        print(f"95th Percentile: {sorted(response_times)[int(0.95 * len(response_times))]:.2f}ms")
    
    # API-specific testing
    print(f"\n🔧 API ENDPOINT TESTING")
    print("-" * 30)
    
    api_tests = [
        {
            "name": "Single Choice Response",
            "data": {"answers": {"1": ["option1"]}}
        },
        {
            "name": "Multiple Choice Response", 
            "data": {"answers": {"1": ["option1", "option2"]}}
        },
        {
            "name": "Complete Medical Survey",
            "data": {"answers": {"1": ["option1"], "6": ["riab cardiologica", "riab respiratoria"]}}
        }
    ]
    
    for test in api_tests:
        result = test_endpoint(
            "/api/questionnaire/1/respond", 
            "POST", 
            test["data"],
            {"Content-Type": "application/json"}
        )
        status_icon = "✅" if result["success"] else "❌"
        print(f"{status_icon} {test['name']}: {result['response_time_ms']}ms")
        if not result["success"]:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    print(f"\n📊 PERFORMANCE SUMMARY")
    print("=" * 50)
    
    successful_tests = [r for r in results if r["success"]]
    if successful_tests:
        all_response_times = [r["response_time_ms"] for r in successful_tests]
        print(f"🎯 Overall Success Rate: {len(successful_tests)}/{len(results)} ({len(successful_tests)/len(results)*100:.1f}%)")
        print(f"⚡ Average Response Time: {statistics.mean(all_response_times):.2f}ms")
        print(f"🏆 Best Response Time: {min(all_response_times):.2f}ms")
        print(f"📈 System Performance: {'EXCELLENT' if statistics.mean(all_response_times) < 100 else 'GOOD' if statistics.mean(all_response_times) < 500 else 'NEEDS_IMPROVEMENT'}")
    
    return results

if __name__ == "__main__":
    results = run_performance_tests()