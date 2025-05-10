# web_portal.py
from flask import Flask, render_template, request, jsonify
import json5
import threading
import importlib
from plugins.marioParty4 import marioParty4
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not running in PyInstaller, use the executable's directory
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

app = Flask(__name__, 
            template_folder=resource_path('templates'),
            static_folder=resource_path('static'))

# Load rewards from the game configuration
import json5
import os

log_message_func = None

def set_log_message(func):
    global log_message_func
    log_message_func = func
    
def load_rewards():
    try:
        config_path = 'config.json5'
        with open(config_path, 'r') as config_file:
            config = json5.load(config_file)
        selected_plugin = config.get("selectedPlugin", "None")

        # Convert the selected plugin name to lower camel case
        words = selected_plugin.split()
        lower_camel_case_plugin_name = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
        plugin_config_path = f'plugins/{lower_camel_case_plugin_name}/{lower_camel_case_plugin_name}.json5'
        
        if not os.path.exists(plugin_config_path):
            print(f"Plugin config file not found: {plugin_config_path}")
            return []

        with open(plugin_config_path, 'r') as game_config_file:
            game_config = json5.load(game_config_file)
            rewards = game_config.get("rewards", [])
            print(f"Loaded rewards: {rewards}")
            return rewards
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return []
    except json5.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

@app.route('/')
def index():
    rewards = load_rewards()
    return render_template('index.html', rewards=rewards)

@app.route('/redeem', methods=['POST'])
def redeem():
    data = request.get_json()
    reward_name = data.get('reward_name')
    input_value = data.get('input_value')

    if not reward_name:
        return jsonify({"status": "error", "message": "Reward name is missing."}), 400

    # Process the reward redemption using the new handler
    event = type('Event', (object,), {'reward': type('Reward', (object,), {'title': reward_name}), 'input': input_value})

    def process_reward():
        config_path = 'config.json5'
        with open(config_path, 'r') as config_file:
            config = json5.load(config_file)
            selected_plugin = config.get("selectedPlugin", "None")
            words = selected_plugin.split()
            lower_camel_case_plugin_name = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
        plugin_module = importlib.import_module(f'plugins.{lower_camel_case_plugin_name}.{lower_camel_case_plugin_name}')
        plugin_module.loadGame(event, log_message_func)

    reward_thread = threading.Thread(target=process_reward)

    reward_thread.start()

    return jsonify({"status": "success", "message": f"Redeemed {reward_name}"})

def run_flask_app():
    app.run(port=5776, use_reloader=False, debug=False)
