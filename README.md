# WhatsApp Bot - AWS Free Tier Deployment

Automated WhatsApp messaging bot using AWS Free Tier services.

## Prerequisites

1. **AWS Account** with Free Tier access
2. **AWS CLI** installed and configured
3. **Python 3.9+** installed
4. **WhatsApp Web** access

## Quick Setup

### 1. Install Dependencies
```bash
pip install pandas openpyxl boto3
```

### 2. Configure AWS CLI
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your region (e.g., us-east-1)
# Enter output format (json)
```

### 3. Create Excel File
```bash
python create_excel.py
```

### 4. Deploy to AWS
**Windows:**
```bash
deploy.bat
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

## Manual Deployment Steps

### 1. Deploy Infrastructure
```bash
aws cloudformation deploy \
  --template-file infrastructure.yaml \
  --stack-name whatsapp-bot-stack \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### 2. Create Deployment Package
```bash
mkdir package
pip install -r requirements.txt -t package/
cp lambda_function.py package/
cd package && zip -r ../whatsapp-bot.zip . && cd ..
```

### 3. Update Lambda Function
```bash
aws lambda update-function-code \
  --function-name whatsapp-bot \
  --zip-file fileb://whatsapp-bot.zip \
  --region us-east-1
```

### 4. Upload Contacts File
```bash
# Get bucket name
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name whatsapp-bot-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' \
  --output text)

# Upload file
aws s3 cp contacts.xlsx s3://$BUCKET_NAME/
```

## Testing

### Manual Test
```bash
python test_function.py
```

### AWS Console Test
1. Go to Lambda console
2. Select `whatsapp-bot` function
3. Create test event with payload:
```json
{
  "excel_file": "contacts.xlsx"
}
```

## Excel File Format

| Name | Phone | Message |
|------|-------|---------|
| John Doe | +1234567890 | Hi {name}! Welcome to our service. |
| Jane Smith | +0987654321 | Hello {name}! This is a test message. |

## Important Notes

### WhatsApp Web Authentication
- Lambda runs headless, so you need to handle authentication
- Consider using WhatsApp Business API for production
- Current implementation requires manual QR code scanning

### Free Tier Limits
- **Lambda**: 1M requests/month, 400,000 GB-seconds
- **S3**: 5GB storage, 20,000 GET requests
- **EventBridge**: 14M events/month

### Compliance
- Get explicit consent before sending messages
- Follow WhatsApp Terms of Service
- Comply with local regulations (GDPR, CAN-SPAM)

## Troubleshooting

### Common Issues

1. **Chrome/ChromeDriver Issues**
   - Lambda layer includes Chrome and ChromeDriver
   - Ensure headless mode is enabled

2. **WhatsApp Authentication**
   - WhatsApp Web requires manual login
   - Consider alternative APIs for production

3. **Timeout Issues**
   - Increase Lambda timeout (max 15 minutes)
   - Reduce batch size for large contact lists

### Logs
Check CloudWatch logs:
```bash
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/whatsapp-bot
```

## Cost Optimization

- Use EventBridge to schedule runs (avoid continuous polling)
- Implement batch processing for large lists
- Monitor usage in AWS Cost Explorer

## Scaling Beyond Free Tier

1. **WhatsApp Business API** - Official, reliable, paid
2. **EC2 Instance** - More control, persistent sessions
3. **ECS/Fargate** - Container-based scaling

## Security Best Practices

- Store sensitive data in AWS Systems Manager Parameter Store
- Use IAM roles with minimal permissions
- Enable CloudTrail for audit logging
- Encrypt S3 buckets

## Support

For issues:
1. Check CloudWatch logs
2. Verify S3 bucket permissions
3. Test with small contact batches first