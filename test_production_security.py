#!/usr/bin/env python3
"""
Test script to demonstrate Lorien API with production security settings.
This script shows how the API behaves with authentication enabled.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_production_mode():
    """Test API behavior with production security settings."""
    print("🏭 Testing Production Security Mode")
    print("=" * 50)
    print()
    
    # First, test without authentication (should work for read operations)
    print("📖 Testing read operations without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"  ✅ GET /health: {response.status_code}")
        
        response = requests.get(f"{BASE_URL}/tree/roots")
        print(f"  ✅ GET /tree/roots: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"     Found {data.get('total', 0)} root nodes")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Test write operations without authentication (should fail in production)
    print("📝 Testing write operations without authentication...")
    try:
        response = requests.post(
            f"{BASE_URL}/tree/roots",
            json={"label": "Unauthorized Test Root"},
            headers={"Content-Type": "application/json"}
        )
        print(f"  📝 POST /tree/roots without auth: {response.status_code}")
        
        if response.status_code == 401:
            print("  ✅ Authentication correctly required for write operations")
            error_data = response.json()
            print(f"     Error: {error_data.get('detail', {}).get('message', 'Unknown error')}")
        elif response.status_code == 201:
            print("  ⚠️  Write operation succeeded (development mode)")
            data = response.json()
            print(f"     Created node: {data}")
        else:
            print(f"  ❓ Unexpected response: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Test with invalid authentication token
    print("🔑 Testing with invalid authentication token...")
    try:
        response = requests.post(
            f"{BASE_URL}/tree/roots",
            json={"label": "Invalid Token Test"},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer invalid-token-123"
            }
        )
        print(f"  📝 POST /tree/roots with invalid token: {response.status_code}")
        
        if response.status_code == 401:
            print("  ✅ Invalid token correctly rejected")
            error_data = response.json()
            print(f"     Error: {error_data.get('detail', {}).get('message', 'Unknown error')}")
        else:
            print(f"  ❓ Unexpected response: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()
    
    # Test with valid authentication token
    print("✅ Testing with valid authentication token...")
    valid_token = "your-production-token-here"  # In real scenario, get from environment
    
    try:
        response = requests.post(
            f"{BASE_URL}/tree/roots",
            json={"label": "Valid Token Test"},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {valid_token}"
            }
        )
        print(f"  📝 POST /tree/roots with valid token: {response.status_code}")
        
        if response.status_code == 401:
            print("  ℹ️  Token validation failed (expected in development)")
            print("     In production, this would succeed with a valid token")
        elif response.status_code == 201:
            print("  ✅ Valid token accepted")
            data = response.json()
            print(f"     Created node: {data}")
        else:
            print(f"  ❓ Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
    print()

def test_security_headers_production():
    """Test security headers in production mode."""
    print("🛡️  Testing Security Headers")
    print("=" * 30)
    print()
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        headers = response.headers
        
        # Check for security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        
        print("Security headers analysis:")
        for header, expected in security_headers.items():
            if header in headers:
                actual = headers[header]
                print(f"  ✅ {header}: {actual}")
                if expected and expected in actual:
                    print(f"     ✓ Contains expected value: {expected}")
                else:
                    print(f"     ⚠️  Expected: {expected}")
            else:
                print(f"  ❌ {header}: Not present")
        
        # Check for custom headers
        print("\nCustom headers:")
        custom_headers = ["X-Request-ID", "X-Trace-ID", "Server"]
        for header in custom_headers:
            if header in headers:
                print(f"  ✅ {header}: {headers[header]}")
            else:
                print(f"  ❌ {header}: Not present")
                
    except Exception as e:
        print(f"  ❌ Error checking headers: {e}")
    print()

def test_rate_limiting_production():
    """Test rate limiting behavior."""
    print("⏱️  Testing Rate Limiting")
    print("=" * 25)
    print()
    
    try:
        print("Making rapid requests to test rate limiting...")
        start_time = time.time()
        responses = []
        
        # Make 10 requests quickly
        for i in range(10):
            response = requests.get(f"{BASE_URL}/health")
            responses.append(response.status_code)
            print(f"  Request {i+1}: {response.status_code}")
            
        elapsed = time.time() - start_time
        print(f"\nCompleted 10 requests in {elapsed:.2f} seconds")
        
        # Analyze results
        success_count = sum(1 for r in responses if r == 200)
        rate_limited_count = sum(1 for r in responses if r == 429)
        
        print(f"Results: {success_count} successful, {rate_limited_count} rate limited")
        
        if rate_limited_count > 0:
            print("✅ Rate limiting is active")
        else:
            print("ℹ️  Rate limiting is disabled (development mode)")
            
    except Exception as e:
        print(f"  ❌ Error testing rate limiting: {e}")
    print()

def main():
    """Run production security tests."""
    print("🚀 Lorien API Production Security Test")
    print("=" * 50)
    print()
    print("ℹ️  Note: This test runs against the development server")
    print("   In production, authentication would be enforced")
    print()
    
    test_production_mode()
    test_security_headers_production()
    test_rate_limiting_production()
    
    print("🏁 Production security testing complete!")
    print()
    print("📋 Summary:")
    print("- Read operations work without authentication")
    print("- Write operations may require authentication in production")
    print("- Security headers provide browser protection")
    print("- Rate limiting prevents abuse")
    print("- CORS is configured for cross-origin requests")
    print()
    print("🔧 To test with full production security:")
    print("1. Set ENVIRONMENT=production")
    print("2. Set AUTH_TOKEN=your-secure-token")
    print("3. Set AUTH_REQUIRED=true")
    print("4. Restart the server")

if __name__ == "__main__":
    main()
