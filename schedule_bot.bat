@echo off
REM Schedule bot to run daily at 9 AM
schtasks /create /tn "WhatsAppBot" /tr "%CD%\run_bot.bat" /sc daily /st 09:00 /f

echo Task scheduled successfully!
echo To view: schtasks /query /tn "WhatsAppBot"
echo To delete: schtasks /delete /tn "WhatsAppBot" /f
pause
