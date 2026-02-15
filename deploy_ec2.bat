@echo off
echo ========================================
echo WhatsApp Bot - EC2 Automated Deployment
echo ========================================
echo.

REM Variables
set STACK_NAME=whatsapp-bot-ec2-stack
set REGION=us-east-1
set KEY_NAME=whatsapp-bot-key

REM Step 1: Check if key pair exists, if not create it
echo Checking for EC2 key pair...
aws ec2 describe-key-pairs --key-names %KEY_NAME% --region %REGION% >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Creating new key pair...
    aws ec2 create-key-pair --key-name %KEY_NAME% --query "KeyMaterial" --output text --region %REGION% > %KEY_NAME%.pem
    echo Key pair saved to %KEY_NAME%.pem
    echo IMPORTANT: Save this file securely!
) else (
    echo Key pair already exists.
)

REM Step 2: Get your public IP
echo.
echo Getting your public IP address...
for /f %%i in ('curl -s https://checkip.amazonaws.com') do set MY_IP=%%i
echo Your IP: %MY_IP%

REM Step 3: Deploy CloudFormation stack
echo.
echo Deploying CloudFormation stack...
echo This will take 5-10 minutes...
aws cloudformation deploy ^
  --template-file ec2-infrastructure.yaml ^
  --stack-name %STACK_NAME% ^
  --parameter-overrides KeyPairName=%KEY_NAME% MyIPAddress=%MY_IP%/32 ^
  --capabilities CAPABILITY_IAM ^
  --region %REGION%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Deployment failed! Check the error above.
    pause
    exit /b 1
)

REM Step 4: Get stack outputs
echo.
echo Getting stack information...
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey==`InstancePublicIP`].OutputValue" --output text --region %REGION%') do set INSTANCE_IP=%%i
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue" --output text --region %REGION%') do set BUCKET_NAME=%%i
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --query "Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue" --output text --region %REGION%') do set INSTANCE_ID=%%i

echo.
echo ========================================
echo Deployment Successful!
echo ========================================
echo Instance ID: %INSTANCE_ID%
echo Public IP: %INSTANCE_IP%
echo S3 Bucket: %BUCKET_NAME%
echo.

REM Step 5: Wait for instance to be ready
echo Waiting for instance to initialize (this takes 5-10 minutes)...
echo You can check status in EC2 console: https://console.aws.amazon.com/ec2/
echo.

timeout /t 300 /nobreak

REM Step 6: Upload bot files to S3
echo.
echo Uploading bot files to S3...
aws s3 cp bot_scheduled.py s3://%BUCKET_NAME%/ --region %REGION%
aws s3 cp contacts.csv s3://%BUCKET_NAME%/ --region %REGION%
aws s3 cp run_bot.bat s3://%BUCKET_NAME%/ --region %REGION%

echo.
echo ========================================
echo Next Steps (MANUAL):
echo ========================================
echo.
echo 1. Get Windows Password:
echo    - Go to EC2 Console
echo    - Select instance: %INSTANCE_ID%
echo    - Actions ^> Security ^> Get Windows Password
echo    - Upload %KEY_NAME%.pem
echo    - Copy the password
echo.
echo 2. Connect via RDP:
echo    - IP Address: %INSTANCE_IP%
echo    - Username: Administrator
echo    - Password: (from step 1)
echo.
echo 3. On the EC2 instance, run in PowerShell:
echo    aws s3 cp s3://%BUCKET_NAME%/bot_scheduled.py C:\whatsapp-bot\
echo    aws s3 cp s3://%BUCKET_NAME%/contacts.csv C:\whatsapp-bot\
echo    aws s3 cp s3://%BUCKET_NAME%/run_bot.bat C:\whatsapp-bot\
echo.
echo 4. Run the bot once to scan QR code:
echo    cd C:\whatsapp-bot
echo    python bot_scheduled.py
echo.
echo 5. Setup Task Scheduler (see EC2_SETUP_GUIDE.md)
echo.
echo ========================================
echo.

pause
