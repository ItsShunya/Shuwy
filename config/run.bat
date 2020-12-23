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

echo %date:~-4%-%date:~3,2%-%date:~0,2% %time:~0,2%:%time:~3,2%:%time:~6,2%.%time:~9,3% Welcome to the Shuwy bot start-up program.
timeout /t 1 /nobreak > NUL
echo %date:~-4%-%date:~3,2%-%date:~0,2% %time:~0,2%:%time:~3,2%:%time:~6,2%.%time:~9,3% Press any key if you wish to start Shuwy Bot.
timeout 15 > NUL
echo %date:~-4%-%date:~3,2%-%date:~0,2% %time:~0,2%:%time:~3,2%:%time:~6,2%.%time:~9,3% Please, wait while the bot starts.
timeout /t 1 /nobreak > NUL
echo --------------------------------------------------------------------------------
timeout /t 1 /nobreak > NUL
echo %date:~-4%-%date:~3,2%-%date:~0,2% %time:~0,2%:%time:~3,2%:%time:~6,2%.%time:~9,3% Setting up the Lavalink server...
timeout /t 1 /nobreak > NUL
::start "TEST" cmd.exe /k TITLE TEST & color 02 & mode con: cols=160 lines=78
start cmd /k "title "Shuwy's Lavalink Server"  & color 05 & call lavalink.bat"

timeout /t 7 /nobreak > NUL
echo %date:~-4%-%date:~3,2%-%date:~0,2% %time:~0,2%:%time:~3,2%:%time:~6,2%.%time:~9,3% Lavalink server has been started, please check above if there were any errors.
timeout /t 1 /nobreak > NUL
echo %date:~-4%-%date:~3,2%-%date:~0,2% %time:~0,2%:%time:~3,2%:%time:~6,2%.%time:~9,3% Shuwy Bot will start now, if errors were encountered in the Lavalink server initialization then Music commands will not be available.
timeout /t 1 /nobreak > NUL
echo %date:~-4%-%date:~3,2%-%date:~0,2% %time:~0,2%:%time:~3,2%:%time:~6,2%.%time:~9,3% Setting up Shuwy Bot...
cd /D "%~dp0"
cd ..
pipenv run python "D:\Projects\Shuwy Discord Bot\Shuwy\Shuwy\Shuwy.py"
pause
echo %date:~-4%-%date:~3,2%-%date:~0,2% %time:~0,2%:%time:~3,2%:%time:~6,2%.%time:~9,3% Shuwy Bot has been started!
pause >nul
