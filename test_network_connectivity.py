#!/usr/bin/env python3
"""
Test network connectivity to Dream11 team generation site
"""

import requests
import socket
import subprocess
import sys

def test_connectivity():
    """Test various aspects of network connectivity"""
    
    print("🌐 Network Connectivity Test")
    print("=" * 50)
    
    # Test 1: Basic internet connectivity
    print("\n1. Testing basic internet connectivity...")
    try:
        response = requests.get("https://www.google.com", timeout=5)
        print(f"   ✅ Internet connection working (Google: {response.status_code})")
    except Exception as e:
        print(f"   ❌ No internet connection: {e}")
        return False
    
    # Test 2: DNS resolution
    print("\n2. Testing DNS resolution...")
    try:
        ip = socket.gethostbyname("team-generation.netlify.app")
        print(f"   ✅ DNS resolution working (IP: {ip})")
    except Exception as e:
        print(f"   ❌ DNS resolution failed: {e}")
        print("   💡 Try using different DNS servers (8.8.8.8, 1.1.1.1)")
        return False
    
    # Test 3: Direct website access
    print("\n3. Testing website accessibility...")
    try:
        response = requests.get("https://team-generation.netlify.app/", timeout=10)
        print(f"   ✅ Website accessible (Status: {response.status_code})")
        print(f"   📄 Page title: {response.text[:100]}...")
    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL/TLS error: {e}")
        print("   💡 Try accessing http:// version or check certificate")
        return False
    except requests.exceptions.Timeout as e:
        print(f"   ❌ Connection timeout: {e}")
        print("   💡 Website might be slow or down")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection error: {e}")
        print("   💡 Website might be down or blocked")
        return False
    except Exception as e:
        print(f"   ❌ Other error: {e}")
        return False
    
    # Test 4: Ping test
    print("\n4. Testing ping connectivity...")
    try:
        if sys.platform.startswith('win'):
            result = subprocess.run(['ping', '-n', '3', 'team-generation.netlify.app'], 
                                  capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(['ping', '-c', '3', 'team-generation.netlify.app'], 
                                  capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   ✅ Ping successful")
        else:
            print("   ⚠️ Ping failed but website might still work")
    except Exception as e:
        print(f"   ⚠️ Ping test failed: {e}")
    
    # Test 5: Alternative URLs
    print("\n5. Testing alternative access methods...")
    alternative_urls = [
        "http://team-generation.netlify.app/",
        "https://team-generation.netlify.com/",
    ]
    
    for url in alternative_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"   ✅ Alternative URL works: {url} (Status: {response.status_code})")
        except Exception as e:
            print(f"   ❌ Alternative URL failed: {url} - {e}")
    
    print("\n" + "=" * 50)
    print("✅ Network connectivity test completed!")
    print("\n💡 If website is accessible but Chrome fails:")
    print("   1. Try running the script with sudo/administrator privileges")
    print("   2. Disable antivirus/firewall temporarily")
    print("   3. Try using a different network (mobile hotspot)")
    print("   4. Check if your organization blocks automated browsing")
    
    return True

if __name__ == "__main__":
    test_connectivity()