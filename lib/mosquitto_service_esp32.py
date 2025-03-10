from flask import Flask, render_template, jsonify, request
import paho.mqtt.client as mqtt
import json
import socket
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Abilita CORS per tutte le route

# Dizionario unificato per memorizzare i dati
gps_data = {
    "latitude": 0.0,
    "longitude": 0.0,
    "speed_over_ground": 0.0,
    "course_over_ground": 0.0,
    "altitude": 0.0,
    "num_satellites": 0,
    "voltage": 0.0,
    "current": 0.0,
    "avg_voltage": 0.0,
    "avg_current": 0.0,
    "battery_percentage": 0.0,
    "last_update": "N/A"
}

import os

# Funzione per salvare i dati della batteria in un file JSON
def save_battery_data(data):
    # Crea il file se non esiste
    if not os.path.exists("battery_data.json"):
        with open("battery_data.json", "w") as file:
            json.dump([], file)  # Inizializza con una lista vuota

    # Leggi i dati esistenti
    with open("battery_data.json", "r") as file:
        existing_data = json.load(file)

    # Aggiungi i nuovi dati con un timestamp
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "voltage": data.get("voltage", 0.0),
        "avg_voltage": data.get("avg_voltage", 0.0),
        "current": data.get("current", 0.0),
        "avg_current": data.get("avg_current", 0.0)
    }
    existing_data.append(new_entry)

    # Scrivi i dati aggiornati nel file
    with open("battery_data.json", "w") as file:
        json.dump(existing_data, file, indent=4)

# Callback per la connessione MQTT
def on_connect(client, userdata, flags, rc, *extra):
    print(f"Connessione riuscita con codice {rc}")
    client.subscribe("dispositivo/batteria")
    client.subscribe("dispositivo/gps")


def on_message(client, userdata, message):
    global gps_data
    try:
        payload = json.loads(message.payload.decode())

        if message.topic == "dispositivo/gps":
            updated_data = {
                "last_update": datetime.now().strftime("%d %b %Y, %H:%M:%S")
            }
            # Aggiorna latitude e longitude se presenti
            if "latitude" in payload and payload["latitude"] is not None:
                updated_data["latitude"] = payload["latitude"]
            if "longitude" in payload and payload["longitude"] is not None:
                updated_data["longitude"] = payload["longitude"]
            # Aggiorna course_over_ground se presente
            if "course_over_ground" in payload and payload["course_over_ground"] is not None:
                updated_data["course_over_ground"] = payload["course_over_ground"]
            # Aggiorna num_satellites, speed_over_ground e altitude solo se presenti
            if "num_satellites" in payload and payload["num_satellites"] is not None:
                updated_data["num_satellites"] = payload["num_satellites"]
            if "speed_over_ground" in payload and payload["speed_over_ground"] is not None:
                updated_data["speed_over_ground"] = payload["speed_over_ground"]
            if "altitude" in payload and payload["altitude"] is not None:
                updated_data["altitude"] = payload["altitude"]

            gps_data.update(updated_data)
            print("Dati GPS ricevuti via MQTT:", updated_data)

        elif message.topic == "dispositivo/batteria":
            gps_data.update(payload)  # Aggiorna i dati della batteria
            print("Dati batteria ricevuti via MQTT:", payload)

            # Salva i dati della batteria in un file JSON
            save_battery_data(payload)

    except json.JSONDecodeError:
        print("JSON non valido ricevuto.")


# Configurazione del client MQTT
mqtt_client = mqtt.Client(client_id="PCSubscriber", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

broker = "test.mosquitto.org"
port = 1883

# Connessione al broker MQTT
mqtt_client.connect(broker, port)
mqtt_client.loop_start()


# Route Flask per servire la pagina principale
@app.route('/')
def index():
    return render_template('index_iphone.html')


# Route per aggiornare le coordinate via POST
@app.route('/update_coordinates', methods=['POST'])
def update_coordinates():
    global gps_data
    data = request.get_json()
    gps_data.update(data)
    return jsonify({'status': 'success', 'message': 'Coordinates updated'})


# Route per ottenere i dati GPS attuali
@app.route('/get_coordinates', methods=['GET'])
def get_coordinates():
    return jsonify(gps_data)


# Avvia il server Flask
port = 7676
local_ip = socket.gethostbyname(socket.gethostname())
app.run(host='0.0.0.0', port=int(port), debug=False, use_reloader=False)
print(f"Server Flask in esecuzione su: http://{local_ip}:{port}")
