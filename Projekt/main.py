import os
from weather_requester import WeatherRequester
import threading
from flask import Flask, render_template
import json

# Konfiguracja Flask
app = Flask(__name__)
dir = "data"
os.makedirs(dir, exist_ok=True)
print(f"Folder 'data' utworzony w {dir} lub już istnieje.")  # Potwierdzenie tworzenia folderu

@app.route("/")
def render_html():
    # Wczyt plików JSON
    files = os.listdir(dir)
    data_files = [f for f in files if f.endswith(".json")]
    data_list = []

    # Wczytanie danych z plików
    for file in data_files:
        file_path = os.path.join(dir, file)
        with open(file_path, "r") as f:
            data = json.load(f)
            data_list.append({"filename": file, "content": data})

    return render_template("results.html", data_list=data_list)


if __name__ == "__main__":
    # Pobranie lokalizacji z zmiennych środowiskowych
    location = os.getenv("LOCATION_ID", "2178")

    if location is None:
        raise ValueError("Zmienna środowiskowa 'LOCATION' nie została załadowana.")
    
     # Utworzenie instancji WeatherRequester
    requester = WeatherRequester(location, dir)

    # Uruchomienie WeatherRequester w osobnym wątku
    requester_thread = threading.Thread(target=requester.main)
    requester_thread.daemon = True  # Ustawienie wątku jako daemon (zakończy się wraz z głównym programem)
    requester_thread.start()

    # Uruchomienie serwera Flask
    app.run(host="0.0.0.0", port=9361, debug=True)