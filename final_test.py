#!/usr/bin/env python3
"""
Final test of the weather bot
"""
import asyncio
import httpx
import time
from datetime import datetime

async def final_test():
    """Final test of webhook and bot functionality"""
    print("=== Final Weather Bot Test ===")
    print(f"Time: {datetime.now()}")
    print()
    print("ИНСТРУКЦИЯ:")
    print("1. Убедитесь, что токен обновлен на Render.com")
    print("2. Дождитесь перезапуска сервиса (1-2 минуты)")
    print("3. Отправьте /start боту @weathertownsbot")
    print("4. Бот должен ответить меню выбора языка")
    print()
    
    input("Нажмите Enter ПОСЛЕ обновления токена на Render...")
    
    print("Ждем 10 секунд для перезапуска сервиса...")
    await asyncio.sleep(10)
    
    # Test webhook endpoint
    print("\nТестируем webhook endpoint...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test root endpoint
            response = await client.get("https://weather-bot-y5fd.onrender.com/")
            print(f"Root endpoint: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Сервис работает")
                
                # Test webhook with sample update
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
                
                webhook_response = await client.post(
                    "https://weather-bot-y5fd.onrender.com/webhook",
                    json=test_update,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Webhook test: {webhook_response.status_code}")
                
                if webhook_response.status_code == 200:
                    print("✅ Webhook работает")
                else:
                    print("❌ Webhook не работает")
            else:
                print("❌ Сервис не отвечает")
                
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
    
    print("\n" + "="*50)
    print("🎉 ФИНАЛЬНЫЙ ТЕСТ ЗАВЕРШЕН!")
    print("Теперь отправьте /start боту @weathertownsbot")
    print("Если бот ответит - все работает идеально!")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(final_test())
