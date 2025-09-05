import asyncio
import aiohttp
from config import settings

async def check_webhook_info():
    """Check current webhook information"""
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/getWebhookInfo"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            
            if data.get("ok"):
                webhook_info = data.get("result", {})
                print("=== Информация о Webhook ===")
                print(f"URL: {webhook_info.get('url', 'НЕ УСТАНОВЛЕН')}")
                print(f"Pending updates: {webhook_info.get('pending_update_count', 0)}")
                print(f"Last error date: {webhook_info.get('last_error_date', 'НЕТ')}")
                print(f"Last error message: {webhook_info.get('last_error_message', 'НЕТ')}")
                print(f"Max connections: {webhook_info.get('max_connections', 'НЕТ')}")
                
                if webhook_info.get('url'):
                    print("✅ Webhook установлен")
                else:
                    print("❌ Webhook НЕ установлен")
                    
                if webhook_info.get('last_error_message'):
                    print(f"⚠️ Последняя ошибка: {webhook_info.get('last_error_message')}")
                    
            else:
                print(f"❌ Ошибка получения информации: {data}")

if __name__ == "__main__":
    asyncio.run(check_webhook_info())
