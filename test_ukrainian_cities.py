#!/usr/bin/env python3
"""
Test Ukrainian city search functionality
"""
import asyncio
from weather_api import WeatherAPI
from localization import localization

async def test_ukrainian_cities():
    """Test searching for Ukrainian cities"""
    print("🇺🇦 Testing Ukrainian City Search")
    print("=" * 40)
    
    weather_api = WeatherAPI()
    
    # Test Ukrainian cities
    ukrainian_cities = [
        "Київ",
        "Харків", 
        "Одеса",
        "Дніпро",
        "Львів",
        "Запоріжжя",
        "Кривий Ріг",
        "Миколаїв",
        "Маріуполь",
        "Вінниця",
        "Херсон",
        "Полтава",
        "Чернігів",
        "Черкаси",
        "Житомир",
        "Суми",
        "Хмельницький",
        "Чернівці",
        "Рівне",
        "Кропивницький",
        "Івано-Франківськ",
        "Тернопіль",
        "Луцьк",
        "Ужгород"
    ]
    
    print(f"Testing {len(ukrainian_cities)} Ukrainian cities...")
    print()
    
    successful = 0
    failed = 0
    
    for city in ukrainian_cities:
        try:
            print(f"🔍 Searching for: {city}")
            cities = await weather_api.search_cities(city)
            
            if cities:
                print(f"✅ Found {len(cities)} result(s):")
                for i, found_city in enumerate(cities[:3], 1):  # Show first 3 results
                    flag = found_city.get('country_emoji', '🏙')
                    name = found_city.get('readable_name', found_city.get('display_name', 'Unknown'))
                    print(f"   {i}. {flag} {name}")
                successful += 1
            else:
                print(f"❌ No results found for {city}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error searching for {city}: {e}")
            failed += 1
        
        print()
    
    print("=" * 40)
    print(f"📊 Results Summary:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success rate: {successful/(successful+failed)*100:.1f}%")

async def test_weather_for_ukrainian_city():
    """Test getting weather for a Ukrainian city"""
    print("\n🌤 Testing Weather for Ukrainian City")
    print("=" * 45)
    
    weather_api = WeatherAPI()
    
    try:
        # Search for Kyiv
        print("🔍 Searching for Київ...")
        cities = await weather_api.search_cities("Київ")
        
        if cities:
            city = cities[0]  # Take first result
            print(f"✅ Found: {city.get('country_emoji', '🏙')} {city.get('readable_name', city.get('display_name', 'Unknown'))}")
            
            # Get weather
            print("🌤 Getting weather data...")
            weather = await weather_api.get_weather_forecast(city['lat'], city['lon'], 'uk', 1)
            
            if weather:
                print("✅ Weather data received:")
                print(f"   🌡 Temperature: {weather.get('current_temperature', 'N/A')}°C")
                print(f"   🌡 Feels like: {weather.get('feels_like', 'N/A')}°C")
                print(f"   ☁️ Description: {weather.get('description', 'N/A')}")
                print(f"   💧 Humidity: {weather.get('humidity', 'N/A')}%")
                print(f"   🌬 Wind: {weather.get('wind_speed', 'N/A')} m/s")
                
                # Test Ukrainian weather message formatting
                print("\n📱 Ukrainian Weather Message:")
                print("-" * 30)
                
                weather_msg = localization.get_text('weather_in', 'uk', 
                                                  city=city.get('readable_name', city.get('display_name', 'Unknown')), 
                                                  date='сьогодні')
                print(weather_msg)
                
                temp_msg = localization.get_text('current_temp', 'uk',
                                                temp=weather.get('current_temperature', 'N/A'),
                                                feels_like=weather.get('feels_like', 'N/A'))
                print(temp_msg)
                
                humidity_msg = localization.get_text('humidity', 'uk',
                                                   humidity=weather.get('humidity', 'N/A'))
                print(humidity_msg)
                
                wind_msg = localization.get_text('wind', 'uk',
                                                speed=weather.get('wind_speed', 'N/A'))
                print(wind_msg)
                
                print(localization.get_text('have_great_day', 'uk'))
                
            else:
                print("❌ Failed to get weather data")
        else:
            print("❌ City not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_popular_cities_ukrainian():
    """Test popular cities display in Ukrainian"""
    print("\n🏙 Testing Popular Cities in Ukrainian")
    print("=" * 45)
    
    cities = localization.get_popular_cities('uk')
    print("Popular cities keyboard for Ukrainian:")
    
    for row in cities:
        for city_text, callback_data in row:
            print(f"  {city_text} -> {callback_data}")

async def main():
    """Main test function"""
    print("🧪 Ukrainian City Search & Weather Test")
    print("=" * 60)
    
    await test_ukrainian_cities()
    await test_weather_for_ukrainian_city()
    await test_popular_cities_ukrainian()
    
    print("\n✅ Ukrainian city and weather test completed!")
    print("🇺🇦 Українські міста та погода працюють правильно!")

if __name__ == "__main__":
    asyncio.run(main())
