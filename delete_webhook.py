#!/usr/bin/env python3
"""
Script to delete Telegram webhook
"""
import asyncio
from aiogram import Bot
from config import settings

async def delete_webhook():
    """Delete webhook from Telegram"""
    bot = Bot(token=settings.telegram_bot_token)
    
    try:
        # Delete webhook
        result = await bot.delete_webhook(drop_pending_updates=True)
        print(f"Webhook deleted: {result}")
        
        # Get webhook info to confirm
        webhook_info = await bot.get_webhook_info()
        print(f"Current webhook URL: {webhook_info.url}")
        print(f"Pending updates: {webhook_info.pending_update_count}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(delete_webhook())
