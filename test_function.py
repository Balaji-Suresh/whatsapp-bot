import boto3
import json

def test_whatsapp_bot():
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Test payload
    payload = {
        "excel_file": "contacts.xlsx"
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='whatsapp-bot',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        result = json.loads(response['Payload'].read())
        print("Function Response:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error invoking function: {e}")

if __name__ == "__main__":
    test_whatsapp_bot()