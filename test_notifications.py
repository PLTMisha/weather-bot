#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы уведомлений
"""
import asyncio
import logging
from datetime import datetime, time

from database import DatabaseManager, init_db
from scheduler import notification_scheduler
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_notifications():
    """Тестирование системы уведомлений"""
    
    print("🔧 Инициализация базы данных...")
    await init_db()
    
    # Получить текущее время
    now = datetime.now()
    current_time_str = now.strftime("%H:%M")
    
    print(f"⏰ Текущее время: {current_time_str}")
    
    # Проверить пользователей с уведомлениями на текущее время
    users = await DatabaseManager.get_users_for_notification(current_time_str)
    print(f"👥 Найдено пользователей с уведомлениями на {current_time_str}: {len(users)}")
    
    for user in users:
        print(f"   - Пользователь {user.user_id}: {user.city}, язык: {user.language}")
    
    # Проверить пользователей на ближайшие 15-минутные интервалы
    test_times = []
    for minute in [0, 15, 30, 45]:
        test_time = now.replace(minute=minute, second=0, microsecond=0)
        test_times.append(test_time.strftime("%H:%M"))
    
    print(f"\n🔍 Проверка пользователей на 15-минутные интервалы:")
    for test_time in test_times:
        users = await DatabaseManager.get_users_for_notification(test_time)
        print(f"   {test_time}: {len(users)} пользователей")
    
    # Проверить статус планировщика
    print(f"\n📅 Статус планировщика:")
    try:
        status = notification_scheduler.get_scheduler_status()
        print(f"   Запущен: {status.get('running', False)}")
        print(f"   Количество задач: {status.get('job_count', 0)}")
        
        # Показать ближайшие задачи
        jobs = status.get('jobs', [])
        if jobs:
            print("   Ближайшие задачи:")
            for job in jobs[:5]:
                print(f"     - {job['name']}: {job.get('next_run', 'не запланировано')}")
    except Exception as e:
        print(f"   Ошибка получения статуса: {e}")
    
    return users


async def send_test_notification_to_user(user_id: int):
    """Отправить тестовое уведомление пользователю"""
    print(f"\n📤 Отправка тестового уведомления пользователю {user_id}...")
    
    try:
        user = await DatabaseManager.get_user(user_id)
        if not user:
            print(f"❌ Пользователь {user_id} не найден")
            return
        
        print(f"✅ Пользователь найден: {user.city}, время: {user.notification_time}")
        
        # Отправить тестовое уведомление
        await notification_scheduler.send_test_notification(user_id)
        print(f"✅ Тестовое уведомление отправлено!")
        
    except Exception as e:
        print(f"❌ Ошибка отправки уведомления: {e}")


async def check_user_settings(user_id: int):
    """Проверить настройки пользователя"""
    print(f"\n👤 Проверка настроек пользователя {user_id}...")
    
    user = await DatabaseManager.get_user(user_id)
    if not user:
        print(f"❌ Пользователь {user_id} не найден")
        return
    
    print(f"   Город: {user.city}")
    print(f"   Координаты: {user.city_lat}, {user.city_lon}")
    print(f"   Время уведомлений: {user.notification_time}")
    print(f"   Уведомления включены: {user.notifications_enabled}")
    print(f"   Язык: {user.language}")
    print(f"   Создан: {user.created_at}")
    print(f"   Обновлен: {user.updated_at}")


async def main():
    """Главная функция"""
    print("🚀 Запуск тестирования системы уведомлений")
    print("=" * 50)
    
    # Тестирование базовой функциональности
    users = await test_notifications()
    
    # Если есть пользователи, можно протестировать отправку
    if users:
        user_id = users[0].user_id
        await check_user_settings(user_id)
        
        # Спросить, отправить ли тестовое уведомление
        print(f"\n❓ Отправить тестовое уведомление пользователю {user_id}? (y/n): ", end="")
        try:
            # В реальном окружении можно использовать input()
            # Для автоматического тестирования пропускаем
            print("Пропускаем интерактивный ввод...")
        except:
            pass
    else:
        print("\n⚠️  Пользователей с активными уведомлениями не найдено")
        print("   Убедитесь, что:")
        print("   1. Пользователь настроил город")
        print("   2. Пользователь включил уведомления")
        print("   3. Время уведомлений соответствует текущему времени или ближайшему 15-минутному интервалу")
    
    print("\n✅ Тестирование завершено")


if __name__ == "__main__":
    asyncio.run(main())
