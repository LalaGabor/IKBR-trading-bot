@echo off
setlocal

:loop
tasklist | find /i "python.exe" | find /i "bot.py" > nul

if errorlevel 1 (
    echo bot.py is not running. Restarting...
    start "" "C:\Users\Sebastian\PycharmProjects\Active\IKBR-trading-bot\Scripts\python.exe" "C:\Users\Sebastian\PycharmProjects\IKBR-trading-bot\bot.py"
)

timeout /t 300 >nul
goto loop
