FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update
RUN apt-get -y install libpq-dev gcc
RUN pip install --no-cache-dir -r requirements.txt
COPY service ./service

RUN useradd --uid 1000 theia && chown -R theia /app
USER theia

EXPOSE 8000
CMD ["gunicorn", "--bind=0.0.0.0:8000", "--log-level=info", "service:app"]