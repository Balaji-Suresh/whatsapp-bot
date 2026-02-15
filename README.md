# WhatsApp Bot - Windows/EC2 Deployment

Automated WhatsApp messaging bot for on-premises Windows servers or EC2 instances.

## Prerequisites

1. **Python 3.9+** installed
2. **Google Chrome** browser installed
3. **WhatsApp Web** access

## Quick Setup

### 1. Run Setup
```cmd
setup.bat
```

### 2. Run Bot
```cmd
run_bot.bat
```

### 3. First Run
- Scan QR code with WhatsApp mobile app
- Press Enter to start sending messages
- Chrome profile is saved (no QR needed next time)

### 4. Schedule Daily Runs (Optional)
Run as Administrator:
```cmd
schedule_bot.bat
```

## Excel File Format

Create `contacts.xlsx` with:

| Name | Phone | Message |
|------|-------|---------|
| John | +1234567890 | Hi {name}! |
| Jane | +0987654321 | Hello {name}! |

## Troubleshooting

**ChromeDriver version mismatch:**
- Check Chrome version: chrome://version
- Download matching ChromeDriver from https://chromedriver.chromium.org/downloads
- Replace chromedriver.exe

**WhatsApp session expired:**
- Delete `chrome-profile` folder
- Run bot again and scan QR code

**Scheduled task not running:**
- Run Task Scheduler as Administrator
- Ensure server doesn't sleep

## Results

Results saved as `results_YYYYMMDD_HHMMSS.csv` after each run.

## Compliance

- Get explicit consent before sending messages
- Follow WhatsApp Terms of Service
- Comply with local regulations