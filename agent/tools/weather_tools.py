import requests
import schedule
import datetime 
import time
import threading
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = "ebf3ceac853c29bd98273c13a2146f22"


class weatherReminder():
    """Activate/deactivate the reminder"""
    def __init__(self, ):
        self.reminder_time = "07:00"
        self.is_running = False

    def run_reminder(self):
        """Run the reminder"""
        try:
            print(f"⏰ **{datetime.now()}** Good morning! Time for weather!")
            weather = get_current_weather()
            print(f"☀️ {weather}")
            print("-" * 60)
            #return weather

        except Exception as e:
            print(f"❌ Error sending weather reminder: {e}")

    def start(self): 
        # Clear any old schedules
        schedule.clear()
        schedule.every().day.at(self.reminder_time).do(self.run_reminder)


        def run():
            """check whather it's time to send weather"""
            print(f"✅ Weather scheduler started! Reminder set for {self.reminder_time} daily")
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=run, daemon=True)
        self.scheduler_thread.start()


    
    def stop(self):   
        self.is_running = False


scheduler = weatherReminder()    

def start_weather_reminder():
    """Activate weather reminder"""
    scheduler.start()
    return f"✅ Weather reminder at {scheduler.reminder_time}."

def stop_weather_reminder():
    """diactivate  weather reminder"""
    scheduler.stop()
    return  "✅ Weather reminders disabled."

def get_reminder_status():
    """check weather status reminder"""
    if scheduler.is_running:
        status = "Enabled"
    else:
        status = "Disable"
    
    return f"Reminder status {status} and the reminder time is {scheduler.reminder_time}"

# def adjust_reminder_time(new_reminder_time): # change
#     scheduler.reminder_time = new_reminder_time

#     try:
#         if scheduler.is_running:
#             scheduler.clear()
#             schedule.every().day.at(new_reminder_time).do(schedule.send_reminder)

#         else:
#             schedule.start()
#             return f"✅ Weather reminder change to {new_reminder_time} and activated"
#     except ValueError:
#         return "Invalid time format!"


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
    """Get weather for a city"""

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
