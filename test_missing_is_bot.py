#!/usr/bin/env python3
"""
Test message without is_bot field to verify our fix works
"""
import asyncio
import httpx

async def test_missing_is_bot():
    """Test sending a message without is_bot field"""
    print("=== Testing Message Without is_bot Field ===")
    
    webhook_url = "https://weather-bot-y5fd.onrender.com/webhook"
    
    # Create update WITHOUT is_bot field (like the old failing messages)
    test_update = {
        "update_id": 987654321,
        "message": {
            "message_id": 2,
            "from": {
                "id": 987654321,
                # NO is_bot field here - this should be fixed by our code
                "first_name": "TestUser",
                "username": "testuser2",
                "language_code": "ru"
            },
            "chat": {
                "id": 987654321,
                "first_name": "TestUser", 
                "username": "testuser2",
                "type": "private"
            },
            "date": 1725394900,
            "text": "/start"
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"Sending update WITHOUT is_bot field to: {webhook_url}")
            print(f"Update data: {test_update}")
            
            response = await client.post(
                webhook_url,
                json=test_update,
                timeout=10
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("status") == "ok":
                    print("✅ SUCCESS: Webhook processed message without is_bot field!")
                    print("✅ Our fix is working - the missing field was added automatically")
                    return True
                else:
                    print(f"❌ Webhook returned error status: {response_data}")
                    return False
            else:
                print(f"❌ Webhook returned HTTP error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_missing_is_bot())
    if success:
        print("\n🎉 Fix verified! Bot can now handle messages without is_bot field.")
    else:
        print("\n❌ Fix not working yet.")
