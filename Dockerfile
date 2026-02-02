FROM python:3.9-slim

ENV PYTHONWARNINGS=ignore::FutureWarning
ENV PYTHONUNBUFFERED=1
ENV IN_DOCKER=1
ENV TZ=Europe/Brussels

WORKDIR /app


RUN apt-get update \
    && apt-get install -y tzdata \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:8080", "app:app"]
