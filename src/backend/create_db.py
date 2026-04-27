
import sqlite3
import psycopg2

from contextlib import contextmanager

from src.backend.weather_agent import WeatherEmailAgent

import os
from dotenv import load_dotenv

load_dotenv()

# Database setup
DATABASE = "weather.db"

class Create_db:
    def __init__(self):
        """Initialize the database and craet table if it doesn't exist"""
        with self.get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather (
                    EMAIL        TEXT PRIMARY KEY,
                    CITY         TEXT NOT NULL,
                    COUNTRY_CODE TEXT,
                    USER         TEXT,
                    SCHEDULED_TIME         TIME
                )
            """)

    @contextmanager
    def get_db(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(DATABASE)
        """conn = psycopg2.connect(
                host="localhost",
                database="weatherdb",
                user="weatheruser",
                password="yourpassword"
            )"""
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def add_weather(self, user, email, city, country_code, scheduled_time):
        """
        ADD weather data to database
        """
        with self.get_db() as conn:
            conn.execute(
                """
                INSERT INTO weather (user, email, city, country_code, scheduled_time)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user,
                    email,
                    city,
                    country_code,
                    scheduled_time
                )
            )

            print(f'Successfully saved {email}!!')

    def get_all_users(self):
        """Fetch all registered users — useful later for the morning scheduler."""
        with self.get_db() as conn:
            rows = conn.execute("SELECT * FROM weather").fetchall()
            return [dict(row) for row in rows]


    def delete_user(self, email: str):
        """Delete user"""
        with self.get_db() as conn:
            cursor = conn.execute("DELETE FROM users WHERE id = ?", (email,))
            if cursor.rowcount == 0:
                raise ValueError(f"No user found with email: {email}")
