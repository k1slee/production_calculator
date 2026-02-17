Write-Host "========================================" -ForegroundColor Green
Write-Host "   ПРОВЕРКА ПОРТА 8781" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$port = 8781

# Проверка через netstat
Write-Host "Проверка через netstat:" -ForegroundColor Yellow
$connections = netstat -ano | findstr ":$port"
if ($connections) {
    Write-Host "Порт $port ЗАНЯТ:" -ForegroundColor Red
    $connections
    
    # Получаем PID
    $lines = $connections -split "`n"
    foreach ($line in $lines) {
        if ($line -match "LISTENING\s+(\d+)$") {
            $pid = $matches[1]
            Write-Host ""
            Write-Host "Процесс с PID $pid:" -ForegroundColor Yellow
            Get-Process -Id $pid -ErrorAction SilentlyContinue | Format-List ProcessName, Id, CPU, StartTime
        }
    }
} else {
    Write-Host "Порт $port СВОБОДЕН!" -ForegroundColor Green
}

# Проверка доступности из сети
Write-Host ""
Write-Host "Проверка доступности из локальной сети:" -ForegroundColor Yellow
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object -First 1).IPAddress

try {
    $request = [System.Net.HttpWebRequest]::Create("http://$ipAddress`:$port")
    $request.Timeout = 3000
    $response = $request.GetResponse()
    Write-Host "✓ Сервер доступен по http://$ipAddress`:$port" -ForegroundColor Green
    $response.Close()
} catch {
    Write-Host "✗ Сервер НЕ доступен по http://$ipAddress`:$port" -ForegroundColor Red
    Write-Host "Возможно, сервер не запущен или брандмауэр блокирует порт" -ForegroundColor Yellow
}

pause