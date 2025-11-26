# Quick Setup Script for Email Notifications

# Step 1: Install python-dotenv
Write-Host "Installing python-dotenv..." -ForegroundColor Green
pip install python-dotenv

# Step 2: Create .env file if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Green
    Copy-Item .env.example .env
    Write-Host ".env file created. Please edit it with your email credentials." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "IMPORTANT: You need to:" -ForegroundColor Red
    Write-Host "1. Generate a Gmail App Password at: https://myaccount.google.com/apppasswords" -ForegroundColor Yellow
    Write-Host "2. Edit .env file and add your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD" -ForegroundColor Yellow
    Write-Host "3. Set DEFAULT_FROM_EMAIL to your Gmail address" -ForegroundColor Yellow
} else {
    Write-Host ".env file already exists." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setup complete! Check EMAIL_SETUP.md for detailed instructions." -ForegroundColor Green
