# Użyj oficjalnego obrazu Pythona
FROM python:3.10

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj pliki
COPY /requirements.txt ./

# Zainstaluj wymagane biblioteki
RUN pip install -r requirements.txt

COPY . /app

# Otwieramy port dla Flask
EXPOSE 9361

CMD ["python", "main.py"]