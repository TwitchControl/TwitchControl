import dolphin_memory_engine
import os
import random
import threading
import time
import math
import platform
import asyncio
import importlib

import customtkinter
import json5
import twitchio
from twitchio.ext import commands, pubsub
from PIL import ImageTk

from functions import (
    check_emulator_window,
    create_channel_point_reward,
    get_broadcaster_id,
    strip_text_after_cmd,
    update_config_if_data,
    update_config_if_empty,
    format_game_name
)
from version import getVersion

log_console = None

def log_message(message, single=False):
    global log_console
    if log_console is not None:
        log_console.configure(state="normal")
        log_console.insert("end", message + "\n")
        log_console.configure(state="disabled")
        
        # Scroll to the end
        log_console.see("end")
        if not single:
            log_console.insert("end", "")

class App():
    def __init__(self):
        global log_console
        # Load configuration
        config_path = 'config.json5'
        if not os.path.exists(config_path):
            dummy_data = {
                "token": "dummy_token",
                "channelName": "dummy_channel",
                "selectedPlugin": "None"
            }
            with open(config_path, 'w') as config_file:
                json5.dump(dummy_data, config_file, indent=4)
        
        with open(config_path, 'r') as config_file:
            self.config = json5.load(config_file)

        
        # Initialize token and initial_channel from the configuration
        self.token = "oauth:" + self.config.get("token", "")
        self.initial_channel = self.config.get("channelName", "")
        self.selected_plugin = self.config.get("selectedPlugin", "None")

        # Create GUI window
        self.window = customtkinter.CTk()
        self.window.title(f"Twitch Control ({getVersion()})")
        self.window.geometry("1080x720")

        self.client = twitchio.Client(token=self.token)
        self.client.pubsub = pubsub.PubSubPool(self.client)

        if self.initial_channel == "":
            twitchChannel = "Twitch disconnected"
        else:
            twitchChannel = self.initial_channel
        
        frame = customtkinter.CTkFrame(self.window)
        frame.pack(anchor="nw", padx=10, pady=5, fill="x")

        # Create bold label for "Channel:"
        channel_label_bold = customtkinter.CTkLabel(
            frame,
            text="Channel: ",
            font=("Arial", 28, "bold")
        )
        channel_label_bold.pack(side="left", padx=5)
        
        global channel_name_label
        # Create regular label for the channel name
        channel_name_label = customtkinter.CTkLabel(
            frame,
            text=twitchChannel,
            font=("Arial", 20)
        )
        channel_name_label.pack(side="left")
        
        # Create a new frame for the status label
        status_frame = customtkinter.CTkFrame(self.window)
        status_frame.pack(anchor="nw", padx=10, pady=2)  # Reduced pady for more compactness
        
        # Create status label with bold "Status:"
        self.status_label = customtkinter.CTkLabel(
            status_frame,
            text="Status: ",
            font=("Arial", 28, "bold")
        )
        self.status_label.pack(side="left", padx=5)  # Change to side="left" to align next to the status name

        # Create regular label for the channel name
        self.status_name_label = customtkinter.CTkLabel(
            status_frame,
            text="Disconnected",
            font=("Arial", 20)
        )
        self.status_name_label.pack(side="left", padx=5)  # Add some padding for spacing

        # Create a text box for logging
        self.log_console = customtkinter.CTkTextbox(self.window, width=100, height=20)
        log_console = self.log_console  # Assign to global variable
        log_console.pack(padx=10, pady=10, fill="both", expand=True)
        log_console.configure(font=("Courier", 18))

        # Create an entry for user input
        self.command_entry = customtkinter.CTkEntry(self.window, width=80)
        self.command_entry.pack(side="left", padx=10, pady=5, fill="x", expand=True)

        # Create a button to submit the command
        self.submit_button = customtkinter.CTkButton(self.window, text="Submit", command=self.submit_command)
        self.submit_button.pack(side="right", padx=10, pady=5)

        log_message(f"Twitch Control Shell:")
        log_message(f"Run /help for a list of commands")

        self.connected_to_dolphin = False
        self.check_connection()
                # Load configuration
        with open('config.json5', 'r') as config_file:
            self.config = json5.load(config_file)

        # Initalize plugins
        games_dir = 'plugins'
        try:
            os.mkdir(games_dir)
        except FileExistsError:
            pass
        plugins = []
        for root, dirs, files in os.walk(games_dir):
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    # Extract the game name from the file path
                    game_name = os.path.splitext(file)[0]
                    plugins.append(game_name)

        game_names = [format_game_name(f) for f in plugins]
    
        for game in plugins:
            try:
                print()
                # Attempt to import the module from the 'plugins' package
                module = importlib.import_module('plugins.marioParty4.marioParty4')
                log_message(f'Loaded Plugin: {format_game_name(game)}')
                self.on_game_selected(game)
            except ModuleNotFoundError:
                log_message(f'Plugin not loaded: {format_game_name(game)}')

        # Check if there are any plugins loaded
        if game_names:
            self.game_selection = customtkinter.CTkOptionMenu(
                frame,
                values=["None"] + game_names,
                command=self.on_game_selected
            )
            self.game_selection.pack(side="right", padx=5)  # Add some padding for spacing
            self.game_selection.set(self.selected_plugin)  # Set the initial selection to the saved plugin
        else:
            log_message("No modules loaded.")  # Log message if no plugins are loaded
       

    def on_game_selected(self, selected_game):
        log_message(f"Selected plugin: {selected_game}")
        
        # Save the selected plugin to the configuration
        self.config["selectedPlugin"] = selected_game
        with open('config.json5', 'w') as config_file:
            json5.dump(self.config, config_file, indent=4)

        try:
            words = selected_game.split()
            lower_camel_case_game = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
            camel_case_game = ''.join(word.capitalize() for word in words)
            with open(f'plugins/{lower_camel_case_game}/{camel_case_game}.json5', 'r') as game_config_file:
                self.game_config = json5.load(game_config_file)
            log_message(f"Loaded plugin for {selected_game}")
        except FileNotFoundError:
            log_message(f"Configuration file for plugin {selected_game} not found.")
        except json5.JSONDecodeError as e:
            log_message(f"Error decoding JSON for plugin {selected_game}: {str(e)}")

    def submit_command(self):
        command = self.command_entry.get()
        log_message(f"> {command}")
        self.command_entry.delete(0, "end")

        if command == "/connect":
            self.handle_connect()
        elif command == "/help":
            self.handle_help()
        elif command == "/disconnect":
            self.handle_disconnect()
        elif "/link" in command:
            self.handle_link(command)
        elif "/create" in command:
            self.handle_create()
        elif "/unlink" in command:
            self.handle_unlink()
        elif "/version" in command:
            self.handle_version()
        else:
            log_message(f"Unknown command. Type /help for a list of commands.")

    def handle_connect(self):
        if self.status_name_label.cget("text") != "Connected":
            self.check_connection()
        else:
            log_message("Already connected to dolphin.")

    def handle_help(self):
        log_message("/connect - Connects to Dolphin.")
        log_message("/create - Creates the rewards on Twitch.")
        log_message("/disconnect - Disconnect from Dolphin")
        log_message("/link - Link to a Twitch account")
        log_message("/unlink - Unlink from Twitch.")
        log_message("/version - Gives the version of the app.")

    def handle_disconnect(self):
        self.disconnect_from_dolphin()

    def handle_link(self, command):
        args = strip_text_after_cmd(command).split()
        arg = args[0] if len(args) > 0 else ""
        arg2 = args[1] if len(args) > 1 else ""
        if arg == "":
            log_message("No channel defined. Type /link <channel> <token>")
        elif arg2 == "":
            log_message(f"No token defined. Type /link {arg} <token>")
        else:
            self.twitch_connect(arg, arg2)

    def handle_create(self):
        if self.config["token"] != "" and self.config["channelName"] != "":
            if hasattr(self, 'game_config') and "rewards" in self.game_config:
                rewards = self.game_config["rewards"]
                for reward in rewards:
                    if reward["enabled"] == "True":
                        self.create_reward(reward)
                    else:
                        self.create_reward(reward)
            else:
                log_message("No rewards found in the selected game's configuration.")
        elif self.config["token"] == "" or self.config["channelName"] == "":
            log_message("Failed to create channel point rewards. Is your channel linked?")

    def create_reward(self, reward):
        args = [
            self.config["channelName"],
            reward["name"],
            reward["cost"],
            self.config["token"],
            reward["maxPerStream"],
            reward["maxPerUserPerStream"],
            reward["cooldown"],
            reward.get("maxPerStreamEnabled", False),
            log_message
        ]

        # Optionally add isUserInputRequired and prompt if they exist
        if "isUserInputRequired" in reward:
            args.append(reward["isUserInputRequired"])
        if "prompt" in reward:
            args.append(reward["prompt"])

        # Start the thread with the prepared arguments
        create_reward_thread = threading.Thread(target=create_channel_point_reward, args=tuple(args))
        create_reward_thread.start()
        log_message(f"Created channel point reward {reward['name']}")

    def handle_unlink(self):
        if self.config["channelName"] != "":
            update_config_if_data('config.json5', 'channelName', "")
            update_config_if_data('config.json5', 'token', "")
            log_message("Unlinked from Twitch")
            channel_name_label.configure(text="Twitch disconnected")
        else:
            log_message("No channel is linked.")

    def handle_version(self):
        log_message(f"Twitch Control: v{getVersion()}")

    def twitch_connect(self, arg, arg2):
        if self.config["channelName"] == "" and self.config["token"] == "":
            update_config_if_empty('config.json5', 'channelName', arg)
            update_config_if_empty('config.json5', 'token', arg2)
            log_message(f"Linked to {arg}")
            channel_name_label.configure(text=arg)
        elif self.config["token"] == "" and self.config["channelName"] != "":
            update_config_if_empty('config.json5', 'token', arg)
        elif self.config["token"] == "" and self.config["token"] != "":
            update_config_if_empty('config.json5', 'channelName', arg)
        else:
            log_message(f"Already linked to {arg}")
    
    def check_connection(self):
        try:
            emulator_status = check_emulator_window()  # Check the emulator window status
            if emulator_status == "Dolphin":
                try:
                    dolphin_memory_engine.hook()
                    self.indicator.configure(text_color="green")
                    self.status_name_label.configure(text="Connected")
                    log_message(f"Successfully Connected to Dolphin")
                    self.connected_to_dolphin = True  # Update the flag once connected
                except Exception as e:  # Catch any exceptions during hooking
                    self.status_name_label.configure(text="Disconnected")
                    log_message(f"Failed to hook to Dolphin: {str(e)}")  # Log the error message
                    self.connected_to_dolphin = False  # Update the flag to indicate not connected
            else:
                self.status_name_label.configure(text="Disconnected")
                log_message("Dolphin emulator is not running.")  # Log if Dolphin is not open
                self.connected_to_dolphin = False  # Update the flag to indicate not connected
        except Exception as e:  # Catch any exceptions during the connection check
            self.status_name_label.configure(text="Disconnected")
            log_message(f"Error checking connection: {str(e)}")  # Log the error message
            self.connected_to_dolphin = False  # Update the flag to indicate not connected
    
    def disconnect_from_dolphin(self):
        if self.connected_to_dolphin:
            self.indicator.configure(text_color="red")
            self.status_name_label.configure(text="Disconnected")
            log_message("Disconnected from Dolphin.")
            dolphin_memory_engine.un_hook()
        else:
            log_message("Dolphin already disconnected.")


    def run_gui(self):
        self.window.mainloop()

class TwitchBot(commands.Bot):
    def __init__(self, token, initial_channels):
        super().__init__(token="oauth:" + token, initial_channels=initial_channels, prefix="!")
        client = twitchio.Client(token=token)
        client.pubsub = pubsub.PubSubPool(client)

        # Load configuration
        with open('config.json5', 'r') as config_file:
            self.config = json5.load(config_file)

        # Register events
        self.register_events(client)
        dolphin_memory_engine.hook()

        @client.event()
        async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
            log_message(f'Received channel points event: {event.reward.title}')  # Log the received event
            if self.game_selection == "Mario Party 4":
                marioParty4.loadGame(self.config, event, log_message)

    async def subscribe_to_topics(self, client):
        topics = [
            pubsub.channel_points(self.config["token"])[int(get_broadcaster_id(self.config["channelName"], self.config["token"]))],
        ]
        await client.pubsub.subscribe_topics(topics)    


    def register_events(self, client):
        @self.event()
        async def event_ready():
            log_message(f'Logged in as: {self.nick}')
            await self.subscribe_to_topics(client)

    async def run_bot(self):
        await self.start()

if __name__ == "__main__":
    app = App()

    twitchBot = TwitchBot(token=app.config["token"], initial_channels=[app.config["channelName"]])
    twitch_bot_thread = threading.Thread(target=twitchBot.run, daemon=True)
    twitch_bot_thread.start()
    
    gui_thread = threading.Thread(target=app.run_gui(), daemon=True)
    gui_thread.start()

