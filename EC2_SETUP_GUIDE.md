# WhatsApp Bot - EC2 Deployment Guide

## Overview
Deploy your WhatsApp bot on an AWS EC2 Windows instance to run 24/7 with scheduled automation.

---

## Step 1: Launch EC2 Instance

### 1.1 Go to EC2 Console
- Open AWS Console: https://console.aws.amazon.com/ec2/
- Click **Launch Instance**

### 1.2 Configure Instance
**Name:** `whatsapp-bot-server`

**AMI:** Windows Server 2022 Base (Free Tier eligible)

**Instance Type:** `t3.micro` or `t2.micro` (Free Tier: 750 hours/month)

**Key Pair:** 
- Click "Create new key pair"
- Name: `whatsapp-bot-key`
- Type: RSA
- Format: .pem (or .ppk if using PuTTY)
- Download and save securely

**Network Settings:**
- Create security group
- Allow RDP (port 3389) from "My IP"

**Storage:** 30 GB gp3 (Free Tier eligible)

**Click:** Launch Instance

---

## Step 2: Connect to EC2

### 2.1 Get Windows Password
1. Wait 5-10 minutes for instance to initialize
2. Select your instance
3. Click **Connect** → **RDP client**
4. Click **Get Password**
5. Upload your `.pem` key file
6. Click **Decrypt Password**
7. Copy the password

### 2.2 Download RDP File
1. Click **Download remote desktop file**
2. Open the `.rdp` file
3. Enter the password you decrypted
4. Click **Yes** to trust the certificate

---

## Step 3: Setup EC2 Instance

### 3.1 Install Chrome
1. Open Edge browser on EC2
2. Download Chrome: https://www.google.com/chrome/
3. Install Chrome

### 3.2 Install Python
1. Download Python 3.11: https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"

### 3.3 Install ChromeDriver
1. Check Chrome version: Chrome → Settings → About Chrome
2. Download matching ChromeDriver: https://chromedriver.chromium.org/downloads
3. Extract `chromedriver.exe`
4. Move to `C:\Windows\System32\`

### 3.4 Create Project Folder
1. Open Command Prompt
2. Run:
```cmd
mkdir C:\whatsapp-bot
cd C:\whatsapp-bot
```

### 3.5 Upload Your Files
**Option A: Use RDP Copy-Paste**
- Copy files from your local PC
- Paste into EC2 `C:\whatsapp-bot\`

**Option B: Use S3**
```cmd
aws s3 cp s3://your-bucket/contacts.csv C:\whatsapp-bot\
```

**Files to upload:**
- `test_robust.py`
- `contacts.csv`

### 3.6 Install Python Dependencies
```cmd
cd C:\whatsapp-bot
python -m pip install pandas selenium
```

---

## Step 4: Initial WhatsApp Login

### 4.1 First Run (Manual QR Scan)
1. On EC2, open Command Prompt
2. Run:
```cmd
cd C:\whatsapp-bot
python test_robust.py
```
3. Chrome will open with WhatsApp Web
4. Scan QR code with your phone
5. Press Enter in Command Prompt
6. Let it send test message
7. **IMPORTANT:** Don't close Chrome yet!

### 4.2 Keep Session Alive
Create a modified script that keeps Chrome open:

**Create:** `C:\whatsapp-bot\bot_scheduled.py`
```python
import pandas as pd
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Profile directory to persist session
PROFILE_DIR = r"C:\whatsapp-bot\chrome-profile"

def send_messages():
    df = pd.read_csv('contacts.csv')
    
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-data-dir={PROFILE_DIR}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://web.whatsapp.com/")
        
        # Wait for WhatsApp to load
        print("Waiting for WhatsApp to load...")
        time.sleep(10)
        
        for index, row in df.iterrows():
            name = row['Name']
            phone = str(row['Phone']).replace('+', '').replace(' ', '')
            message = row['Message'].replace("{name}", name)
            
            print(f"Sending to {name}...")
            
            try:
                encoded_message = urllib.parse.quote(message)
                url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
                driver.get(url)
                time.sleep(5)
                
                selectors = [
                    '//button[@aria-label="Send"]',
                    '//span[@data-icon="send"]',
                ]
                
                for selector in selectors:
                    try:
                        send_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        send_button.click()
                        break
                    except:
                        continue
                
                print(f"✓ Sent to {name}")
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ Failed: {name} - {str(e)[:50]}")
                continue
        
        print("Completed!")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    send_messages()
```

---

## Step 5: Schedule Automation

### 5.1 Create Batch File
**Create:** `C:\whatsapp-bot\run_bot.bat`
```batch
@echo off
cd C:\whatsapp-bot
python bot_scheduled.py >> bot_log.txt 2>&1
```

### 5.2 Setup Task Scheduler
1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Basic Task**
3. Name: `WhatsApp Bot Daily`
4. Trigger: **Daily**
5. Time: Choose your preferred time (e.g., 9:00 AM)
6. Action: **Start a program**
   - Program: `C:\whatsapp-bot\run_bot.bat`
   - Start in: `C:\whatsapp-bot`
7. Click **Finish**

### 5.3 Test Scheduled Task
1. Right-click the task
2. Click **Run**
3. Check `C:\whatsapp-bot\bot_log.txt` for results

---

## Step 6: Keep EC2 Running

### 6.1 Prevent Auto-Shutdown
1. Open **Power Options**
2. Set "Turn off display" to **Never**
3. Set "Put computer to sleep" to **Never**

### 6.2 Auto-Login (Optional)
To avoid RDP login after restarts:
1. Press `Win + R`
2. Type: `netplwiz`
3. Uncheck "Users must enter a username and password"
4. Click OK
5. Enter your password

---

## Cost Estimate

**Free Tier (First 12 months):**
- EC2 t2.micro: 750 hours/month FREE
- 30 GB Storage: FREE
- Data Transfer: 15 GB/month FREE

**After Free Tier:**
- EC2 t3.micro: ~$7.50/month (if running 24/7)
- Storage: ~$2.40/month
- **Total: ~$10/month**

**Cost Optimization:**
- Stop instance when not needed
- Use t2.micro instead of t3.micro
- Schedule instance start/stop with Lambda

---

## Maintenance

### Check Logs
```cmd
type C:\whatsapp-bot\bot_log.txt
```

### Update Contacts
1. RDP to EC2
2. Edit `contacts.csv`
3. Save

### Re-scan QR Code (if session expires)
1. RDP to EC2
2. Delete `C:\whatsapp-bot\chrome-profile` folder
3. Run `python test_robust.py`
4. Scan QR code again

---

## Troubleshooting

**Issue: Chrome won't start**
- Reinstall ChromeDriver matching Chrome version

**Issue: WhatsApp session expired**
- Delete chrome-profile folder
- Re-scan QR code

**Issue: Task Scheduler not running**
- Check Task Scheduler History
- Verify batch file path
- Run batch file manually to test

**Issue: High costs**
- Stop EC2 when not needed
- Use Spot Instances (advanced)

---

## Security Best Practices

1. **Restrict RDP Access**
   - Only allow your IP in Security Group
   - Change RDP port from 3389 (advanced)

2. **Regular Updates**
   - Keep Windows updated
   - Update Python packages

3. **Backup**
   - Backup `contacts.csv` regularly
   - Create AMI snapshot monthly

4. **Monitor Costs**
   - Set up AWS Budget alerts
   - Check billing dashboard weekly

---

## Important Warnings

⚠️ **This violates WhatsApp Terms of Service**
- Your account may be banned
- Use at your own risk
- Consider official WhatsApp Business API for production

⚠️ **EC2 Costs**
- Free Tier is only 750 hours/month
- Monitor your usage
- Stop instance when not needed

⚠️ **Session Management**
- WhatsApp may log you out randomly
- You'll need to re-scan QR code
- No way to fully automate this

---

## Next Steps

1. ✅ Launch EC2 instance
2. ✅ Install software (Chrome, Python, ChromeDriver)
3. ✅ Upload your files
4. ✅ Scan QR code once
5. ✅ Setup Task Scheduler
6. ✅ Test automation
7. ✅ Monitor and maintain

Good luck! 🚀
