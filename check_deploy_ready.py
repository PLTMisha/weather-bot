#!/usr/bin/env python3
"""
Скрипт проверки готовности к деплою на Render.com
"""

import os
import sys
from pathlib import Path

def check_file_exists(filename: str, required: bool = True) -> bool:
    """Проверить существование файла"""
    exists = Path(filename).exists()
    status = "✅" if exists else ("❌" if required else "⚠️")
    requirement = "ОБЯЗАТЕЛЬНО" if required else "ОПЦИОНАЛЬНО"
    print(f"{status} {filename} - {requirement}")
    return exists

def check_file_content(filename: str, required_content: list) -> bool:
    """Проверить содержимое файла"""
    if not Path(filename).exists():
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing = []
        for item in required_content:
            if item not in content:
                missing.append(item)
        
        if missing:
            print(f"⚠️  {filename} - отсутствует: {', '.join(missing)}")
            return False
        else:
            print(f"✅ {filename} - содержимое корректно")
            return True
            
    except Exception as e:
        print(f"❌ {filename} - ошибка чтения: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("🔍 Проверка готовности Weather Bot к деплою на Render.com")
    print("=" * 60)
    
    all_good = True
    
    # Проверка основных файлов
    print("\n📁 Основные файлы:")
    required_files = [
        "main.py",
        "bot.py", 
        "weather_api.py",
        "database.py",
        "config.py",
        "localization.py",
        "scheduler.py",
        "monitoring.py",
        "requirements.txt",
        "render.yaml"
    ]
    
    for file in required_files:
        if not check_file_exists(file, required=True):
            all_good = False
    
    # Проверка опциональных файлов
    print("\n📄 Документация и инструкции:")
    optional_files = [
        "README.md",
        "RENDER_DEPLOY_GUIDE.md",
        "QUICK_DEPLOY.md",
        ".env.production",
        ".gitignore"
    ]
    
    for file in optional_files:
        check_file_exists(file, required=False)
    
    # Проверка содержимого render.yaml
    print("\n⚙️ Конфигурация Render:")
    render_content = [
        "type: web",
        "env: python", 
        "buildCommand",
        "startCommand",
        "uvicorn main:app",
        "TELEGRAM_BOT_TOKEN",
        "DATABASE_URL",
        "WEBHOOK_URL"
    ]
    
    if not check_file_content("render.yaml", render_content):
        all_good = False
    
    # Проверка requirements.txt
    print("\n📦 Зависимости Python:")
    requirements_content = [
        "fastapi",
        "aiogram",
        "uvicorn",
        "sqlalchemy",
        "alembic",
        "psycopg2-binary",
        "apscheduler",
        "httpx",
        "structlog"
    ]
    
    if not check_file_content("requirements.txt", requirements_content):
        all_good = False
    
    # Проверка main.py
    print("\n🚀 Веб-сервер:")
    main_content = [
        "FastAPI",
        "lifespan",
        "/webhook",
        "/health",
        "uvicorn"
    ]
    
    if not check_file_content("main.py", main_content):
        all_good = False
    
    # Проверка bot.py
    print("\n🤖 Telegram Bot:")
    bot_content = [
        "aiogram",
        "_get_weather_emoji",
        "handle_hourly_forecast",
        "handle_daily_forecast"
    ]
    
    if not check_file_content("bot.py", bot_content):
        all_good = False
    
    # Проверка .gitignore
    print("\n🔒 Git конфигурация:")
    if Path(".gitignore").exists():
        gitignore_content = [".env", "__pycache__", "*.pyc"]
        check_file_content(".gitignore", gitignore_content)
    else:
        print("⚠️  .gitignore отсутствует - создай для безопасности")
    
    # Финальный результат
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 ВСЕ ГОТОВО К ДЕПЛОЮ!")
        print("\n📋 Следующие шаги:")
        print("1. Создай Telegram бота через @BotFather")
        print("2. Загрузи код на GitHub")
        print("3. Создай веб-сервис на Render.com")
        print("4. Добавь переменные окружения")
        print("5. Создай PostgreSQL базу данных")
        print("6. Настрой BetterStack мониторинг")
        print("\n📖 Подробная инструкция: RENDER_DEPLOY_GUIDE.md")
        print("⚡ Быстрый старт: QUICK_DEPLOY.md")
        return 0
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ! Исправь ошибки выше перед деплоем.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
