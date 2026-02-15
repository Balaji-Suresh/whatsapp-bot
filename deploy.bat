@echo off
echo Starting WhatsApp Bot deployment...

REM Variables
set STACK_NAME=whatsapp-bot-stack
set FUNCTION_NAME=whatsapp-bot
set REGION=us-east-1

REM Step 1: Deploy CloudFormation stack
echo Deploying CloudFormation stack...
aws cloudformation deploy ^
  --template-file infrastructure.yaml ^
  --stack-name %STACK_NAME% ^
  --capabilities CAPABILITY_NAMED_IAM ^
  --region %REGION%

REM Get bucket name from stack outputs
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue" --output text --region %REGION%') do set BUCKET_NAME=%%i

echo S3 Bucket created: %BUCKET_NAME%

REM Step 2: Create deployment package
echo Creating deployment package...
if exist package rmdir /s /q package
mkdir package
python -m pip install -r requirements.txt -t package
copy lambda_function.py package\

REM Create zip file
cd package
powershell Compress-Archive -Path * -DestinationPath ..\whatsapp-bot.zip -Force
cd ..

REM Step 3: Update Lambda function code
echo Updating Lambda function code...
aws lambda update-function-code ^
  --function-name %FUNCTION_NAME% ^
  --zip-file fileb://whatsapp-bot.zip ^
  --region %REGION%

REM Step 4: Upload sample Excel file
echo Uploading sample contacts file...
aws s3 cp contacts.xlsx s3://%BUCKET_NAME%/ --region %REGION%

echo Deployment completed successfully!
echo Bucket Name: %BUCKET_NAME%
echo Function Name: %FUNCTION_NAME%
echo.
echo Next steps:
echo 1. Upload your contacts.xlsx file to S3 bucket: %BUCKET_NAME%
echo 2. Test the function manually or enable the schedule
echo 3. Check results in the S3 bucket under 'results/' folder

pause