#!/usr/bin/env python3
"""
Script to set up Telegram webhook for the weather bot
"""
import asyncio
import os
import sys
from aiogram import Bot
from config import settings

async def setup_webhook():
    """Set up webhook for Telegram bot"""
    print("=== Setting up Telegram Webhook ===")
    
    # Check if bot token is configured
    if not settings.telegram_bot_token or settings.telegram_bot_token == "your_telegram_bot_token_here":
        print("❌ TELEGRAM_BOT_TOKEN not configured!")
        print("Please set your bot token in Render environment variables")
        return False
    
    # Create bot instance
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

async def check_webhook_status():
    """Check current webhook status"""
    print("\n=== Checking Webhook Status ===")
    
    if not settings.telegram_bot_token or settings.telegram_bot_token == "your_telegram_bot_token_here":
        print("❌ TELEGRAM_BOT_TOKEN not configured!")
        return False
    
    bot = Bot(token=settings.telegram_bot_token)
    
    try:
        webhook_info = await bot.get_webhook_info()
        
        print(f"Webhook URL: {webhook_info.url}")
        print(f"Has custom certificate: {webhook_info.has_custom_certificate}")
        print(f"Pending update count: {webhook_info.pending_update_count}")
        print(f"Last error date: {webhook_info.last_error_date}")
        print(f"Last error message: {webhook_info.last_error_message}")
        print(f"Max connections: {webhook_info.max_connections}")
        print(f"Allowed updates: {webhook_info.allowed_updates}")
        
        if webhook_info.url:
            print("✅ Webhook is configured")
            return True
        else:
            print("❌ No webhook configured")
            return False
            
    except Exception as e:
        print(f"❌ Error checking webhook: {e}")
        return False
        
    finally:
        await bot.session.close()

async def test_bot_connection():
    """Test bot connection and basic functionality"""
    print("\n=== Testing Bot Connection ===")
    
    if not settings.telegram_bot_token or settings.telegram_bot_token == "your_telegram_bot_token_here":
        print("❌ TELEGRAM_BOT_TOKEN not configured!")
        return False
    
    bot = Bot(token=settings.telegram_bot_token)
    
    try:
        # Get bot info
        bot_info = await bot.get_me()
        print(f"✅ Bot ID: {bot_info.id}")
        print(f"✅ Bot Username: @{bot_info.username}")
        print(f"✅ Bot Name: {bot_info.first_name}")
        print(f"✅ Can join groups: {bot_info.can_join_groups}")
        print(f"✅ Can read all group messages: {bot_info.can_read_all_group_messages}")
        print(f"✅ Supports inline queries: {bot_info.supports_inline_queries}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing bot connection: {e}")
        return False
        
    finally:
        await bot.session.close()

async def main():
    """Main function"""
    print("Telegram Bot Webhook Setup Tool")
    print("=" * 40)
    
    # Test bot connection first
    if not await test_bot_connection():
        print("\n💥 Bot connection failed! Check your TELEGRAM_BOT_TOKEN")
        sys.exit(1)
    
    # Check current webhook status
    await check_webhook_status()
    
    # Set up webhook
    if await setup_webhook():
        print("\n🎉 Webhook setup completed successfully!")
        print("\nYour bot should now respond to messages.")
        print("Try sending /start to your bot in Telegram.")
    else:
        print("\n💥 Webhook setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
