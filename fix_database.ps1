# Quick Fix Script for Active Column Error
# Run this script to fix the "no such column: users_profile.active" error

Write-Host "`n=== FIXING DATABASE SCHEMA ===" -ForegroundColor Cyan
Write-Host "Error: users_profile.active column missing`n" -ForegroundColor Yellow

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    
    Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    
    Write-Host "`nRunning migrations..." -ForegroundColor Yellow
    python manage.py migrate users
    python manage.py migrate
    
    Write-Host "`n=== FIX COMPLETE ===" -ForegroundColor Green
    Write-Host "Database schema updated successfully!" -ForegroundColor Green
    Write-Host "`nYou can now run the server:" -ForegroundColor Cyan
    Write-Host "  python manage.py runserver`n" -ForegroundColor White
    
} elseif (Test-Path "hy_env\Scripts\Activate.ps1") {
    Write-Host "✓ Virtual environment (hy_env) found" -ForegroundColor Green
    
    Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
    & "hy_env\Scripts\Activate.ps1"
    
    Write-Host "`nRunning migrations..." -ForegroundColor Yellow
    python manage.py migrate users
    python manage.py migrate
    
    Write-Host "`n=== FIX COMPLETE ===" -ForegroundColor Green
    Write-Host "Database schema updated successfully!" -ForegroundColor Green
    Write-Host "`nYou can now run the server:" -ForegroundColor Cyan
    Write-Host "  python manage.py runserver`n" -ForegroundColor White
    
} else {
    Write-Host "✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host "`nPlease activate your virtual environment first:" -ForegroundColor Yellow
    Write-Host "  venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "`nThen run migrations manually:" -ForegroundColor Yellow
    Write-Host "  python manage.py migrate users" -ForegroundColor White
    Write-Host "  python manage.py migrate`n" -ForegroundColor White
}
