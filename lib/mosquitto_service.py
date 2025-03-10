from flask import Flask, render_template, jsonify, request
import paho.mqtt.client as mqtt
import json
import requests
import socket
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

gps_data = {
    "latitude": 0.0,  # Decimal degrees (positive for North, negative for South)
    "longitude": 0.0,  # Decimal degrees (positive for East, negative for West)
    "speed_over_ground": 0.0,  # Speed in kilometers per hour
    "course_over_ground": 0.0,  # Course in degrees (0-360, relative to true north)
    "altitude": 0.0,  # Altitude in meters
    "num_satellites": 0.0  # Number of satellites currently used for the fix
}

# Funzione di callback per la connessione
def on_connect(client, userdata, flags, rc, *extra):
    # Gestisci la connessione
    print(f"Connessione riuscita con codice {rc}")
    # Sottoscrizione al topic MQTT
    client.subscribe("test/topic_livio_1997_namo")

# Funzione di callback per la ricezione dei messaggi MQTT
def on_message(client, userdata, message):
    global gps_data
    try:
        data = json.loads(message.payload.decode())
        gps_data.update(data)
        print("Dati ricevuti via MQTT:", data)  # Stampa i dati nella console del server
    except json.JSONDecodeError:
        print("JSON non valido ricevuto.")

# Configurazione del client MQTT
mqtt_client = mqtt.Client(client_id="PCSubscriber", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

broker = "test.mosquitto.org"
port = 1883
topic = "test/topic_livio_1997_namo"

# Connessione al broker MQTT
mqtt_client.connect(broker, 1883)
mqtt_client.loop_start()  # Inizia il loop MQTT per ricevere i messaggi

# Rotta per la homepage

@app.route('/')
def index():
    return render_template('index_iphone.html')  # Serve HTML from the templates folder

@app.route('/update_coordinates', methods=['POST'])
def update_coordinates():
    global gps_data
    data = request.get_json()
    gps_data.update(data)  # Update GPS data
    return jsonify({'status': 'success', 'message': 'Coordinates updated'})

@app.route('/get_coordinates', methods=['GET'])
def get_coordinates():
    return jsonify(gps_data)

port = '5000'
# Start Flask server
local_ip = socket.gethostbyname(socket.gethostname())
app.run(host='0.0.0.0', port=int(port), debug=False, use_reloader=False)
print(f"Server Flask in esecuzione su: http://{local_ip}:{port}")