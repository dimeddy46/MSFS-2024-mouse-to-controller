@echo off

"python.exe" --version 2 > nul

if errorlevel 1 goto NOPYTHON
if not exist "%~dp0mouse_yoke.py" goto NOSCRIPT

"python.exe" -m pip install --upgrade pip --quiet
"python.exe" -m pip install --upgrade tk --quiet
"python.exe" -m pip install -r ./requirements.txt --quiet

"python.exe" ./mouse_yoke.py
pause
exit /b 0

:NOPYTHON
echo Error^: Python is not installed or is not reachable. If you believe you have Python installed, check your PATH settings.
pause

:NOSCRIPT
echo Error^: mouse_yoke.py is not reachable. Is it in the same path as run.bat?
pause