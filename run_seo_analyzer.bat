@echo off
echo ========================================
echo    SEO Analyzer - Запуск приложения
echo ========================================
echo.

echo Проверка Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не установлен!
    echo Скачайте Python с https://python.org
    echo Убедитесь, что Python добавлен в PATH
    pause
    exit /b 1
)

echo Python найден!
echo.

echo Проверка зависимостей...
if not exist "requirements.txt" (
    echo ОШИБКА: Файл requirements.txt не найден!
    echo Убедитесь, что вы находитесь в папке проекта
    pause
    exit /b 1
)

echo Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo ОШИБКА: Не удалось установить зависимости!
    echo Проверьте интернет-соединение
    pause
    exit /b 1
)

echo.
echo Запуск SEO Analyzer...
echo.

python main.py

echo.
echo Приложение завершено.
pause 