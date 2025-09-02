#!/usr/bin/env python3
"""
Test webhook functionality by sending a test update
"""
import asyncio
import json
import httpx
from config import settings

async def test_webhook():
    """Test webhook endpoint"""
    print("=== Testing Webhook Endpoint ===")
    
    webhook_url = "https://weather-bot-y5fd.onrender.com/webhook"
    
    # Create a test update (simulating Telegram sending /start command)
    test_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
                "language_code": "en"
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser",
                "type": "private"
            },
            "date": 1640995200,
            "text": "/start",
            "entities": [
                {
                    "offset": 0,
                    "length": 6,
                    "type": "bot_command"
                }
            ]
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"Sending test update to: {webhook_url}")
            
            response = await client.post(
                webhook_url,
                json=test_update,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            
            if response.status_code == 200:
                print("✅ Webhook is working!")
                return True
            else:
                print(f"❌ Webhook returned error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

async def test_health_endpoint():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    
    health_url = "https://weather-bot-y5fd.onrender.com/health"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(health_url)
            
            print(f"Health status: {response.status_code}")
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed")
                print(f"Status: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return False

async def test_root_endpoint():
    """Test root endpoint"""
    print("\n=== Testing Root Endpoint ===")
    
    root_url = "https://weather-bot-y5fd.onrender.com/"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(root_url)
            
            print(f"Root status: {response.status_code}")
            
            if response.status_code == 200:
                root_data = response.json()
                print(f"✅ Root endpoint working")
                print(f"Message: {root_data.get('message', 'unknown')}")
                print(f"Version: {root_data.get('version', 'unknown')}")
                return True
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error checking root: {e}")
        return False

async def main():
    """Main test function"""
    print("Webhook Functionality Test")
    print("=" * 30)
    
    # Test all endpoints
    root_ok = await test_root_endpoint()
    health_ok = await test_health_endpoint()
    webhook_ok = await test_webhook()
    
    print("\n" + "=" * 30)
    print("Test Results:")
    print(f"Root endpoint: {'✅ OK' if root_ok else '❌ FAIL'}")
    print(f"Health endpoint: {'✅ OK' if health_ok else '❌ FAIL'}")
    print(f"Webhook endpoint: {'✅ OK' if webhook_ok else '❌ FAIL'}")
    
    if all([root_ok, health_ok, webhook_ok]):
        print("\n🎉 All tests passed! Your bot should be working.")
    else:
        print("\n💥 Some tests failed. Check the logs above.")

if __name__ == "__main__":
    asyncio.run(main())
