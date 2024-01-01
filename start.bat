@echo off
setlocal EnableDelayedExpansion

:loop
python main.py
echo "Press Ctrl-C to stop!"

goto loop

:: set /p answer=Do you want to run the script again? (y/n)

:: if /i "%answer%"=="y" goto :loop

:: echo Goodbye!
:: pause
