#!/usr/bin/env python3
"""
Тест для проверки работы LocationIQ API
"""
import asyncio
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from weather_api import weather_api
from config import settings

async def test_locationiq():
    """Тестируем LocationIQ API"""
    print("🌍 Тестирование LocationIQ API...")
    
    if not settings.locationiq_api_key:
        print("❌ LocationIQ API ключ не настроен!")
        print("💡 Добавьте LOCATIONIQ_API_KEY в файл .env")
        return False
    
    print(f"🔑 LocationIQ API ключ: {'*' * 10}{settings.locationiq_api_key[-4:]}")
    
    test_cities = [
        "Полтава",
        "Киев", 
        "Лондон",
        "New York",
        "Paris"
    ]
    
    success_count = 0
    total_tests = len(test_cities)
    
    for city in test_cities:
        print(f"\n🔍 Поиск города: {city}")
        try:
            results = await weather_api.search_cities(city, limit=3)
            
            if results:
                print(f"✅ Найдено {len(results)} результатов:")
                for i, result in enumerate(results, 1):
                    emoji = result.get('country_emoji', '🌍')
                    readable_name = result.get('readable_name', result['display_name'])
                    print(f"  {i}. {emoji} {readable_name} ({result['lat']:.4f}, {result['lon']:.4f})")
                success_count += 1
            else:
                print(f"❌ Результаты не найдены для города: {city}")
                
        except Exception as e:
            print(f"❌ Ошибка при поиске {city}: {e}")
    
    print(f"\n📊 Результат теста: {success_count}/{total_tests} городов найдено")
    
    if success_count == total_tests:
        print("🎉 LocationIQ API работает корректно!")
        return True
    elif success_count > 0:
        print("⚠️ LocationIQ API работает частично")
        return True
    else:
        print("❌ LocationIQ API не работает")
        return False

async def test_weather():
    """Тестируем получение погоды"""
    print("\n🌤️ Тестирование получения погоды для Полтавы...")
    
    try:
        # Получаем координаты Полтавы
        coords = await weather_api.get_city_coordinates("Полтава")
        
        if not coords:
            print("❌ Не удалось получить координаты для Полтавы")
            return False
        
        lat, lon, display_name = coords
        print(f"📍 Координаты: {lat:.4f}, {lon:.4f}")
        print(f"🏙️ Название: {display_name}")
        
        # Получаем погоду
        weather = await weather_api.get_weather_forecast(lat, lon, "ru", 1)
        
        if weather:
            print("✅ Погода получена:")
            print(f"  🌡️ Температура: {weather['current_temperature']}°C")
            print(f"  🤔 Ощущается: {weather['feels_like']}°C")
            print(f"  📝 Описание: {weather['description']}")
            print(f"  💧 Влажность: {weather['humidity']}%")
            print(f"  💨 Ветер: {weather['wind_speed']} м/с")
            print(f"  ☔ Вероятность дождя: {weather['rain_probability']}%")
            return True
        else:
            print("❌ Не удалось получить данные о погоде")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при получении погоды: {e}")
        return False

async def main():
    """Главная функция"""
    print("🚀 Запуск тестирования LocationIQ и погоды...\n")
    
    try:
        # Тестируем LocationIQ
        locationiq_ok = await test_locationiq()
        
        # Тестируем погоду
        weather_ok = await test_weather()
        
        print(f"\n🏁 Тестирование завершено:")
        print(f"  LocationIQ: {'✅' if locationiq_ok else '❌'}")
        print(f"  Погода: {'✅' if weather_ok else '❌'}")
        
        if locationiq_ok and weather_ok:
            print("\n🎉 Все тесты пройдены успешно!")
            return True
        else:
            print("\n⚠️ Некоторые тесты не прошли")
            return False
            
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        return False
    finally:
        # Закрываем соединения
        await weather_api.close()

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {e}")
        sys.exit(1)
