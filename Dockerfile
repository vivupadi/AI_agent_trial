FROM python:3.10


WORKDIR /app

COPY requirements.txt .

RUN pip install requirements.txt

COPY . /app


EXPOSE 8080

CMD ['python', 'api_server.py']