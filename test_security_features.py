#!/usr/bin/env python3
"""
Test script to demonstrate Lorien API security features.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_public_endpoints():
    """Test that public endpoints work without authentication."""
    print("🔍 Testing public endpoints...")
    
    endpoints = ["/health", "/live", "/ready"]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"  ✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"     Response: {json.dumps(data, indent=2)[:100]}...")
        except Exception as e:
            print(f"  ❌ {endpoint}: Error - {e}")
        print()

def test_authentication_required():
    """Test that write operations require authentication in production mode."""
    print("🔐 Testing authentication requirements...")
    
    # Test write operation without auth
    try:
        response = requests.post(
            f"{BASE_URL}/tree/roots",
            json={"label": "Test Root"},
            headers={"Content-Type": "application/json"}
        )
        print(f"  📝 POST /tree/roots without auth: {response.status_code}")
        if response.status_code != 200:
            print(f"     Response: {response.text[:200]}...")
    except Exception as e:
        print(f"  ❌ POST /tree/roots: Error - {e}")
    print()

def test_with_auth_token():
    """Test with authentication token (if available)."""
    print("🎫 Testing with authentication...")
    
    # Generate a test token (in real scenario, this would be set in environment)
    test_token = "test-auth-token-123"
    
    try:
        response = requests.post(
            f"{BASE_URL}/tree/roots",
            json={"label": "Test Root with Auth"},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {test_token}"
            }
        )
        print(f"  📝 POST /tree/roots with auth: {response.status_code}")
        if response.status_code != 200:
            print(f"     Response: {response.text[:200]}...")
        else:
            print(f"     Response: {response.json()}")
    except Exception as e:
        print(f"  ❌ POST /tree/roots with auth: Error - {e}")
    print()

def test_security_headers():
    """Test that security headers are present."""
    print("🛡️  Testing security headers...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        headers = response.headers
        
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Content-Security-Policy",
            "Permissions-Policy"
        ]
        
        print("  Security headers present:")
        for header in security_headers:
            if header in headers:
                print(f"    ✅ {header}: {headers[header]}")
            else:
                print(f"    ❌ {header}: Not present")
                
        # Check for custom headers
        custom_headers = ["X-Request-ID", "X-Trace-ID"]
        print("  Custom headers present:")
        for header in custom_headers:
            if header in headers:
                print(f"    ✅ {header}: {headers[header]}")
            else:
                print(f"    ❌ {header}: Not present")
                
    except Exception as e:
        print(f"  ❌ Error checking headers: {e}")
    print()

def test_rate_limiting():
    """Test rate limiting (if enabled)."""
    print("⏱️  Testing rate limiting...")
    
    try:
        # Make multiple requests quickly
        start_time = time.time()
        responses = []
        
        for i in range(5):
            response = requests.get(f"{BASE_URL}/health")
            responses.append(response.status_code)
            print(f"  Request {i+1}: {response.status_code}")
            
        elapsed = time.time() - start_time
        print(f"  Completed 5 requests in {elapsed:.2f} seconds")
        
        # Check if any were rate limited (429)
        rate_limited = [r for r in responses if r == 429]
        if rate_limited:
            print(f"  ⚠️  Rate limiting active: {len(rate_limited)} requests blocked")
        else:
            print(f"  ℹ️  Rate limiting not active (development mode)")
            
    except Exception as e:
        print(f"  ❌ Error testing rate limiting: {e}")
    print()

def test_cors():
    """Test CORS configuration."""
    print("🌐 Testing CORS configuration...")
    
    try:
        # Test preflight request
        response = requests.options(
            f"{BASE_URL}/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        print(f"  OPTIONS request: {response.status_code}")
        
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods", 
            "Access-Control-Allow-Headers"
        ]
        
        for header in cors_headers:
            if header in response.headers:
                print(f"    ✅ {header}: {response.headers[header]}")
            else:
                print(f"    ❌ {header}: Not present")
                
    except Exception as e:
        print(f"  ❌ Error testing CORS: {e}")
    print()

def main():
    """Run all security tests."""
    print("🚀 Lorien API Security Features Test")
    print("=" * 50)
    print()
    
    test_public_endpoints()
    test_authentication_required()
    test_with_auth_token()
    test_security_headers()
    test_rate_limiting()
    test_cors()
    
    print("🏁 Security testing complete!")
    print()
    print("📝 Notes:")
    print("- In development mode, authentication is optional")
    print("- In production mode, all write operations require Bearer token")
    print("- Rate limiting is disabled in development")
    print("- Security headers are enabled for all responses")
    print("- CORS allows all origins in development")

if __name__ == "__main__":
    main()
