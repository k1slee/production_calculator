# Запустите от имени администратора
Write-Host "========================================" -ForegroundColor Green
Write-Host "   СОЗДАНИЕ СЛУЖБЫ WINDOWS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$appPath = "C:\ProgramData\ProductionCalculator"
$pythonPath = "$appPath\venv\Scripts\python.exe"
$port = 8781
$serviceName = "ProductionCalculator"
$displayName = "Production Calculator Service"
$description = "Система расчета расходов материалов на производстве"

# Проверяем пути
if (-not (Test-Path $pythonPath)) {
    Write-Host "ОШИБКА: Python не найден по пути: $pythonPath" -ForegroundColor Red
    pause
    exit
}

# Скачиваем NSSM если нет
$nssmPath = "$appPath\nssm.exe"
if (-not (Test-Path $nssmPath)) {
    Write-Host "Скачивание NSSM (менеджер служб)..." -ForegroundColor Yellow
    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $nssmZip = "$appPath\nssm.zip"
    
    Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip
    Expand-Archive -Path $nssmZip -DestinationPath "$appPath" -Force
    
    # Копируем 64-битную версию
    Copy-Item "$appPath\nssm-2.24\win64\nssm.exe" "$appPath\nssm.exe" -Force
    
    # Очистка
    Remove-Item $nssmZip -Force
    Remove-Item "$appPath\nssm-2.24" -Recurse -Force
}

# Удаляем старую службу если есть
if (Get-Service $serviceName -ErrorAction SilentlyContinue) {
    Write-Host "Удаление старой службы..." -ForegroundColor Yellow
    Stop-Service $serviceName -Force -ErrorAction SilentlyContinue
    & $nssmPath remove $serviceName confirm
    Start-Sleep -Seconds 2
}

# Создаем новую службу
Write-Host "Создание службы на порту $port..." -ForegroundColor Yellow
& $nssmPath install $serviceName $pythonPath "manage.py runserver 0.0.0.0:$port --settings=production_calculator.settings_prod"

# Настройка службы
& $nssmPath set $serviceName DisplayName $displayName
& $nssmPath set $serviceName Description $description
& $nssmPath set $serviceName Start SERVICE_AUTO_START
& $nssmPath set $serviceName AppDirectory $appPath
& $nssmPath set $serviceName AppStdout "$appPath\logs\service.log"
& $nssmPath set $serviceName AppStderr "$appPath\logs\service-error.log"

# Создаем папку для логов
New-Item -ItemType Directory -Force -Path "$appPath\logs" | Out-Null

# Настройки окружения
& $nssmPath set $serviceName AppEnvironmentExtra DJANGO_SETTINGS_MODULE=production_calculator.settings_prod

# Настройка перезапуска при сбое
& $nssmPath set $serviceName AppRestartDelay 5000
& $nssmPath set $serviceName AppThrottle 0

# Даем права на папку
Write-Host "Настройка прав доступа..." -ForegroundColor Yellow
icacls $appPath /grant "NT AUTHORITY\SYSTEM:(OI)(CI)F" /T
icacls $appPath\logs /grant "NT AUTHORITY\SYSTEM:(OI)(CI)F" /T

# Запускаем службу
Write-Host "Запуск службы..." -ForegroundColor Yellow
Start-Service $serviceName

# Проверяем статус
Start-Sleep -Seconds 3
$service = Get-Service $serviceName

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "        СЛУЖБА СОЗДАНА!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Имя службы: $serviceName" -ForegroundColor Cyan
Write-Host "Порт: $port" -ForegroundColor Cyan
Write-Host "Статус: $($service.Status)" -ForegroundColor Cyan
Write-Host "Логи: $appPath\logs\service.log" -ForegroundColor Cyan
Write-Host ""
Write-Host "Управление службой:" -ForegroundColor Yellow
Write-Host "Start-Service $serviceName" -ForegroundColor White
Write-Host "Stop-Service $serviceName" -ForegroundColor White
Write-Host "Restart-Service $serviceName" -ForegroundColor White
Write-Host ""

# Открываем порт
Write-Host "Открыть порт в брандмауэре? (y/n)" -ForegroundColor Yellow
$openFirewall = Read-Host
if ($openFirewall -eq 'y') {
    & "$appPath\04_firewall.ps1"
}

pause