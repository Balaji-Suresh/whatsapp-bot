import json
import boto3
import pandas as pd
from io import BytesIO
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    # Get configuration
    bucket_name = os.environ['S3_BUCKET']
    excel_key = event.get('excel_file', 'contacts.xlsx')
    
    try:
        # Download Excel file from S3
        response = s3.get_object(Bucket=bucket_name, Key=excel_key)
        excel_data = response['Body'].read()
        
        # Read contacts
        df = pd.read_excel(BytesIO(excel_data))
        
        # Setup Chrome for Lambda
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--user-data-dir=/tmp/chrome-user-data')
        
        driver = webdriver.Chrome('/opt/chromedriver', options=options)
        
        results = []
        
        try:
            # Login to WhatsApp Web (requires pre-authenticated session)
            driver.get("https://web.whatsapp.com/")
            time.sleep(5)
            
            for index, row in df.iterrows():
                name = row.iloc[0]
                phone = str(row.iloc[1]).replace('+', '').replace(' ', '')
                message = row.iloc[2] if len(row) > 2 and pd.notna(row.iloc[2]) else f"Hello {name}!"
                
                # Personalize message
                personalized_message = message.replace("{name}", name)
                encoded_message = urllib.parse.quote(personalized_message)
                
                try:
                    # Navigate to chat
                    url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
                    driver.get(url)
                    
                    # Wait and click send
                    send_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                    )
                    send_button.click()
                    
                    results.append({
                        'name': name,
                        'phone': phone,
                        'status': 'sent'
                    })
                    
                    time.sleep(3)  # Delay between messages
                    
                except Exception as e:
                    results.append({
                        'name': name,
                        'phone': phone,
                        'status': 'failed',
                        'error': str(e)
                    })
                    
        finally:
            driver.quit()
        
        # Save results to S3
        results_df = pd.DataFrame(results)
        csv_buffer = BytesIO()
        results_df.to_csv(csv_buffer, index=False)
        
        s3.put_object(
            Bucket=bucket_name,
            Key=f'results/campaign_{context.aws_request_id}.csv',
            Body=csv_buffer.getvalue()
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Campaign completed. Processed {len(results)} contacts.',
                'successful': len([r for r in results if r['status'] == 'sent']),
                'failed': len([r for r in results if r['status'] == 'failed'])
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }