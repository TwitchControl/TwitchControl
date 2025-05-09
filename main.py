import dolphin_memory_engine
import os
import random
import threading
import time
import math
import platform
import asyncio
import importlib
import sys
import webbrowser

import customtkinter
import json5
import twitchio
import subprocess

from twitchio.ext import commands, pubsub
from PIL import ImageTk

from web_portal import run_flask_app, set_log_message

from plugins.marioParty4 import marioParty4

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
                "token": "",
                "channelName": "",
                "selectedPlugin": "None"
            }
            with open(config_path, 'w') as config_file:
                json5.dump(dummy_data, config_file, indent=4)
        
        with open(config_path, 'r') as config_file:
            self.config = json5.load(config_file)

        
        self.token = "oauth:" + self.config.get("token", "")
        self.initial_channel = self.config.get("channelName", "")
        self.selected_plugin = self.config.get("selectedPlugin", "None")

        self.window = customtkinter.CTk()
        self.window.title(f"Twitch Control ({getVersion()})")
        self.window.geometry("1080x720")

        self.client = twitchio.Client(token=self.token)
        self.client.pubsub = pubsub.PubSubPool(self.client)

        plugins = ["marioParty4"]

        if self.initial_channel == "":
            twitchChannel = "Twitch disconnected"
        else:
            twitchChannel = self.initial_channel
        
        frame = customtkinter.CTkFrame(self.window)
        frame.pack(anchor="nw", padx=10, pady=5, fill="x")

        channel_label_bold = customtkinter.CTkLabel(
            frame,
            text="Channel: ",
            font=("Arial", 28, "bold")
        )
        channel_label_bold.pack(side="left", padx=5)
        
        global channel_name_label
        channel_name_label = customtkinter.CTkLabel(
            frame,
            text=twitchChannel,
            font=("Arial", 20)
        )
        channel_name_label.pack(side="left")
        
        status_frame = customtkinter.CTkFrame(self.window)
        status_frame.pack(anchor="nw", padx=10, pady=2)
        
        self.status_label = customtkinter.CTkLabel(
            status_frame,
            text="Status: ",
            font=("Arial", 28, "bold")
        )
        self.status_label.pack(side="left", padx=5)

        self.status_name_label = customtkinter.CTkLabel(
            status_frame,
            text="Disconnected",
            font=("Arial", 20)
        )
        self.status_name_label.pack(side="left", padx=5)

        self.log_console = customtkinter.CTkTextbox(self.window, width=100, height=20)
        log_console = self.log_console
        log_console.pack(padx=10, pady=10, fill="both", expand=True)
        log_console.configure(font=("Courier", 18))

        self.command_entry = customtkinter.CTkEntry(self.window, width=80)
        self.command_entry.pack(side="left", padx=10, pady=5, fill="x", expand=True)

        self.submit_button = customtkinter.CTkButton(self.window, text="Submit", command=self.submit_command)
        self.submit_button.pack(side="right", padx=10, pady=5)

        log_message(f"Twitch Control Shell:")
        log_message(f"Run /help for a list of commands")

        self.connected_to_dolphin = False
        self.check_connection()
        
        with open('config.json5', 'r') as config_file:
            self.config = json5.load(config_file)

        try:
            os.mkdir("plugins")
        except FileExistsError:
            pass
        
        plugins_dir = os.path.join(os.path.dirname(sys.executable), 'plugins')
        
        sys.path.append(plugins_dir)
        
        # Load plugins
        game_names = [format_game_name(f) for f in plugins]
        self.on_game_selected(self.config.get("selectedPlugin", "None"))

        # Check if there are any plugins loaded
        if game_names:
            self.game_selection = customtkinter.CTkOptionMenu(
                frame,
                values=["None"] + game_names,
                command=self.on_game_selected
            )
            self.game_selection.pack(side="right", padx=5)
            self.game_selection.set(self.selected_plugin)
        else:
            log_message("No modules loaded.")

        self.command_entry.bind("<Return>", self.submit_command)

    def on_game_selected(self, selected_game):
        log_message(f"Selected plugin: {format_game_name(selected_game)}")
        
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
                log_message(f"Loaded config for plugin {selected_game}.")

        except FileNotFoundError:
            log_message(f"Configuration file for plugin {selected_game} not found.")
        except json5.JSONDecodeError as e:
            log_message(f"Error decoding JSON for plugin {selected_game}: {str(e)}")

    def submit_command(self, event=None):
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
        elif "/web" in command:
            self.handle_web()
        elif command == "/config":
            self.open_config_window()
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
        log_message("/web - Opens a web interface for manual redemption.")


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

        elif self.config.get("token", "") == "" or self.config.get("channelName", "") == "":
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

        if "isUserInputRequired" in reward:
            args.append(reward["isUserInputRequired"])
        if "prompt" in reward:
            args.append(reward["prompt"])

        create_reward_thread = threading.Thread(target=create_channel_point_reward, args=tuple(args))
        create_reward_thread.start()

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
            emulator_status = check_emulator_window()
            if emulator_status == "Dolphin":
                try:
                    dolphin_memory_engine.hook()
                    self.status_name_label.configure(text="Connected")
                    log_message(f"Successfully Connected to Dolphin")
                    self.connected_to_dolphin = True
                except Exception as e:
                    self.status_name_label.configure(text="Disconnected")
                    log_message(f"Failed to hook to Dolphin: {str(e)}")
                    self.connected_to_dolphin = False
            else:
                self.status_name_label.configure(text="Disconnected")
                log_message("Dolphin emulator is not running.")
                self.connected_to_dolphin = False
        except Exception as e:
            self.status_name_label.configure(text="Disconnected")
            log_message(f"Error checking connection: {str(e)}")
            self.connected_to_dolphin = False
    
    def disconnect_from_dolphin(self):
        if self.connected_to_dolphin:
            self.status_name_label.configure(text="Disconnected")
            log_message("Disconnected from Dolphin.")
            dolphin_memory_engine.un_hook()
        else:
            log_message("Dolphin already disconnected.")

    def run_gui(self):
        self.window.mainloop()

    def handle_web(self):
        try:
            set_log_message(log_message)
            # Start the Flask server in a new thread
            flask_thread = threading.Thread(target=run_flask_app, daemon=True)
            flask_thread.start()
            log_message("Web portal started at http://localhost:5776")

            # Open web browser
            webbrowser.open("http://localhost:5776")
        except Exception as e:
            log_message(f"Failed to start web portal: {str(e)}")

class TwitchBot(commands.Bot):
    def __init__(self, token, initial_channels):
        super().__init__(token="oauth:" + token, initial_channels=initial_channels, prefix="!")
        client = twitchio.Client(token=token)
        client.pubsub = pubsub.PubSubPool(client)

        with open('config.json5', 'r') as config_file:
            self.config = json5.load(config_file)

        self.register_events(client)
        dolphin_memory_engine.hook()

        @client.event()
        async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
            log_message(f'Received channel points event: {event.reward.title}')
            if self.config.get("selectedPlugin", "None") == "Mario Party 4":
                load_game_thread = threading.Thread(target=marioParty4.loadGame, args=(event, log_message))
                load_game_thread.start()

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