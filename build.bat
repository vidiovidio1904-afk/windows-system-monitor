@echo off

pip install -r requirements.txt

pyinstaller ^
--onefile ^
--windowed ^
--name WindowsSystemMonitor ^
monitor.py

pause
