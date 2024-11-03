@echo off
rmdir dist /s /q

REM Get the short git hash
FOR /F "tokens=*" %%i IN ('git rev-parse --short HEAD') DO SET GIT_HASH=%%i

REM Update version.py with the git hash
echo def getVersion(): > version.py
echo     return "%%GIT_HASH%%" >> version.py

pyinstaller --onefile .\main.py --name="Twitch Control" -w
mkdir dist\plugins
