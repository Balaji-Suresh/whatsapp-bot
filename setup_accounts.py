import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

def setup_accounts(num_accounts=4):
    """Setup and authenticate multiple WhatsApp accounts"""
    
    for account_num in range(1, num_accounts + 1):
        profile_dir = f'./chrome-profile-{account_num}'
        
        print(f"\n{'='*50}")
        print(f"Setting up Account {account_num}")
        print(f"{'='*50}")
        
        options = Options()
        options.add_argument(f'--user-data-dir={profile_dir}')
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get("https://web.whatsapp.com/")
            print(f"\nScan QR code with WhatsApp number {account_num}")
            input(f"Press Enter after scanning QR code for Account {account_num}...")
            
            print(f"✓ Account {account_num} authenticated successfully!")
            time.sleep(2)
            
        finally:
            driver.quit()
    
    print(f"\n{'='*50}")
    print(f"All {num_accounts} accounts setup complete!")
    print("You can now run run_multi_bot.bat")
    print(f"{'='*50}")

if __name__ == '__main__':
    setup_accounts()
