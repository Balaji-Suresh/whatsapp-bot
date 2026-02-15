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

def send_messages_multi_account(excel_file='contacts.xlsx', num_accounts=4):
    df = pd.read_excel(excel_file)
    results = []
    
    # Distribute contacts across accounts
    contacts_per_account = len(df) // num_accounts + (1 if len(df) % num_accounts else 0)
    
    for account_num in range(1, num_accounts + 1):
        profile_dir = f'./chrome-profile-{account_num}'
        start_idx = (account_num - 1) * contacts_per_account
        end_idx = min(start_idx + contacts_per_account, len(df))
        
        if start_idx >= len(df):
            break
            
        account_contacts = df.iloc[start_idx:end_idx]
        
        print(f"\n{'='*50}")
        print(f"Account {account_num}: Processing {len(account_contacts)} contacts")
        print(f"{'='*50}")
        
        options = Options()
        options.add_argument(f'--user-data-dir={profile_dir}')
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get("https://web.whatsapp.com/")
            
            if not os.path.exists(profile_dir) or len(os.listdir(profile_dir)) < 2:
                print(f"Scan QR code for Account {account_num}...")
                input(f"Press Enter after scanning QR code for Account {account_num}...")
            else:
                print(f"Using saved session for Account {account_num}")
                time.sleep(5)
            
            for index, row in account_contacts.iterrows():
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
                    
                    print(f"✓ [Account {account_num}] Sent to {name} ({phone})")
                    results.append({'account': account_num, 'name': name, 'phone': phone, 'status': 'sent'})
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"✗ [Account {account_num}] Failed to send to {name}: {str(e)}")
                    results.append({'account': account_num, 'name': name, 'phone': phone, 'status': 'failed', 'error': str(e)})
                    
        finally:
            driver.quit()
    
    # Save results
    results_df = pd.DataFrame(results)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_df.to_csv(f'results_{timestamp}.csv', index=False)
    print(f"\n{'='*50}")
    print(f"Results saved to results_{timestamp}.csv")
    
    successful = len([r for r in results if r['status'] == 'sent'])
    print(f"Completed: {successful}/{len(results)} messages sent")
    print(f"{'='*50}")

if __name__ == '__main__':
    send_messages_multi_account()
