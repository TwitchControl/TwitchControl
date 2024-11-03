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
    update_config_if_empty
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
                "channelName": "dummy_channel"
            }
            with open(config_path, 'w') as config_file:
                json5.dump(dummy_data, config_file, indent=4)
        
        with open(config_path, 'r') as config_file:
            self.config = json5.load(config_file)

        
        # Initialize token and initial_channel from the configuration
        self.token = "oauth:" + self.config.get("token", "")
        self.initial_channel = self.config.get("channelName", "")

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
        log_console.configure(font=("Courier", 20))

        # Create an entry for user input
        self.command_entry = customtkinter.CTkEntry(self.window, width=80)
        self.command_entry.pack(side="left", padx=10, pady=5, fill="x", expand=True)

        # Create a button to submit the command
        self.submit_button = customtkinter.CTkButton(self.window, text="Submit", command=self.submit_command)
        self.submit_button.pack(side="right", padx=10, pady=5)

        log_message(f"Mario Party 4 - Twitch Control Shell:")
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

        game_names = [self.format_game_name(f) for f in plugins]
        print(game_names)
        for game in plugins:
            try:
                # Attempt to import the module from the 'plugins' package
                module = importlib.import_module(f'plugins.{game}.{game}')
                log_message(f'Loaded Game: {game}')
            except ModuleNotFoundError:
                pass

        # Check if there are any plugins loaded
        if game_names:
            self.game_selection = customtkinter.CTkOptionMenu(
                frame,
                values=game_names,
                command=self.on_game_selected
            )
            self.game_selection.pack(side="right", padx=5)  # Add some padding for spacing
        else:
            log_message("No modules loaded.")  # Log message if no plugins are loaded


    def format_game_name(self, module_name):
        # Convert camel case to title case with spaces, handling numbers separately
        formatted_name = ''.join([' ' + char if char.isupper() else char for char in module_name]).title().strip()
        # Ensure numbers are separated from the preceding word
        formatted_name = ''.join([' ' + char if char.isdigit() and not formatted_name[i-1].isspace() else char for i, char in enumerate(formatted_name)])
        return formatted_name

    def on_game_selected(self, selected_game):
        log_message(f"Selected game: {selected_game}")
        # Load game-specific configuration
        try:
            with open(f'plugins/{selected_game}/{selected_game}.json5', 'r') as game_config_file:
                self.game_config = json5.load(game_config_file)
            log_message(f"Loaded configuration for {selected_game}")
        except FileNotFoundError:
            log_message(f"Configuration file for {selected_game} not found.")
        except json5.JSONDecodeError as e:
            log_message(f"Error decoding JSON for {selected_game}: {str(e)}")


    def submit_command(self):
        command = self.command_entry.get()
        log_message(f"> {command}")
        self.command_entry.delete(0, "end")
        if command == "/connect":
            if self.status_name_label.cget("text") != "Connected":
                self.check_connection()
            else:
                log_message("Already connected to dolphin.")
        elif command == "/help":
            log_message("/connect - Connects to Dolphin.")
            log_message("/create - Creates the rewards on Twitch.")
            log_message("/disconnect - Disconnect from Dolphin")
            log_message("/link - Link to a Twitch account")
            log_message("/unlink - Unlink from Twitch.")
            log_message("/version - Gives the version of the app.")
        elif command == "/disconnect":
            self.disconnect_from_dolphin()
        elif "/link" in command:
            args = strip_text_after_cmd(command).split()
            arg = args[0] if len(args) > 0 else ""
            arg2 = args[1] if len(args) > 1 else ""
            if arg == "":
                log_message("No channel defined. Type /link <channel> <token>")
            elif arg2 == "":
                log_message(f"No token defined. Type /link {arg} <token>")
            else:
                self.twitch_connect(arg, arg2)
        elif "/create" in command:
            if self.config["token"] != "" and self.config["channelName"] != "":
                for reward in self.config["rewards"]:
                    if reward["enabled"] == "True":
                        if reward.get("isUserInputRequired", False) is False:
                            create_reward_thread = threading.Thread(target=create_channel_point_reward, args=(
                                self.config["channelName"],
                                reward["name"],
                                reward["cost"],
                                self.config["token"],
                                reward["maxPerStream"],
                                reward["maxPerUserPerStream"],
                                reward["cooldown"],
                                reward["maxPerStreamEnabled"],
                                log_message
                            ))
                            create_reward_thread.start()
                        else:
                            create_reward_thread = threading.Thread(target=create_channel_point_reward, args=(
                                self.config["channelName"],
                                reward["name"],
                                reward["cost"],
                                self.config["token"],
                                reward["maxPerStream"],
                                reward["maxPerUserPerStream"],
                                reward["cooldown"],
                                reward["maxPerStreamEnabled"],
                                log_message
                            ))
                            create_reward_thread.start()
                            log_message(f"Created channel point reward {reward["name"]}")
            elif self.config["token"] == "" or self.config["channelName"] == "":
                log_message("Failed to create channel point rewards is your channel linked.")
        elif "/unlink" in command:
            arg = strip_text_after_cmd(command)
            if self.config["channelName"] != "":
                update_config_if_data('config.json5', 'channelName', "")
                update_config_if_data('config.json5', 'token', "")
                log_message("Unlinked from Twitch")
                channel_name_label.configure(text="Twitch disconnected")
            else:
                log_message("No channel is linked.")
        elif "/version" in command:
            log_message(f"MP Twitch Control: v{getVersion()}")
        else:
            log_message(f"Unknown command. Type /help for a list of commands.")

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

