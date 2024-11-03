import requests
import json5
import sys
import dolphin_memory_engine

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

def format_game_name(module_name):
    # Convert camel case to title case with spaces, handling numbers separately
    formatted_name = ''.join([' ' + char if char.isupper() else char for char in module_name]).title().strip()
    # Ensure numbers are separated from the preceding word
    formatted_name = ''.join([' ' + char if char.isdigit() and not formatted_name[i-1].isspace() else char for i, char in enumerate(formatted_name)])
    return formatted_name

def format_game_name_camel(module_name):
    # Convert camel case to title case with spaces, handling numbers separately
    formatted_name = ''.join([' ' + char if char.isupper() else char for char in module_name]).title().strip()
    # Ensure numbers are separated from the preceding word
    formatted_name = ''.join([' ' + char if char.isdigit() and not formatted_name[i-1].isspace() else char for i, char in enumerate(formatted_name)])
    # Capitalize the first character if it's not already
    if formatted_name and not formatted_name[0].isupper():
        formatted_name = formatted_name[0].upper() + formatted_name[1:]
    return formatted_name

def write_bytes(address, value, size=1):
    dolphin_memory_engine.write_bytes(address, value.to_bytes(size, byteorder='big'))

def read_bytes(address, size=1):
    return int.from_bytes(dolphin_memory_engine.read_bytes(address, size), byteorder='big')

def update_value(address, increment, min_value=0, max_value=999):
    current_value = read_bytes(address, 2)
    new_value = max(min(current_value + increment, max_value), min_value)
    write_bytes(address, new_value, 2)
    return new_value