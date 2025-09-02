#!/usr/bin/env python3
"""
Test real webhook by sending a message and checking if it's received
"""
import asyncio
import httpx
import time
from datetime import datetime

async def test_real_webhook():
    """Test if webhook receives real messages"""
    print("=== Testing Real Webhook Reception ===")
    print(f"Time: {datetime.now()}")
    print()
    print("ИНСТРУКЦИЯ:")
    print("1. Сейчас отправьте сообщение '/start' вашему боту @mishatgtestbot в Telegram")
    print("2. Подождите 5 секунд")
    print("3. Мы проверим логи на Render")
    print()
    
    input("Нажмите Enter ПОСЛЕ того, как отправили /start боту...")
    
    print("Ждем 3 секунды для обработки...")
    await asyncio.sleep(3)
    
    # Check if webhook endpoint is still working
    print("\nПроверяем webhook endpoint...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test webhook with a simple message
            test_update = {
                "update_id": int(time.time()),
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
                    "date": int(time.time()),
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
            
            response = await client.post(
                "https://weather-bot-y5fd.onrender.com/webhook",
                json=test_update,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Webhook test response: {response.status_code}")
            print(f"Response body: {response.text}")
            
            if response.status_code == 200:
                print("✅ Webhook endpoint отвечает правильно")
            else:
                print("❌ Webhook endpoint возвращает ошибку")
                
    except Exception as e:
        print(f"❌ Ошибка при тестировании webhook: {e}")
    
    print("\nТеперь проверьте логи на Render.com:")
    print("1. Зайдите на https://dashboard.render.com")
    print("2. Откройте ваш сервис weather-bot")
    print("3. Перейдите в раздел 'Logs'")
    print("4. Найдите записи с 'Received webhook update' или ошибки")
    print()
    print("Если в логах НЕТ записей о получении webhook update,")
    print("значит Telegram не отправляет сообщения на наш webhook.")

if __name__ == "__main__":
    asyncio.run(test_real_webhook())
