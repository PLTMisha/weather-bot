#!/usr/bin/env python3
"""
Test new bot @weathertownsbot
"""
import asyncio
import os
from aiogram import Bot

async def test_new_bot():
    """Test new bot connection"""
    print("=== Testing New Bot @weathertownsbot ===")
    
    # Get token from user input
    new_token = input("Введите новый токен для @weathertownsbot: ").strip()
    
    if not new_token:
        print("❌ Токен не введен!")
        return
    
    bot = Bot(token=new_token)
    
    try:
        # Test bot connection
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: @{bot_info.username}")
        print(f"Bot ID: {bot_info.id}")
        print(f"Bot Name: {bot_info.first_name}")
        
        # Check webhook status
        webhook_info = await bot.get_webhook_info()
        print(f"Webhook URL: {webhook_info.url}")
        print(f"Pending updates: {webhook_info.pending_update_count}")
        
        if webhook_info.url:
            print("⚠️  Webhook is set, deleting it for testing...")
            await bot.delete_webhook(drop_pending_updates=True)
            print("✅ Webhook deleted")
        
        # Update .env file
        env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={new_token}

# Database Configuration
DATABASE_URL=sqlite:///./weather_bot.db

# Webhook Configuration (comment out for local development)
# WEBHOOK_URL=https://your-app.onrender.com/webhook

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# Monitoring
BETTER_STACK_TOKEN=your_better_stack_token_here

# Weather API (Optional - Open-Meteo is free)
WEATHER_API_KEY=your_weather_api_key_here
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ .env file updated with new token")
        print(f"✅ New bot @{bot_info.username} is ready for testing!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing new bot: {e}")
        return False
        
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(test_new_bot())
