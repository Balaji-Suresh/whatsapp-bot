import pandas as pd
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Read CSV file
df = pd.read_csv('contacts.csv')

# Setup Chrome
options = webdriver.ChromeOptions()
options.add_argument('--user-data-dir=./chrome-profile')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--remote-debugging-port=9222')

from selenium.webdriver.chrome.service import Service
service = Service()
driver = webdriver.Chrome(service=service, options=options)

try:
    # Open WhatsApp Web
    driver.get("https://web.whatsapp.com/")
    print("Scan QR code and press Enter...")
    input()
    
    for index, row in df.iterrows():
        name = row['Name']
        phone = str(row['Phone']).replace('+', '').replace(' ', '')
        message = row['Message'].replace("{name}", name)
        
        encoded_message = urllib.parse.quote(message)
        url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
        
        driver.get(url)
        
        send_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
        )
        send_button.click()
        
        print(f"✓ Sent to {name}")
        time.sleep(3)
        
except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
