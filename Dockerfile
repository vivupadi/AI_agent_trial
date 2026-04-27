FROM python:3.10


WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app


EXPOSE 8080

CMD ["python", "-m", "src.backend.cron_job"]