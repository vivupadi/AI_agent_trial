# Weather Alert Agent

An AI agent that sends reminder email whether to carry an umbrella(rain probability) to the user-provided mail-id based on the user-provided city and country code.

## Tech Stack

Frontend : HTML/Javascript

Backend: Python/ SQLite/ FastAPI

Database: SQLite 

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

[Weather Agent](http://46.225.56.25:31080/)

## Licenses
