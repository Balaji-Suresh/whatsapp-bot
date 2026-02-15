#!/bin/bash

# WhatsApp Bot AWS Deployment Script
set -e

echo "Starting WhatsApp Bot deployment..."

# Variables
STACK_NAME="whatsapp-bot-stack"
FUNCTION_NAME="whatsapp-bot"
REGION="us-east-1"

# Step 1: Deploy CloudFormation stack
echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
  --template-file infrastructure.yaml \
  --stack-name $STACK_NAME \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

# Get bucket name from stack outputs
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' \
  --output text \
  --region $REGION)

echo "S3 Bucket created: $BUCKET_NAME"

# Step 2: Create deployment package
echo "Creating deployment package..."
mkdir -p package
pip install -r requirements.txt -t package/
cp lambda_function.py package/

# Create zip file
cd package
zip -r ../whatsapp-bot.zip .
cd ..

# Step 3: Update Lambda function code
echo "Updating Lambda function code..."
aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --zip-file fileb://whatsapp-bot.zip \
  --region $REGION

# Step 4: Upload sample Excel file
echo "Uploading sample contacts file..."
aws s3 cp contacts.xlsx s3://$BUCKET_NAME/ --region $REGION

echo "Deployment completed successfully!"
echo "Bucket Name: $BUCKET_NAME"
echo "Function Name: $FUNCTION_NAME"
echo ""
echo "Next steps:"
echo "1. Upload your contacts.xlsx file to S3 bucket: $BUCKET_NAME"
echo "2. Test the function manually or enable the schedule"
echo "3. Check results in the S3 bucket under 'results/' folder"