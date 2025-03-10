from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
CLOUDFLARE_TUNNEL_URL = "https://your-tunnel.trycloudflare.com/update_coordinates"

@app.route('/update', methods=['POST'])
def proxy():
    try:
        # Inoltra i dati al tunnel Cloudflare via HTTPS
        response = requests.post(
            CLOUDFLARE_TUNNEL_URL,
            json=request.get_json(),
            headers={'Content-Type': 'application/json'}
        )
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)  # Avvia su tutte le interfacce, porta 3000