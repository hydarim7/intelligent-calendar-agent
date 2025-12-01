import requests
import schedule
import datetime 
import time
import threading
API_KEY = ""



def get_location():
    "Get location from  ipapi.co (1,000 request/day)"
    try: 
        response = requests.get("https://ipapi.co/json/")
        if response.status_code == 200:
            print("✅ Location detect Automatically!")
            result = response.json()
            dic_location = {"city": result.get("city"), "country": result.get("country")}
            return dic_location
        
        elif response.status_code == 429:
            print("⚠️ Rate limit reached, using default location(The staus_code is {response.status_code}).")
            response_ipwhois = requests.get("https://ipwhois.app/json/", timeout=3)
            if response_ipwhois.status_code == 200:
                result = response_ipwhois.json()
                print("✅ Location detected (ipwhois.app backup)")
                dic_location = {"city": result.get("city"), "country": result.get("country")}
            else:
                # Final fallback: Use default
                print("⚠️ All APIs failed, using default location")            
                dic_location =  {"city": "Toronto", "country": "CA"}
        
        return dic_location  

    except Exception as e:
        print(f"Error is *{e}*")
        return None


def get_current_weather(city: str)-> dict:
    """Get current weather conditions for a specific city.
    Args:
        city: City name (e.g., "Ottawa", "Toronto")
    
    Returns:
        dict: Weather data including temperature, conditions, humidity, wind speed or None if request fails
    """
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    if not API_KEY:
        print("❌ OPENWEATHER_API_KEY not found.")
        return None
    
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
    }

    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        print(f"✅ Weather in {city}:{response.json()}")
        return response.json()

    else:
        print(f"Error: {response.status_code}")


    
def get_forecast_summary(city: str = None, days: int = 5):
    """
    Get weather forecast for 1-5 days for a specific city.
    Auto-detects location if city is not provided.
    
    Args:
        Args:
        city: City name (e.g., "Ottawa", "Toronto", "Paris"). 
              If None, automatically detects user's location.
        days: Number of days to forecast (1-5). Default is 5.
              - "tomorrow" = 1
              - "next 3 days" = 3
              - "this week" = 5
              - If not specified = 5
    
    Returns:
        list: Daily weather summaries
    """
    if city is None:
        location = get_location()
        if location:
            city = location.get('city', 'Toronto')
        else:
            city = 'Toronto'

    # Safety check in case days is somehow None
    if days is None:
        days = 5

    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"  

    if not API_KEY:
        print("❌ OPENWEATHER_API_KEY not found.")
        return None
    
    # Validate days parameter
    if days < 1 or days > 5:
        print(f"⚠️ Days must be between 1-5. Using default: 5")
        days = 5

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
    }

    response = requests.get(FORECAST_URL, params=params)
    
    if response.status_code == 200:
        print(f"✅ {days}-day forecast for {city} retrieved")
        forecast_data = response.json()
        
        daily_summaries = {}
        
        # Process the 3-hour interval forecasts
        for item in forecast_data['list']:
            date = item['dt_txt'].split(' ')[0]
            
            if date not in daily_summaries:
                daily_summaries[date] = {
                    'date': date,
                    'temps': [],
                    'conditions': [],
                    'humidity': [],
                    'wind_speed': []
                }
            
            daily_summaries[date]['temps'].append(item['main']['temp'])
            daily_summaries[date]['conditions'].append(item['weather'][0]['description'])
            daily_summaries[date]['humidity'].append(item['main']['humidity'])
            daily_summaries[date]['wind_speed'].append(item['wind']['speed'])
        
        # Calculate daily averages
        result = []
        for date, data in list(daily_summaries.items())[:days]:
            result.append({
                'date': date,
                'avg_temp': round(sum(data['temps']) / len(data['temps'])),      
                'min_temp': round(min(data['temps'])),                            
                'max_temp': round(max(data['temps'])),                            
                'condition': max(set(data['conditions']), key=data['conditions'].count),
                'avg_humidity': round(sum(data['humidity']) / len(data['humidity'])),
                'avg_wind_speed': round(sum(data['wind_speed']) / len(data['wind_speed']), 1)  
            })
        
        return result
    else:
        print(f"Error: {response.status_code}")
        return None
    
   