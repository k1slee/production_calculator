Write-Host "========================================" -ForegroundColor Green
Write-Host "   РЕЗЕРВНОЕ КОПИРОВАНИЕ БД" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$appPath = "C:\ProgramData\ProductionCalculator"
$backupPath = "C:\ProgramData\ProductionCalculator\backups"
$date = Get-Date -Format "yyyy-MM-dd_HH-mm"

# Создаем папку для бэкапов
New-Item -ItemType Directory -Force -Path $backupPath | Out-Null

# Копируем базу данных
if (Test-Path "$appPath\db.sqlite3") {
    $backupFile = "$backupPath\db_$date.sqlite3"
    Copy-Item "$appPath\db.sqlite3" $backupFile
    Write-Host "✓ База данных сохранена: $backupFile" -ForegroundColor Green
} else {
    Write-Host "✗ Файл базы данных не найден!" -ForegroundColor Red
}

# Показываем последние 5 бэкапов
Write-Host ""
Write-Host "Последние резервные копии:" -ForegroundColor Yellow
Get-ChildItem $backupPath -Filter "*.sqlite3" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | Format-Table Name, LastWriteTime

pause