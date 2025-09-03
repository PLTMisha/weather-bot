import asyncio
import aiohttp
from config import settings

async def check_webhook():
    async with aiohttp.ClientSession() as session:
        url = f'https://api.telegram.org/bot{settings.telegram_bot_token}/getWebhookInfo'
        async with session.get(url) as resp:
            data = await resp.json()
            print("=== Webhook Info ===")
            print(f"URL: {data['result'].get('url', 'Not set')}")
            print(f"Has custom certificate: {data['result'].get('has_custom_certificate', False)}")
            print(f"Pending update count: {data['result'].get('pending_update_count', 0)}")
            print(f"Last error date: {data['result'].get('last_error_date', 'None')}")
            print(f"Last error message: {data['result'].get('last_error_message', 'None')}")
            print(f"Max connections: {data['result'].get('max_connections', 'None')}")
            print(f"Allowed updates: {data['result'].get('allowed_updates', 'None')}")

if __name__ == "__main__":
    asyncio.run(check_webhook())
