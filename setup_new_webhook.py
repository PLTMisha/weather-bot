#!/usr/bin/env python3
"""
Setup webhook for new bot @weathertownsbot
"""
import asyncio
from aiogram import Bot
from config import settings

async def setup_new_webhook():
    """Setup webhook for new bot"""
    print("=== Setting up Webhook for @weathertownsbot ===")
    
    bot = Bot(token=settings.telegram_bot_token)
    
    try:
        # Get bot info
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: @{bot_info.username}")
        
        # Set webhook URL
        webhook_url = "https://weather-bot-y5fd.onrender.com/webhook"
        print(f"Setting webhook to: {webhook_url}")
        
        # Delete existing webhook first
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Deleted existing webhook")
        
        # Set new webhook
        result = await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        
        if result:
            print("✅ Webhook set successfully!")
            
            # Get webhook info to verify
            webhook_info = await bot.get_webhook_info()
            print(f"✅ Webhook URL: {webhook_info.url}")
            print(f"✅ Pending updates: {webhook_info.pending_update_count}")
            
            return True
        else:
            print("❌ Failed to set webhook")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up webhook: {e}")
        return False
        
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(setup_new_webhook())
