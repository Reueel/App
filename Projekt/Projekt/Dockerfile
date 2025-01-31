# Użyj oficjalnego obrazu Pythona
FROM python:3.10

ENV PYTHONUNBUFFERED 1

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj pliki
COPY /requirements.txt ./

# Zainstaluj wymagane biblioteki
RUN pip install -r requirements.txt

COPY . /app

COPY templates /app/templates

# Otwieramy port dla Flask
EXPOSE 9361

#CMD ["python", "main.py"]