import os
import json
import time
from openaq import OpenAQ
import paho.mqtt.client as mqtt

# Parametry MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER", "167.172.164.168")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "261833/Del_Norte")  # Nazwa pliku
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "student")  # Użytkownik
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "sys-wbud")  # Hasło

class WeatherRequester:
    def __init__(self, location_id, data_dir):
        self.location_id = location_id
        self.client = OpenAQ(api_key='KEY')
        self.data_dir = data_dir  
        os.makedirs(self.data_dir, exist_ok=True)  # Sprawdzanie lokalizacji zapisu
        #self.mqtt_client = mqtt.Client()
        self.mqtt_client = None

    #Publikujemy dane z pomocą mqtt
    def send_to_mqtt(self, data):
        try:
            self.mqtt_client.username_pw_set(MQTT_USERNAME,MQTT_PASSWORD)
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
            self.mqtt_client.loop_start()
            time.sleep(1)
            data_to_send = json.dumps(data)
            topic = MQTT_TOPIC.replace(" ","_")
            self.mqtt_client.publish(topic, data_to_send)
            #self.mqtt_client.loop_stop()
            #self.mqtt_client.disconnect()
            self.mqtt_client.enable_logger()
            print(f"Wysłano dane do MQTT")
        except Exception as e:
            print(f"Error wysłania danych do MQTT: {e}")

    #Odbiera dane z API i je zapisuje 
    def fetch_data(self):
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

            return data

        except Exception as e:
            return json.dumps({"error": f"Error fetching sensor data: {str(e)}"})

    def main(self):
        print("Zbieram dane")
        data = self.fetch_data()
        self.send_to_mqtt(data)
        print(data)
        time.sleep(30)  # Odczekanie 30 sekund

print("before main")
if __name__ == "__main__":
    location = os.getenv("LOCATION", "2178")
    dir = "data"
    requester = WeatherRequester(location, dir)
    while True:
        requester.main()
