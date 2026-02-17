# Запустите от имени администратора
Write-Host "========================================" -ForegroundColor Green
Write-Host "   НАСТРОЙКА PRODUCTION CALCULATOR" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Проверяем Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Python не установлен!" -ForegroundColor Red
    Write-Host "Сначала запустите 01_install_python.ps1" -ForegroundColor Yellow
    pause
    exit
}
Write-Host "✓ Python установлен: $pythonVersion" -ForegroundColor Green

# Папка приложения
$appPath = "C:\ProgramData\ProductionCalculator"
Write-Host "Создание папки приложения: $appPath" -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $appPath | Out-Null

# Копируем файлы проекта (предполагаем, что они в той же папке что и скрипт)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Копирование файлов проекта..." -ForegroundColor Yellow
Copy-Item -Path "$scriptPath\*" -Destination $appPath -Recurse -Force -Exclude @("*.ps1", "venv")

Set-Location $appPath

# Создаем виртуальное окружение
Write-Host "Создание виртуального окружения..." -ForegroundColor Yellow
python -m venv venv

# Активируем и устанавливаем зависимости
Write-Host "Установка зависимостей..." -ForegroundColor Yellow
& "$appPath\venv\Scripts\Activate.ps1"
pip install --upgrade pip
pip install django
pip install django-crispy-forms
pip install crispy-bootstrap5
pip install xhtml2pdf
pip install reportlab
pip install gunicorn
pip install waitress

# Если есть requirements.txt
if (Test-Path "$appPath\requirements.txt") {
    pip install -r requirements.txt
}

# Создаем продакшен настройки
Write-Host "Настройка конфигурации..." -ForegroundColor Yellow

# Получаем IP сервера
$ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object -First 1).IPAddress
$hostname = $env:COMPUTERNAME

# Создаем локальный settings_prod.py
$settingsPath = "$appPath\production_calculator\settings_prod.py"
$settingsContent = @"
from .settings import *

DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '$hostname',
    '$ipAddress',
    '*',
]

# Статические файлы
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# Медиа файлы
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Безопасность
CSRF_COOKIE_SECURE = False  # В локальной сети можно False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
"@
$settingsContent | Out-File -FilePath $settingsPath -Encoding UTF8

# Настраиваем базу данных
Write-Host "Настройка базы данных..." -ForegroundColor Yellow
$env:DJANGO_SETTINGS_MODULE = "production_calculator.settings_prod"
python manage.py migrate
python manage.py collectstatic --noinput --clear

# Создаем суперпользователя (опционально)
Write-Host ""
Write-Host "Хотите создать суперпользователя? (y/n)" -ForegroundColor Yellow
$createSuperuser = Read-Host
if ($createSuperuser -eq 'y') {
    python manage.py createsuperuser
}

# Права доступа
Write-Host "Настройка прав доступа..." -ForegroundColor Yellow
icacls $appPath /grant "IIS_IUSRS:(OI)(CI)F" /T
icacls $appPath /grant "NETWORK SERVICE:(OI)(CI)F" /T
icacls $appPath /grant "NT AUTHORITY\SYSTEM:(OI)(CI)F" /T

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   НАСТРОЙКА ЗАВЕРШЕНА!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Путь к приложению: $appPath" -ForegroundColor Cyan
Write-Host "IP сервера: $ipAddress" -ForegroundColor Cyan
Write-Host "Имя сервера: $hostname" -ForegroundColor Cyan
Write-Host ""
Write-Host "Далее запустите:" -ForegroundColor Yellow
Write-Host "03_create_service.ps1 - для создания службы" -ForegroundColor White
Write-Host "04_firewall.ps1 - для открытия порта" -ForegroundColor White
Write-Host "05_test_run.ps1 - для тестового запуска" -ForegroundColor White
Write-Host ""
pause