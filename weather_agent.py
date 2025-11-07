#!/usr/bin/env python3
"""
Weather Email Agent - Sends umbrella reminder based on weather forecast
Free tools: OpenWeatherMap API + Gmail SMTP
"""

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import schedule
import time

import os 
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIGURATION ==========
# Get free API key from: https://openweathermap.org/api
OPENWEATHER_API_KEY = os.getenv('weather_api_key')
CITY = "Mainz"  # Change to your city
COUNTRY_CODE = "DE"  # 2-letter country code

# Gmail credentials
GMAIL_ADDRESS = os.getenv("gmail_id")
GMAIL_APP_PASSWORD = os.getenv("google_app_password")  # Use App Password, not regular password

# Recipient
RECIPIENT_EMAIL = "vivekpadayattil@gmail.com"

# Weather thresholds for umbrella recommendation
RAIN_THRESHOLD = 0.3  # 30% chance of rain
RAIN_KEYWORDS = ['rain', 'drizzle', 'thunderstorm', 'shower']
# ===================================


class WeatherEmailAgent:
    """Agent that checks weather and sends email reminders"""
    
    def __init__(self, api_key, city, country_code):
        self.api_key = api_key
        self.city = city
        self.country_code = country_code
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
            msg['To'] = RECIPIENT_EMAIL
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
            body = f"""Hello Vivek!

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
    
    # Create agent instance
    agent = WeatherEmailAgent(OPENWEATHER_API_KEY, CITY, COUNTRY_CODE)
    
    # Run immediately on start
    agent.run_check()
    
    # Schedule daily check at 7:00 AM
    schedule.every().day.at("16:49").do(agent.run_check)
    
    print("\n⏰ Scheduled daily check at 7:00 AM")
    print("Press Ctrl+C to stop the agent\n")
    
    # Keep the agent running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n👋 Agent stopped by user")


if __name__ == "__main__":
    main()