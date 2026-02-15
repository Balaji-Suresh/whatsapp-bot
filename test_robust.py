import pandas as pd
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Read CSV file
df = pd.read_csv('contacts.csv')

# Setup Chrome
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
    
    print("\nWaiting for WhatsApp to load...")
    time.sleep(5)
    
    print("\nStarting to send messages...\n")
    
    for index, row in df.iterrows():
        name = row['Name']
        phone = str(row['Phone']).replace('+', '').replace(' ', '')
        message = row['Message'].replace("{name}", name)
        
        print(f"Sending to {name} ({phone})...")
        
        try:
            # Navigate to chat
            encoded_message = urllib.parse.quote(message)
            url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
            driver.get(url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Try multiple selectors for send button
            send_button = None
            selectors = [
                '//button[@aria-label="Send"]',
                '//span[@data-icon="send"]',
                '//button[contains(@class, "send")]',
                '//*[@data-testid="send"]'
            ]
            
            for selector in selectors:
                try:
                    send_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if send_button:
                send_button.click()
                print(f"✓ Sent to {name}")
                time.sleep(3)
            else:
                # Alternative: Press Enter key
                print(f"Trying alternative method for {name}...")
                message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                message_box.send_keys(Keys.ENTER)
                print(f"✓ Sent to {name}")
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ Failed to send to {name}: {str(e)[:100]}")
            continue
    
    print("\n=== COMPLETED ===")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    print("\nClosing browser in 5 seconds...")
    time.sleep(5)
    driver.quit()
