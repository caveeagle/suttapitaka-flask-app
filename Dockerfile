FROM python:3.9-slim

ENV PYTHONWARNINGS=ignore::FutureWarning
ENV PYTHONUNBUFFERED=1
ENV IN_DOCKER=1
ENV TZ=Europe/Brussels

WORKDIR /app


RUN apt-get update \
    && apt-get install -y tzdata curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN curl -fL "https://media.githubusercontent.com/media/caveeagle/suttapitaka-flask-app/master/sutta-pitaka.sqlite" \
    -o /app/sutta-pitaka.sqlite \
    && ls -la /app/sutta-pitaka.sqlite

EXPOSE 8080

CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:8080", "app:app"]
