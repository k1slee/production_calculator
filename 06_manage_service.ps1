# Запустите от имени администратора
Write-Host "========================================" -ForegroundColor Green
Write-Host "   УПРАВЛЕНИЕ СЛУЖБОЙ" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$serviceName = "ProductionCalculator"
$appPath = "C:\ProgramData\ProductionCalculator"
$nssmPath = "$appPath\nssm.exe"

$service = Get-Service $serviceName -ErrorAction SilentlyContinue

if (-not $service) {
    Write-Host "ОШИБКА: Служба '$serviceName' не найдена!" -ForegroundColor Red
    pause
    exit
}

Write-Host "Текущий статус: $($service.Status)" -ForegroundColor Cyan
Write-Host ""

Write-Host "Выберите действие:" -ForegroundColor Yellow
Write-Host "1. Запустить службу" -ForegroundColor White
Write-Host "2. Остановить службу" -ForegroundColor White
Write-Host "3. Перезапустить службу" -ForegroundColor White
Write-Host "4. Посмотреть логи" -ForegroundColor White
Write-Host "5. Удалить службу" -ForegroundColor White
Write-Host "6. Выход" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Ваш выбор (1-6)"

switch ($choice) {
    "1" {
        Write-Host "Запуск службы..." -ForegroundColor Yellow
        Start-Service $serviceName
        Start-Sleep -Seconds 2
        Write-Host "Статус: $(Get-Service $serviceName | Select-Object -ExpandProperty Status)" -ForegroundColor Green
    }
    "2" {
        Write-Host "Остановка службы..." -ForegroundColor Yellow
        Stop-Service $serviceName -Force
        Start-Sleep -Seconds 2
        Write-Host "Статус: $(Get-Service $serviceName | Select-Object -ExpandProperty Status)" -ForegroundColor Green
    }
    "3" {
        Write-Host "Перезапуск службы..." -ForegroundColor Yellow
        Restart-Service $serviceName -Force
        Start-Sleep -Seconds 3
        Write-Host "Статус: $(Get-Service $serviceName | Select-Object -ExpandProperty Status)" -ForegroundColor Green
    }
    "4" {
        Write-Host "Последние 50 строк лога:" -ForegroundColor Yellow
        if (Test-Path "$appPath\logs\service.log") {
            Get-Content "$appPath\logs\service.log" -Tail 50
        } else {
            Write-Host "Лог-файл не найден" -ForegroundColor Red
        }
        Write-Host ""
        Write-Host "Ошибки:" -ForegroundColor Yellow
        if (Test-Path "$appPath\logs\service-error.log") {
            Get-Content "$appPath\logs\service-error.log" -Tail 20
        } else {
            Write-Host "Файл ошибок не найден" -ForegroundColor Red
        }
    }
    "5" {
        Write-Host "Удаление службы..." -ForegroundColor Red
        $confirm = Read-Host "Вы уверены? (y/n)"
        if ($confirm -eq 'y') {
            Stop-Service $serviceName -Force -ErrorAction SilentlyContinue
            & $nssmPath remove $serviceName confirm
            Write-Host "Служба удалена" -ForegroundColor Green
        }
    }
    "6" {
        exit
    }
}

pause