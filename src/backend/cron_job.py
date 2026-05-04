"""
Run the script daily to assess the weather and send the reminder to the registered user
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from src.backend.create_db import Create_db

import os 
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIGURATION ==========
# Get free API key from: https://openweathermap.org/api
OPENWEATHER_API_KEY = os.getenv('weather_api_key')

# Gmail credentials
GMAIL_ADDRESS = os.getenv("gmail_id")
GMAIL_APP_PASSWORD = os.getenv("google_app_password")  # Use App Password, not regular password


# Weather thresholds for umbrella recommendation
RAIN_THRESHOLD = 0.15  # 25% chance of rain
RAIN_KEYWORDS = ['rain', 'drizzle', 'thunderstorm', 'shower']
# ===================================


class WeatherEmailAgent:
    """Agent that checks weather and sends email reminders"""
    
    def __init__(self, api_key, recipient_email, user, city, country_code, scheduled_time):

        self.api_key = api_key
        self.user = user
        self.email = recipient_email
        self.city = city
        self.country_code = country_code
        self.scheduled_time = scheduled_time
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        self.current_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self):
        """Fetch current weather and forecast"""
        try:
            params = {
                'q': f"{self.city},{self.country_code}",
                'appid': self.api_key,
                'units': 'metric'  # Use Celsius
            }
        
            #Forecast result
            forecast_response = requests.get(self.forecast_url, params=params)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            #current weather result
            current_response = requests.get(self.current_url, params=params)
            current_response.raise_for_status()
            current_data = current_response.json()
            
            #Filter forcast entries for today
            today = datetime.now().date()
            today_forcasts = []

            for entry in forecast_data['list']:
                forecast_time = datetime.fromtimestamp(entry['dt'])
                if forecast_time.date() == today:
                    today_forcasts.append({
                        'time': forecast_time.strftime('%H:%M'),
                        'weather': entry['weather'][0]['main'].lower(),
                        'description': entry['weather'][0]['description']
                    })

            return {
                'current_description': current_data['weather'][0]['description'],
                'temp': current_data['main']['temp'],
                'humidity': current_data['main']['humidity'],
                'today_forecast': today_forcasts
            }
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None
    
    def should_carry_umbrella(self, weather_data):
        """Decide if umbrella is needed based on weather"""
        if not weather_data:
            return False, "Unable to fetch weather data"
        
       # Check all forecast entries for today
        rain_times = []
        for forecast in weather_data['today_forecasts']:
            if any(keyword in forecast['weather'] for keyword in RAIN_KEYWORDS):
                rain_times.append(f"{forecast['time']} ({forecast['description']})")
        
        if rain_times:
            times_str = ", ".join(rain_times)
            return True, f"Rain expected today at: {times_str}"
    
        return False, "No rain expected today"
    
    def send_email(self, subject, body):
        """Send email via Gmail SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = GMAIL_ADDRESS
            msg['To'] = self.email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            print(f"✓ Email sent successfully at {datetime.now().strftime('%H:%M:%S')}")
            return True
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return False
    
    def run_check(self):
        """Main agent function - check weather and send email if needed"""
        print(f"\n{'='*50}")
        print(f"Weather Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        # Get weather data
        weather = self.get_weather()
        
        if not weather:
            print("Failed to get weather data")
            return
        
        print(f"Location: {self.city}, {self.country_code}")
        print(f"Temperature: {weather['current_temp']}°C")
        print(f"Condition: {weather['current_description']}")
        print(f"Humidity: {weather['current_humidity']}%")
        
        # Decide on umbrella
        need_umbrella, reason = self.should_carry_umbrella(weather)
        
        if need_umbrella:
            subject = "☔ Umbrella Reminder - Take Your Umbrella Today!"
            body = f"""Hello {self.user}!

Your Weather Agent here with an important reminder:

🌧️ DON'T FORGET YOUR UMBRELLA TODAY! 🌧️

Current Weather in {self.city}:
• Condition: {weather['current_description'].title()}
• Temperature: {weather['current_temp']}°C
• Humidity: {weather['current_humidity']}%

Reason: {reason}

Stay dry!

---
Automated message from your Weather Email Agent
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            print(f"\n🌂 Umbrella needed! Sending email...")
            self.send_email(subject, body)
        else:
            print(f"\n☀️ No umbrella needed - {reason}")



def main():
    """Run the agent"""
    print("🤖 Weather Email Agent Starting...")

    current_time = datetime.now().time()
    current_hour = current_time.hour

    db = Create_db()
    users = db.get_all_users()

    for user in users:
        scheduled_hour = int(user['SCHEDULED_TIME'].split(':')[0])

        print(f"Checking user: {user['USER']} - Scheduled Hour: {scheduled_hour} - Current Hour: {current_hour}")

        if current_hour == scheduled_hour:
            # Create agent instance
            agent = WeatherEmailAgent(OPENWEATHER_API_KEY, user['EMAIL'], user['USER'], user['CITY'], user['COUNTRY_CODE'], user['SCHEDULED_TIME'])
            
            # Run check for this user
            agent.run_check()


if __name__ == "__main__":
    main()