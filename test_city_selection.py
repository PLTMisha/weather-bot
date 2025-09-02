#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности выбора городов с эмодзи стран
"""
import asyncio
import logging
from weather_api import weather_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_city_search():
    """Тестирование поиска городов"""
    
    print("🔧 Тестирование системы поиска городов с эмодзи стран")
    print("=" * 60)
    
    # Тестовые города с потенциально множественными результатами
    test_cities = [
        "London",      # Лондон в Англии, Канаде, США
        "Paris",       # Париж во Франции, США, Канаде
        "Moscow",      # Москва в России, США
        "Berlin",      # Берлин в Германии, США
        "Springfield", # Много городов в США
        "Cambridge",   # Кембридж в Англии, США, Канаде
        "York",        # Йорк в Англии, США, Канаде
        "Manchester",  # Манчестер в Англии, США
        "Birmingham",  # Бирмингем в Англии, США
        "Newcastle"    # Ньюкасл в Англии, Австралии, США
    ]
    
    for city_name in test_cities:
        print(f"\n🏙 Поиск города: {city_name}")
        print("-" * 40)
        
        try:
            cities = await weather_api.search_cities(city_name, limit=5)
            
            if not cities:
                print(f"❌ Город '{city_name}' не найден")
                continue
            
            print(f"✅ Найдено {len(cities)} вариантов:")
            
            for i, city in enumerate(cities):
                print(f"   {i+1}. {city['country_emoji']} {city['readable_name']}")
                print(f"      Координаты: {city['lat']:.4f}, {city['lon']:.4f}")
                print(f"      Страна: {city['country']}")
                if city.get('state'):
                    print(f"      Штат/Область: {city['state']}")
                print()
            
        except Exception as e:
            print(f"❌ Ошибка при поиске '{city_name}': {e}")
    
    print("\n🌍 Тестирование эмодзи стран:")
    print("-" * 40)
    
    # Тестирование эмодзи для разных стран
    test_countries = [
        "Russia", "United States", "United Kingdom", "Germany", "France",
        "Canada", "Australia", "Japan", "China", "India", "Brazil",
        "Ukraine", "Kazakhstan", "Belarus", "Poland", "Italy", "Spain"
    ]
    
    for country in test_countries:
        emoji = weather_api._get_country_emoji(country)
        print(f"   {emoji} {country}")


async def test_single_vs_multiple():
    """Тестирование логики одиночного vs множественного выбора"""
    
    print(f"\n🔍 Тестирование логики выбора:")
    print("-" * 40)
    
    # Города с единственным результатом
    single_cities = ["Vladivostok", "Novosibirsk", "Yekaterinburg"]
    
    # Города с множественными результатами
    multiple_cities = ["London", "Paris", "Berlin"]
    
    print("Города с единственным результатом:")
    for city in single_cities:
        cities = await weather_api.search_cities(city, limit=5)
        print(f"   {city}: {len(cities)} результат(ов)")
    
    print("\nГорода с множественными результатами:")
    for city in multiple_cities:
        cities = await weather_api.search_cities(city, limit=5)
        print(f"   {city}: {len(cities)} результат(ов)")


async def test_weather_for_selected_city():
    """Тестирование получения погоды для выбранного города"""
    
    print(f"\n🌤 Тестирование получения погоды:")
    print("-" * 40)
    
    # Найти Лондон в Англии
    cities = await weather_api.search_cities("London", limit=5)
    
    if cities:
        # Выбрать первый результат (обычно самый релевантный)
        london = cities[0]
        print(f"Выбран город: {london['country_emoji']} {london['readable_name']}")
        
        # Получить погоду
        weather_data = await weather_api.get_weather_forecast(
            london["lat"], 
            london["lon"], 
            "ru"
        )
        
        if weather_data:
            print(f"✅ Погода получена:")
            print(f"   Температура: {weather_data['current_temperature']}°C")
            print(f"   Описание: {weather_data['description']}")
            print(f"   Влажность: {weather_data['humidity']}%")
        else:
            print("❌ Не удалось получить данные о погоде")


async def main():
    """Главная функция"""
    try:
        await test_city_search()
        await test_single_vs_multiple()
        await test_weather_for_selected_city()
        
        print("\n✅ Все тесты завершены!")
        
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
    
    finally:
        # Закрыть HTTP клиент
        await weather_api.close()


if __name__ == "__main__":
    asyncio.run(main())
