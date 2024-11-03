import requests
import json5
import sys

if sys.platform == "win32":
    import win32gui

def get_broadcaster_id(username, token):
    url = f"https://api.twitch.tv/helix/users?login={username}"
    
    headers = {
        'Client-ID': 'gp762nuuoqcoxypju8c569th9wz7q5',
        'Authorization': f'Bearer {token}',
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            return data['data'][0]['id']
        else:
            print("User not found.")
            return None
    else:
        print(f"Failed to get user ID: {response.status_code} - {response.text}")
        return None
    
def strip_text_after_cmd(command):
    parts = command.split(" ", 1)
    if len(parts) > 1:
        return parts[1]
    else:
        return ""

def update_config_if_empty(file_path, key, new_value):
    # Read the existing configuration
    with open(file_path, 'r', encoding='utf-8') as config_file:
        config = json5.load(config_file)
    
    # Ensure new_value is a string
    new_value = str(new_value)
    
    # Check if the key exists and is empty
    if key in config and not config[key]:
        config[key] = new_value  # Update the key with the new value
    
    # Write the updated configuration back to the file
    with open(file_path, 'w', encoding='utf-8') as config_file:
        config_file.write(json5.dumps(config, ensure_ascii=False, indent=2))

def update_config_if_data(file_path, key, new_value):
    # Read the existing configuration
    with open(file_path, 'r', encoding='utf-8') as config_file:
        config = json5.load(config_file)
    
    # Ensure new_value is a string
    new_value = str(new_value)
    
    config[key] = new_value  # Update the key with the new value
    
    # Write the updated configuration back to the file
    with open(file_path, 'w', encoding='utf-8') as config_file:
        config_file.write(json5.dumps(config, ensure_ascii=False, indent=4))


def create_channel_point_reward(username, title, cost, token, maxPerStream, maxPerUserPerStream, coolDown, maxPerStreamBool, log_message, isUserInputRequired = False, prompt = None):
    url = f"https://api.twitch.tv/helix/channel_points/custom_rewards"
    
    headers = {
        'Client-ID': 'gp762nuuoqcoxypju8c569th9wz7q5',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "broadcaster_id": get_broadcaster_id(username, token),
        "title": title,
        "cost": int(cost),
        "is_enabled": True,
        "is_user_input_required": False,
        "max_per_stream": int(maxPerStream),
        "is_max_per_stream_enabled": True if maxPerStreamBool == "True" else False,
        "max_per_user_per_stream": int(maxPerUserPerStream),
        "global_cooldown_seconds": int(coolDown),
        "is_user_input_required": True if isUserInputRequired == "True" else False,
        "prompt": prompt
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        log_message("Channel point reward created successfully!")
    else:
        log_message(f"Failed to create reward: {response.status_code} - {response.text}")

def window_enumeration_handler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

def find_window_by_substring(substring):
    top_windows = []
    win32gui.EnumWindows(window_enumeration_handler, top_windows)
    for hwnd, window_text in top_windows:
        if substring in window_text:
            return hwnd, window_text

    return None, None
def check_emulator_window():
    if sys.platform == "win32":
        hwnd, window_text = find_window_by_substring("Dolphin MPN")
        if hwnd:
            return "Dolphin"
        hwnd, window_text = find_window_by_substring("Dolphin")
        if hwnd:
            return "Dolphin"
        return None
