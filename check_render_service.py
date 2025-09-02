#!/usr/bin/env python3
"""
Check Render service status
"""
import asyncio
import httpx

async def check_render_service():
    """Check if Render service is working"""
    print("=== Проверка сервиса на Render ===")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check root endpoint
            print("Проверяем root endpoint...")
            response = await client.get("https://weather-bot-y5fd.onrender.com/")
            print(f"Root endpoint: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Service status: {data.get('status', 'unknown')}")
                print("✅ Сервис работает")
                
                # Test webhook endpoint
                print("\nТестируем webhook endpoint...")
                test_data = {
                    "update_id": 123,
                    "message": {
                        "message_id": 1,
                        "from": {"id": 123, "first_name": "Test"},
                        "chat": {"id": 123, "type": "private"},
                        "date": 1234567890,
                        "text": "/start"
                    }
                }
                
                webhook_response = await client.post(
                    "https://weather-bot-y5fd.onrender.com/webhook",
                    json=test_data
                )
                print(f"Webhook test: {webhook_response.status_code}")
                print(f"Webhook response: {webhook_response.text}")
                
                if webhook_response.status_code == 200:
                    print("✅ Webhook отвечает")
                else:
                    print("❌ Webhook не работает")
                    
                # Check health endpoint
                print("\nПроверяем health endpoint...")
                health_response = await client.get("https://weather-bot-y5fd.onrender.com/health")
                print(f"Health endpoint: {health_response.status_code}")
                
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    print(f"Health status: {health_data.get('status', 'unknown')}")
                else:
                    print("❌ Health endpoint не работает")
                    
            else:
                print("❌ Сервис не отвечает")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_render_service())
