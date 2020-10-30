@echo off
color 5
title Shuwy Discord Bot
cls

:: We will limit the use of this script to Windows 10 only.
:: Timeout command does not work well with Windows XP.
:: Sleep command does not work well in Windows 7


:: Check Windows version

setlocal
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
if "%version%" == "10.0" goto Main
endlocal

:Main

echo                   _____________________________________________
echo          ________^|   _____  _____  _____  _____  __ __  _____   ^|_______
echo          \       ^|  ^|   __^|^|  ^|  ^|^|  ^|  ^|^|   ^| ^|^|  ^|  ^|^|  _  ^|  ^|      /
echo           \      ^|  ^|__   ^|^|     ^|^|  ^|  ^|^| ^| ^| ^|^|_   _^|^|     ^|  ^|     /
echo            \     ^|  ^|_____^|^|__^|__^|^|_____^|^|_^|___^|  ^|_^|  ^|__^|__^|  ^|    /
echo            /     ^|______________________________________________^|    \
echo           /           /                                    \          \
echo          /___________/                                      \__________\
echo --------------------------------------------------------------------------------
echo. 
echo.
  
echo Welcome to the Shuwy bot start-up program.
timeout /t 2 /nobreak > NUL
echo Press any key if you wish to start Shuwy Bot.
timeout 15 > NUL
echo Please, wait while the bot starts.
timeout /t 2 /nobreak > NUL
echo --------------------------------------------------------------------------------
timeout /t 2 /nobreak > NUL
echo Setting up the Lavalink server...
timeout /t 2 /nobreak > NUL
::start "TEST" cmd.exe /k TITLE TEST & color 02 & mode con: cols=160 lines=78
start cmd /k "title "Shuwy's Lavalink Server"  & color 05 & call lavalink.bat"

timeout /t 7 /nobreak > NUL
echo Lavalink server has been started, please check above if there were any errors.
timeout /t 2 /nobreak > NUL
echo Shuwy Bot will start now, if errors were encountered in the Lavalink server initialization then Music commands will not be available.
timeout /t 2 /nobreak > NUL
echo Setting up Shuwy Bot...
cd /D "%~dp0"
cd ..
"D:\Projects\discord.py bot\ShunyaBOT\ShunyaBOT\ShunyaBOTenv2\Scripts\python.exe" "D:\Projects\discord.py bot\ShunyaBOT\ShunyaBOT\ShunyaBOT.py" %*
pause
echo Shuwy Bot has been started!
pause >nul
