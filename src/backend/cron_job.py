def initialize_db():



def send_mail():


def send_telegram_msg():
#!/usr/bin/env python3
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
RAIN_THRESHOLD = 0.25  # 25% chance of rain
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
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def get_weather(self):
        """Fetch current weather and forecast"""
        try:
            params = {
                'q': f"{self.city},{self.country_code}",
                'appid': self.api_key,
                'units': 'metric'  # Use Celsius
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            #breakpoint()
            
            return {
                'description': data['weather'][0]['description'],
                'main': data['weather'][0]['main'].lower(),
                'temp': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'rain_probability': data.get('clouds', {}).get('all', 0) / 100  # Cloud coverage as proxy
            }
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None
    
    def should_carry_umbrella(self, weather_data):
        """Decide if umbrella is needed based on weather"""
        if not weather_data:
            return False, "Unable to fetch weather data"
        
        weather_main = weather_data['main']
        description = weather_data['description']
        
        # Check if it's raining or likely to rain
        if any(keyword in weather_main for keyword in RAIN_KEYWORDS):
            return True, f"It's currently {description}"
        
        # Check if it's cloudy/high chance of rain
        if weather_data['rain_probability'] > RAIN_THRESHOLD:
            return True, f"High chance of rain - {description}"
        
        return False, f"Clear weather - {description}"
    
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
        print(f"Temperature: {weather['temp']}°C")
        print(f"Condition: {weather['description']}")
        print(f"Humidity: {weather['humidity']}%")
        
        # Decide on umbrella
        need_umbrella, reason = self.should_carry_umbrella(weather)
        
        if need_umbrella:
            subject = "☔ Umbrella Reminder - Take Your Umbrella Today!"
            body = f"""Hello {self.user}!

Your Weather Agent here with an important reminder:

🌧️ DON'T FORGET YOUR UMBRELLA TODAY! 🌧️

Current Weather in {self.city}:
• Condition: {weather['description'].title()}
• Temperature: {weather['temp']}°C
• Humidity: {weather['humidity']}%

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

        if current_hour == scheduled_hour:
            # Create agent instance
            agent = WeatherEmailAgent(OPENWEATHER_API_KEY, user['EMAIL'], user['USER'], user['CITY'], user['COUNTRY_CODE'], user['SCHEDULED_TIME'])
            
            # Run check for this user
            agent.run_check()


if __name__ == "__main__":
    main()