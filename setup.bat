@echo off
echo Installing dependencies...
pip install -r requirements-windows.txt

echo.
echo Downloading ChromeDriver...
powershell -Command "Invoke-WebRequest -Uri 'https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_win32.zip' -OutFile 'chromedriver.zip'"
powershell -Command "Expand-Archive -Path 'chromedriver.zip' -DestinationPath '.' -Force"
del chromedriver.zip

echo.
echo Setup complete!
echo Run: python whatsapp_bot.py
pause
