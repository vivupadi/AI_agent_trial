# Weather Alert Agent

An AI agent that sends a reminder email whether to carry an umbrella(rain probability) and daily Rain forecast to the user-provided mail-id based on the user-provided city and country code.

## Tech Stack

Frontend : HTML/Javascript with nginx.conf (weather sub-domain)

Backend: Python/ SQLite/ FastAPI

Database: SQLite (Persistent volume on the Hetzner server)

Hosted: Hetzner Server using Kubernetes K3 service

## Project Structure

- src
   - backend
     - create_db.py
     - cron_job.py
     - api_server.py
  - frontend
    - index.html
- Dockerfile.api
- Dockerfile.cronjob
- .env
- .gitignore

## Live Demo

[Weather Agent]((https://weather.vivekpadayattil.com/)

## Licenses
