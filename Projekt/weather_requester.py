import os
import json
import time
from openaq import OpenAQ
import paho.mqtt.client as mqtt

# Parametry MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER", "167.172.164.168")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "261833/Del Norte")  # Wildcard, aby subskrybować wszystkie podtematy
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "student")  # Użytkownik
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "sys-wbud")  # Hasło

class WeatherRequester:
    def __init__(self, location_id, data_dir):
        self.location_id = location_id
        self.client = OpenAQ(api_key='c66941448a7e701684ce55bda3cfa427472edb16422d1502c8711f4455af86cc')
        self.data_dir = data_dir  
        os.makedirs(self.data_dir, exist_ok=True)  # Sprawdzanie lokalizacji zapisu
        self.mqtt_client = mqtt.Client()

    #Podłączamy do mqtt
    def mqtt_init(self):
        self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.on_message = self.subscribe_indeks
        self.mqtt_client.subscribe(MQTT_TOPIC)  # subskrybcja tematu
        self.mqtt_client.loop_start()
        print("Połączono z brokerem MQTT")
    
    #Zbiera dane od innych studentów
    def subscribe_indeks(self, client, userdata, msg):  # zapis do pliku 
        try:
            topic_parts = msg.topic.split("/")
            if len(topic_parts) != 2:
                print(f"Nieprawidłowy topik: {msg.topic}")
                return

            nr_indeksu, lokalizacja = topic_parts
            lokalizacja = lokalizacja.replace(" ","_")
            data = msg.payload.decode("utf-8")
            filename = os.path.join(self.data_dir, f"{nr_indeksu}-{lokalizacja}.json")  # 

            with open(filename, "w") as file: 
                json.dump(data, file, indent=4)
            
            print(f"Dane z {msg.topic} zapisane do {filename}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    #Publikujemy dane z pomocą mqtt
    def send_to_mqtt(self, data):
        try:
            data_to_send = json.dumps(data)
            self.mqtt_client.publish(MQTT_TOPIC, data_to_send)
            print(f"Wysłano dane do MQTT")
        except Exception as e:
            print(f"Error wysłania danych do MQTT: {e}")

    #Odbiera dane z API i je zapisuje 
    def fetch_and_save_data(self):
        try:
            location = self.client.locations.get(self.location_id)
            latest = self.client.locations.latest(self.location_id)
            name = location.results[0].name
            date = location.results[0].datetime_last.utc
            end = len(location.results[0].sensors)

            values = []
            for i in range(0, end):
                sensor_name = location.results[0].sensors[i].name
                sensor_value = latest.results[i].value
                values.append({sensor_name: sensor_value})

            data = {
                "location": name,
                "timestamp": date,
                "values": values
            }

            # Formatowanie i drukowanie danych
            student_id = "261833"
            place = name.replace(" ","_")
            filename = os.path.join(self.data_dir, f"{student_id}-{place}.json")  # 

            with open(filename, "w") as file: 
                json.dump(data, file, indent=4)
            
            print(f"Dane zapisane do {filename}")
            return data

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            return json.dumps({"error": f"Error fetching sensor data: {str(e)}"})

    def main(self):
        self.mqtt_init()
        while True:
            data = self.fetch_and_save_data()
            self.send_to_mqtt(data)
            print(data)
            time.sleep(30)  # Odczekanie 30 sekund