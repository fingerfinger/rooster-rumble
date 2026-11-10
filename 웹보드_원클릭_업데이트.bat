@echo off
title ROOSTER RUMBLE Webboard Auto Deploy
cd /d "%~dp0"
python sync_webboard.py --push
echo.
pause
