# Запустите от имени администратора
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ОТКРЫТИЕ ПОРТА В БРАНДМАУЭРЕ" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$port = 8781
$ruleName = "ProductionCalculator Port $port"

# Проверяем, существует ли правило
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
if ($existingRule) {
    Write-Host "Удаление существующего правила..." -ForegroundColor Yellow
    Remove-NetFirewallRule -DisplayName $ruleName
}

# Создаем новое правило
Write-Host "Открытие порта $port..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName $ruleName `
                    -Direction Inbound `
                    -Protocol TCP `
                    -LocalPort $port `
                    -Action Allow `
                    -Enabled True `
                    -Profile Any | Out-Null

Write-Host "✓ Порт $port открыт в брандмауэре" -ForegroundColor Green

# Получаем IP сервера
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object -First 1).IPAddress
$hostname = $env:COMPUTERNAME

Write-Host ""
Write-Host "Сервер доступен по:" -ForegroundColor Cyan
Write-Host "http://$hostname`:$port" -ForegroundColor White
Write-Host "http://$ipAddress`:$port" -ForegroundColor White
Write-Host "http://localhost:$port (на сервере)" -ForegroundColor White
Write-Host ""

# Проверка правил
Write-Host "Проверка правил брандмауэра:" -ForegroundColor Yellow
Get-NetFirewallRule -DisplayName "ProductionCalculator*" | Format-Table DisplayName, Enabled, Direction, Action -AutoSize

pause