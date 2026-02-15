@echo off
echo Starting WhatsApp Bot...
cd C:\whatsapp-bot
python bot_scheduled.py >> bot_log.txt 2>&1
echo Bot execution completed.
