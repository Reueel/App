import os
from weather_requester import WeatherRequester
import threading
from flask import Flask, render_template
import json
import paho.mqtt.client as mqtt

# Parametry MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER", "167.172.164.168")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = "+/+"  # Wildcard, aby subskrybować wszystkie podtematy
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "student")  # Użytkownik
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "sys-wbud")  # Hasło


# Konfiguracja Flask
app = Flask(__name__)
mqtt_client = mqtt.Client()
dir = "data"
os.makedirs(dir, exist_ok=True)
print(f"Folder 'data' utworzony w {dir} lub już istnieje.")  # Potwierdzenie tworzenia folderu

def mqtt_init():
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_connect = test
    mqtt_client.on_message = subscribe_indeks
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.subscribe(MQTT_TOPIC)  # subskrybcja tematu
    mqtt_client.loop_start()
    print("Połączono z brokerem MQTT")

# testuje połączenie
def test(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully!")
    else:
        print(f"Connection failed with code {rc}")

    #Zbiera dane od innych studentów
    #on_message
def subscribe_indeks(client, userdata, msg):  # zapis do pliku 
    try:
        topic_parts = msg.topic.split("/")
        if len(topic_parts) != 2:
            print(f"Nieprawidłowy topik: {msg.topic}")
            return

        nr_indeksu, lokalizacja = topic_parts
        lokalizacja = lokalizacja.replace(" ","_")
        data = msg.payload.decode("utf-8")
        filename = os.path.join(dir, f"{nr_indeksu}-{lokalizacja}.json")  # 

        with open(filename, "w") as file: 
            json.dump(data, file, indent=4)
           
        print(f"Dane z {msg.topic} zapisane do {filename}")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print("Except {e}")

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
    location = os.getenv("LOCATION", "2178")
    
    mqtt_init()
    '''
    # Utworzenie instancji WeatherRequester
    requester = WeatherRequester(location, dir)
    # Uruchomienie WeatherRequester w osobnym wątku
    requester_thread = threading.Thread(target=requester.main)
    requester_thread.daemon = True  # Ustawienie wątku jako daemon (requester to while true loop więc ustawiając go jako daemon to wylaczymy go z zamknieciem main)
    requester_thread.start()
    '''
    # Uruchomienie serwera Flask
    app.run(host="0.0.0.0", port=9361, debug=True)