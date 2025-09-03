#!/usr/bin/env python3
"""
Test real bot message processing
"""
import asyncio
import httpx
from config import settings

async def test_real_bot_message():
    """Test sending a real message to the bot"""
    print("=== Testing Real Bot Message ===")
    
    # Real webhook URL
    webhook_url = "https://weather-bot-y5fd.onrender.com/webhook"
    
    # Create a proper Telegram update structure
    test_update = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": False,  # This field was missing before!
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
            "date": 1725394800,
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
        async with httpx.AsyncClient() as client:
            print(f"Sending test update to: {webhook_url}")
            print(f"Update data: {test_update}")
            
            response = await client.post(
                webhook_url,
                json=test_update,
                timeout=10
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            
            if response.status_code == 200:
                print("✅ Webhook accepted the message!")
                return True
            else:
                print(f"❌ Webhook returned error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_real_bot_message())
    if success:
        print("\n🎉 Test message sent successfully!")
        print("Check the bot logs to see if it processed correctly.")
    else:
        print("\n❌ Test failed.")
