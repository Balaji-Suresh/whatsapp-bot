import pandas as pd
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
from datetime import datetime

# Profile directory to persist WhatsApp session
PROFILE_DIR = r"C:\whatsapp-bot\chrome-profile"

def send_messages():
    print(f"\n{'='*50}")
    print(f"WhatsApp Bot Started: {datetime.now()}")
    print(f"{'='*50}\n")
    
    # Read contacts
    df = pd.read_csv('contacts.csv')
    print(f"Loaded {len(df)} contacts\n")
    
    # Setup Chrome with auto-installed ChromeDriver
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-data-dir={PROFILE_DIR}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-notifications')
    
    # Auto-install ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get("https://web.whatsapp.com/")
        print("Waiting for WhatsApp to load...")
        time.sleep(10)
        
        success_count = 0
        fail_count = 0
        
        for index, row in df.iterrows():
            name = row['Name']
            phone = str(row['Phone']).replace('+', '').replace(' ', '')
            message = row['Message'].replace("{name}", name)
            
            print(f"[{index+1}/{len(df)}] Sending to {name} ({phone})...")
            
            try:
                encoded_message = urllib.parse.quote(message)
                url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
                driver.get(url)
                time.sleep(5)
                
                # Try multiple selectors
                send_button = None
                selectors = [
                    '//button[@aria-label="Send"]',
                    '//span[@data-icon="send"]',
                    '//button[contains(@class, "send")]',
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
                
                if send_button:
                    print(f"  ✓ Sent successfully")
                    success_count += 1
                else:
                    print(f"  ❌ Failed - Send button not found")
                    fail_count += 1
                
                time.sleep(3)
                
            except Exception as e:
                print(f"  ❌ Failed - {str(e)[:50]}")
                fail_count += 1
                continue
        
        print(f"\n{'='*50}")
        print(f"Campaign Completed: {datetime.now()}")
        print(f"Success: {success_count} | Failed: {fail_count}")
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"\n❌ Critical Error: {e}\n")
    finally:
        driver.quit()

if __name__ == "__main__":
    send_messages()
