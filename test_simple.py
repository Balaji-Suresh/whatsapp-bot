import pandas as pd
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Read CSV file
df = pd.read_csv('contacts.csv')

# Setup Chrome - simpler version
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')

driver = webdriver.Chrome(options=options)

try:
    # Open WhatsApp Web
    driver.get("https://web.whatsapp.com/")
    print("\n=== SCAN QR CODE WITH YOUR PHONE ===")
    print("1. Open WhatsApp on your phone")
    print("2. Go to Settings > Linked Devices")
    print("3. Tap 'Link a Device'")
    print("4. Scan the QR code in the browser")
    print("\nAfter scanning, press Enter here...")
    input()
    
    print("\nStarting to send messages...\n")
    
    for index, row in df.iterrows():
        name = row['Name']
        phone = str(row['Phone']).replace('+', '').replace(' ', '')
        message = row['Message'].replace("{name}", name)
        
        encoded_message = urllib.parse.quote(message)
        url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
        
        print(f"Sending to {name} ({phone})...")
        driver.get(url)
        
        send_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
        )
        send_button.click()
        
        print(f"✓ Sent to {name}")
        time.sleep(3)
    
    print("\n=== ALL MESSAGES SENT ===")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    print("\nClosing browser in 5 seconds...")
    time.sleep(5)
    driver.quit()
