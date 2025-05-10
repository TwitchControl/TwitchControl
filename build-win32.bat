@echo off
pyinstaller --onefile .\main.py --name="Twitch Control" -w --add-data "templates;templates" --add-data "plugins;plugins"