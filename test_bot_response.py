import asyncio
import aiohttp
from config import settings

async def send_test_message():
    """Send a test message to the bot"""
    # Get bot info first
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getMe"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            
            if data.get("ok"):
                bot_info = data.get("result", {})
                print(f"✅ Бот подключен: @{bot_info.get('username')}")
                print(f"✅ ID бота: {bot_info.get('id')}")
                print(f"✅ Имя бота: {bot_info.get('first_name')}")
                
                # Check webhook status
                webhook_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getWebhookInfo"
                async with session.get(webhook_url) as webhook_response:
                    webhook_data = await webhook_response.json()
                    
                    if webhook_data.get("ok"):
                        webhook_info = webhook_data.get("result", {})
                        print(f"✅ Webhook URL: {webhook_info.get('url')}")
                        print(f"✅ Pending updates: {webhook_info.get('pending_update_count', 0)}")
                        
                        if webhook_info.get('url'):
                            print("\n🎉 Бот готов к работе!")
                            print("Попробуйте отправить /start боту в Telegram")
                        else:
                            print("❌ Webhook не установлен")
                    else:
                        print(f"❌ Ошибка получения webhook: {webhook_data}")
            else:
                print(f"❌ Ошибка подключения к боту: {data}")

if __name__ == "__main__":
    asyncio.run(send_test_message())
