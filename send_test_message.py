#!/usr/bin/env python3
"""
Send a test message to the bot to trigger webhook
"""
import asyncio
from aiogram import Bot
from config import settings

async def send_test_message():
    """Send a test message to trigger webhook"""
    print("=== Sending Test Message to Bot ===")
    
    bot = Bot(token=settings.telegram_bot_token)
    
    try:
        # Get bot info
        bot_info = await bot.get_me()
        print(f"Bot: @{bot_info.username}")
        
        # Get webhook info
        webhook_info = await bot.get_webhook_info()
        print(f"Webhook URL: {webhook_info.url}")
        print(f"Pending updates: {webhook_info.pending_update_count}")
        
        if webhook_info.pending_update_count > 0:
            print(f"⚠️  There are {webhook_info.pending_update_count} pending updates!")
            print("This means Telegram has messages waiting to be processed.")
            
            # Try to get updates manually
            print("\nTrying to get pending updates...")
            updates = await bot.get_updates()
            
            if updates:
                print(f"Found {len(updates)} pending updates:")
                for update in updates:
                    if update.message:
                        print(f"- Message from {update.message.from_user.first_name}: {update.message.text}")
                    else:
                        print(f"- Update type: {type(update)}")
            else:
                print("No updates found via get_updates()")
        else:
            print("✅ No pending updates")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
        
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(send_test_message())
