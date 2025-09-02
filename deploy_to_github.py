#!/usr/bin/env python3
"""
Скрипт для быстрого деплоя Weather Bot на GitHub
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description=""):
    """Выполнить команду и показать результат"""
    print(f"🔄 {description}")
    print(f"   Команда: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Успешно!")
            if result.stdout.strip():
                print(f"   Вывод: {result.stdout.strip()}")
        else:
            print(f"❌ Ошибка: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False
    
    print()
    return True

def check_git_installed():
    """Проверить установлен ли git"""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except:
        return False

def main():
    """Основная функция"""
    print("🚀 Быстрый деплой Weather Bot на GitHub")
    print("=" * 50)
    
    # Проверка git
    if not check_git_installed():
        print("❌ Git не установлен! Установи git и попробуй снова.")
        return 1
    
    # Получение информации от пользователя
    print("\n📝 Введи информацию для GitHub:")
    
    username = input("GitHub username: ").strip()
    if not username:
        print("❌ Username обязателен!")
        return 1
    
    repo_name = input("Название репозитория (по умолчанию: weather-bot): ").strip()
    if not repo_name:
        repo_name = "weather-bot"
    
    description = input("Описание репозитория (опционально): ").strip()
    if not description:
        description = "Telegram Weather Bot with daily notifications and multi-language support"
    
    print(f"\n📋 Информация:")
    print(f"   Username: {username}")
    print(f"   Репозиторий: {repo_name}")
    print(f"   Описание: {description}")
    print(f"   URL: https://github.com/{username}/{repo_name}")
    
    confirm = input("\n✅ Продолжить? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', 'да', 'д']:
        print("❌ Отменено пользователем")
        return 1
    
    print("\n🔧 Начинаю деплой...")
    
    # Шаг 1: Инициализация git репозитория
    if not run_command("git init", "Инициализация git репозитория"):
        return 1
    
    # Шаг 2: Добавление всех файлов
    if not run_command("git add .", "Добавление всех файлов"):
        return 1
    
    # Шаг 3: Первый коммит
    commit_message = "Initial commit: Weather Bot with emojis and multi-language support"
    if not run_command(f'git commit -m "{commit_message}"', "Создание первого коммита"):
        return 1
    
    # Шаг 4: Переименование ветки в main
    if not run_command("git branch -M main", "Переименование ветки в main"):
        return 1
    
    # Шаг 5: Добавление remote origin
    remote_url = f"https://github.com/{username}/{repo_name}.git"
    if not run_command(f"git remote add origin {remote_url}", "Добавление remote origin"):
        return 1
    
    print("🎯 Git репозиторий готов!")
    print("\n📋 Следующие шаги:")
    print("1. Создай репозиторий на GitHub:")
    print(f"   - Перейди на https://github.com/new")
    print(f"   - Repository name: {repo_name}")
    print(f"   - Description: {description}")
    print(f"   - Выбери Public")
    print(f"   - НЕ добавляй README, .gitignore или license (у нас уже есть)")
    print(f"   - Нажми 'Create repository'")
    print()
    print("2. После создания репозитория выполни:")
    print(f"   git push -u origin main")
    print()
    print("3. Или запусти этот скрипт еще раз с параметром --push")
    
    # Опция для автоматического push
    if len(sys.argv) > 1 and sys.argv[1] == "--push":
        print("\n🚀 Выполняю push на GitHub...")
        if run_command("git push -u origin main", "Push на GitHub"):
            print("🎉 Успешно загружено на GitHub!")
            print(f"🔗 Репозиторий: https://github.com/{username}/{repo_name}")
        else:
            print("❌ Ошибка при push. Убедись что репозиторий создан на GitHub.")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
