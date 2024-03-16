@echo off
setlocal EnableDelayedExpansion

:loop
python main.py
if errorlevel 1 (
    echo "Error detected, restarting in 5 seconds..."
    choice /C:abcdefghijklmnopqrstuvwxyz
    if errorlevel 1 goto loop
    if errorlevel 0 exit

)

cls
goto loop

@ECHO off
