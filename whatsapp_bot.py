import pandas as pd
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import os

def send_messages(excel_file='contacts.xlsx'):
    # Read contacts
    df = pd.read_excel(excel_file)
    
    # Setup Chrome
    options = Options()
    options.add_argument('--user-data-dir=./chrome-profile')
    
    driver = webdriver.Chrome(options=options)
    results = []
    
    try:
        # Login to WhatsApp Web
        driver.get("https://web.whatsapp.com/")
        print("Scan QR code to login...")
        input("Press Enter after scanning QR code...")
        
        for index, row in df.iterrows():
            name = row.iloc[0]
            phone = str(row.iloc[1]).replace('+', '').replace(' ', '')
            message = row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else f"Hello {name}!"
            
            personalized_message = message.replace("{name}", name)
            encoded_message = urllib.parse.quote(personalized_message)
            
            try:
                url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
                driver.get(url)
                
                send_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                )
                send_button.click()
                
                print(f"✓ Sent to {name} ({phone})")
                results.append({'name': name, 'phone': phone, 'status': 'sent'})
                time.sleep(3)
                
            except Exception as e:
                print(f"✗ Failed to send to {name}: {str(e)}")
                results.append({'name': name, 'phone': phone, 'status': 'failed', 'error': str(e)})
                
    finally:
        driver.quit()
    
    # Save results
    results_df = pd.DataFrame(results)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_df.to_csv(f'results_{timestamp}.csv', index=False)
    print(f"\nResults saved to results_{timestamp}.csv")
    
    successful = len([r for r in results if r['status'] == 'sent'])
    print(f"Completed: {successful}/{len(results)} messages sent")

if __name__ == '__main__':
    send_messages()
