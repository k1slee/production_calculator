# Запустите от имени администратора
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ТЕСТОВЫЙ ЗАПУСК СЕРВЕРА" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$appPath = "C:\ProgramData\ProductionCalculator"
$port = 8781

# Получаем IP сервера
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object -First 1).IPAddress
$hostname = $env:COMPUTERNAME

Set-Location $appPath

Write-Host "Активация виртуального окружения..." -ForegroundColor Yellow
& "$appPath\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Запуск сервера на порту $port..." -ForegroundColor Yellow
Write-Host "Доступные адреса:" -ForegroundColor Green
Write-Host "----------------------------------------"
Write-Host "На сервере: http://localhost:$port" -ForegroundColor White
Write-Host "По сети:    http://$ipAddress`:$port" -ForegroundColor White
Write-Host "По имени:   http://$hostname`:$port" -ForegroundColor White
Write-Host "----------------------------------------"
Write-Host ""
Write-Host "Для остановки нажмите Ctrl+C" -ForegroundColor Red
Write-Host ""

$env:DJANGO_SETTINGS_MODULE = "production_calculator.settings_prod"
python manage.py runserver 0.0.0.0:$port