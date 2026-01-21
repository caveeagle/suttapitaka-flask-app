FROM python:3.9-slim

# рабочая директория
WORKDIR /app

# зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# код приложения
COPY . .

# (опционально) чтобы логи сразу шли в stdout
ENV PYTHONUNBUFFERED=1

ENV IN_DOCKER=1

ENV TZ=Europe/Brussels

RUN apt-get update \
    && apt-get install -y tzdata \
    && rm -rf /var/lib/apt/lists/*
    
# порт внутри контейнера
EXPOSE 8000

# запуск
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8000", "app:app"]
