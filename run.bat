@echo off
echo Installing dependencies...
py -m pip install -r requirements.txt
echo.
echo Starting AI Image Generator Server...
echo Please open your browser to: http://127.0.0.1:5000
py app.py
pause
