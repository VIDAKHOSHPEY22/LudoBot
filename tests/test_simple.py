"""
Network Connection Test Module
Simple test to check if the bot can connect to Telegram's API servers.
"""

import socket
import ssl
import sys


def test_telegram_connection():
    """
    Test the connection to Telegram's API servers.
    Checks both basic connectivity and SSL/TLS handshake.
    """
    print("=" * 50)
    print("🔍 Testing Telegram API Connection")
    print("=" * 50)
    
    # Test 1: Basic TCP connection to api.telegram.org on port 443 (HTTPS)
    print("\n📡 Test 1: TCP Connection Test")
    try:
        # Try to establish a TCP connection to Telegram's API server
        socket.create_connection(("api.telegram.org", 443), timeout=5)
        print("   ✅ Port 443 is open! Basic connection successful.")
        connection_success = True
    except socket.gaierror:
        print("   ❌ DNS resolution failed. Cannot resolve api.telegram.org")
        print("   💡 Possible causes:")
        print("      - DNS server is not responding")
        print("      - Network connectivity issues")
        print("      - Firewall blocking DNS queries")
        return False
    except socket.timeout:
        print("   ❌ Connection timed out. Telegram API is not responding.")
        print("   💡 Possible causes:")
        print("      - Network is slow or unstable")
        print("      - Firewall is blocking the connection")
        print("      - Telegram API is temporarily down")
        return False
    except ConnectionRefusedError:
        print("   ❌ Connection refused. Telegram API may be down.")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False
    
    # Test 2: SSL/TLS Handshake (if basic connection succeeded)
    if connection_success:
        print("\n🔐 Test 2: SSL/TLS Handshake Test")
        try:
            # Create a secure SSL/TLS connection
            context = ssl.create_default_context()
            with socket.create_connection(("api.telegram.org", 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname="api.telegram.org") as secure_sock:
                    print("   ✅ SSL/TLS handshake successful!")
                    print(f"   🔒 Cipher: {secure_sock.cipher()}")
                    print(f"   🌐 Certificate: {secure_sock.getpeercert().get('subject', [['Unknown']])[0][0][1]}")
        except ssl.SSLError as e:
            print(f"   ❌ SSL/TLS error: {e}")
            print("   💡 Possible causes:")
            print("      - SSL certificate verification failed")
            print("      - System time is incorrect")
            return False
        except Exception as e:
            print(f"   ❌ SSL/TLS handshake failed: {e}")
            return False
    
    # Test 3: API Endpoint (if previous tests passed)
    print("\n🌐 Test 3: API Endpoint Test")
    try:
        import urllib.request
        import json
        
        # Test with a simple API call
        url = "https://api.telegram.org/bot"
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"   ✅ API endpoint is reachable!")
            print(f"   📊 HTTP Status: {response.status}")
            print(f"   📁 Server: {response.headers.get('Server', 'Unknown')}")
    except Exception as e:
        print(f"   ⚠️ API endpoint test: {e}")
        print("   💡 This is normal if you don't have a valid bot token configured")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("   ✅ DNS Resolution: PASSED")
    print(f"   ✅ TCP Connection: PASSED")
    print("   ✅ SSL/TLS: PASSED")
    print("=" * 50)
    print("\n🎉 Connection to Telegram API is working!")
    print("💡 Your bot should be able to connect to Telegram.")
    
    return True


def test_dns_resolution():
    """
    Additional test: Check DNS resolution specifically.
    """
    print("\n🔍 Test 4: DNS Resolution Test")
    try:
        import socket
        ip_addresses = socket.gethostbyname_ex("api.telegram.org")
        print(f"   ✅ Domain resolves to IPs: {ip_addresses[2]}")
        return True
    except Exception as e:
        print(f"   ❌ DNS resolution failed: {e}")
        return False


def test_port_connectivity(host: str = "api.telegram.org", port: int = 443):
    """
    Test connectivity to a specific host and port.
    
    Args:
        host: Hostname to connect to
        port: Port number to test
    """
    print(f"\n📡 Test 5: Specific Port Test ({host}:{port})")
    try:
        socket.create_connection((host, port), timeout=5)
        print(f"   ✅ Port {port} is open on {host}")
        return True
    except Exception as e:
        print(f"   ❌ Could not connect to {host}:{port} - {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Ludo Bot - Network Connection Test")
    print("=" * 60)
    
    # Run all tests
    results = []
    
    # Test 1: DNS Resolution
    print("\n" + "=" * 60)
    print("🌐 Testing Network Connectivity...")
    print("=" * 60)
    
    # Test DNS first
    dns_ok = test_dns_resolution()
    results.append(("DNS Resolution", dns_ok))
    
    # Test main connection
    main_ok = test_telegram_connection()
    results.append(("Main Connection", main_ok))
    
    # Test specific ports
    port_ok = test_port_connectivity()
    results.append(("Port 443", port_ok))
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! Your network is ready for the bot.")
        print("💡 You can now run the bot with: python run.py")
    else:
        print("\n⚠️ Some tests failed. Please check your network settings.")
        print("   💡 Common fixes:")
        print("      - Check your internet connection")
        print("      - Disable VPN or firewall temporarily")
        print("      - Try using a different DNS server (e.g., 8.8.8.8)")
        print("      - Contact your network administrator")
    
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)