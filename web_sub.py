# web_sub.py
from flask import Flask, request, jsonify
import requests
import base64
import json5
from functions import get_broadcaster_id
import secrets
app = Flask(__name__)

# Load configuration
with open('config.json5', 'r') as config_file:
    config = json5.load(config_file)

@app.route('/eventsub', methods=['POST'])
def eventsub():
    data = request.get_json()
    print("Received EventSub notification:", data)
    return jsonify({"status": "success"}), 200

def run_eventsub_app():
    app.run(port=5777, use_reloader=False, debug=False)

def subscribe_to_eventsub():
    url = 'https://api.twitch.tv/helix/eventsub/subscriptions'
    headers = {
        'Client-ID': 'q7nvallmbbgvk66edgzqkxs7tjcm48',  # Use the Client ID from the config
        'Authorization': f'Bearer {config["token"]}',  # Use the OAuth token from the config
        'Content-Type': 'application/json'
    }
    
    data = {
        "type": "channel.channel_points_custom_reward_redemption.add",
        "version": "1",
        "condition": {
            "broadcaster_user_id": get_broadcaster_id(config["channelName"], config["token"])
        },
        "transport": {
            "method": "webhook",
            "callback": "http://localhost:5777/eventsub",
            "secret": base64.b64decode(secrets.getSecret).decode('utf-8')

        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 202:
        print("Successfully subscribed to EventSub.")
    else:
        print(f"Failed to subscribe: {response.status_code} - {response.text}")

if __name__ == "__main__":
    run_eventsub_app()