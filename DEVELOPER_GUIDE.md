# 🛠️ Руководство разработчика SEO Analyzer

## 📋 Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Архитектура приложения](#архитектура-приложения)
3. [Установка и настройка](#установка-и-настройка)
4. [Структура кода](#структура-кода)
5. [Основные модули](#основные-модули)
6. [База данных](#база-данных)
7. [API и интеграции](#api-и-интеграции)
8. [Тестирование](#тестирование)
9. [Развертывание](#развертывание)
10. [Устранение неполадок](#устранение-неполадок)
11. [Рекомендации по улучшению](#рекомендации-по-улучшению)

---

## 🎯 Обзор проекта

### Назначение

SEO Analyzer - это комплексное приложение для анализа веб-сайтов с функциями:

- SEO-анализ страниц
- Отслеживание позиций в поисковых системах
- Генерация отчетов
- Анализ конкурентов

### Технологический стек

- **Frontend**: Flet (Python UI framework)
- **Backend**: Python 3.8+
- **База данных**: SQLite
- **Веб-скрапинг**: Selenium + BeautifulSoup
- **Анализ данных**: Pandas, Matplotlib
- **Отчеты**: Excel (openpyxl), Word (python-docx)

---

## 🏗️ Архитектура приложения

### Структура файлов

```
SEO new/
├── main.py                    # Главный файл приложения
├── serp_tracker.py            # Базовый SERP трекер
├── serp_tracker_advanced.py   # Расширенный SERP трекер
├── requirements.txt           # Зависимости
├── assets/                    # Ресурсы (иконки, изображения)
├── reports/                   # Сгенерированные отчеты
├── screenshots/              # Скриншоты страниц
└── *.db                      # Базы данных SQLite
```

### Основные компоненты

#### 1. Главный модуль (main.py)

- **Назначение**: Основной интерфейс приложения
- **Ключевые функции**:
  - `run_test()` - полный SEO-анализ
  - `run_links_test()` - анализ ссылок
  - `analyze_keywords()` - анализ ключевых слов
  - `check_seo_files()` - проверка robots.txt и sitemap.xml

#### 2. SERP Трекер (serp_tracker.py)

- **Назначение**: Отслеживание позиций в поисковых системах
- **Ключевые классы**:
  - `SERPTracker` - основной класс трекера
  - `run_serp_tracking()` - функция запуска трекинга
  - `run_detailed_site_analysis()` - детальный анализ сайта

#### 3. WebDriver Manager

- **Назначение**: Управление браузером для скрапинга
- **Функции**:
  - `create_webdriver()` - создание драйвера
  - Обход блокировок и капчи
  - Ротация User-Agent

---

## ⚙️ Установка и настройка

### Системные требования

- **ОС**: Windows 10/11
- **Python**: 3.8+
- **RAM**: 4 GB (рекомендуется 8 GB)
- **Место на диске**: 500 MB
- **Интернет**: требуется для анализа сайтов

### Установка зависимостей

```bash
# Клонирование репозитория
git clone <repository-url>
cd seo-analyzer

# Создание виртуального окружения
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Установка зависимостей
pip install -r requirements.txt
```

### Ключевые зависимости

```python
# Основные библиотеки
flet                    # UI framework
selenium               # Веб-скрапинг
webdriver-manager      # Управление драйверами
requests               # HTTP запросы
beautifulsoup4         # Парсинг HTML
pandas                 # Анализ данных
openpyxl               # Excel отчеты
python-docx            # Word отчеты
matplotlib             # Графики
seaborn                # Визуализация
```

### Настройка окружения

#### 1. Переменные окружения

Создайте файл `.env`:

```env
# Настройки базы данных
DB_PATH=serp_tracker.db

# Настройки API (если используются)
GOOGLE_API_KEY=your_api_key
YANDEX_API_KEY=your_api_key

# Настройки логирования
LOG_LEVEL=INFO
LOG_FILE=seo_log.txt
```

#### 2. Настройка ChromeDriver

```python
# Автоматическая загрузка (рекомендуется)
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Ручная настройка
# 1. Скачайте ChromeDriver с https://chromedriver.chromium.org/
# 2. Добавьте путь в PATH или укажите в коде
```

---

## 📁 Структура кода

### Основные функции main.py

#### 1. Функции анализа

```python
def run_test(site_url, summary_area, page, progress_bar, ignore_ssl, target_keywords):
    """Полный SEO-анализ сайта"""
    # Проверка доступности
    # Анализ мета-тегов
    # Проверка ссылок
    # Анализ изображений
    # Генерация отчета

def analyze_keywords(driver, site_url, target_keywords):
    """Анализ ключевых слов с учетом склонений"""
    # Извлечение текста
    # Подсчет частоты
    # Анализ плотности
    # Генерация склонений

def check_seo_files(site_url, ignore_ssl):
    """Проверка robots.txt и sitemap.xml"""
    # Проверка доступности
    # Парсинг содержимого
    # Валидация структуры
```

#### 2. Функции WebDriver

```python
def create_webdriver(ignore_ssl=False, window_size=None, anti_bot_mode=False):
    """Создание WebDriver с настройками"""
    # Настройка опций Chrome
    # Обход блокировок
    # Ротация User-Agent
    # Настройка прокси (если нужно)

def check_site_accessibility(site_url, ignore_ssl=False):
    """Проверка доступности сайта"""
    # Множественные методы доступа
    # Обход блокировок
    # Анализ ответов
```

#### 3. Функции отчетов

```python
def save_results(site_url, log_content, summary_content, report_type='full', format='excel'):
    """Сохранение результатов анализа"""
    # Парсинг данных
    # Создание DataFrame
    # Экспорт в Excel/Word

def generate_report(summary, site_url, report_type='full', format='txt'):
    """Генерация отчетов"""
    # Форматирование данных
    # Создание файлов
    # Сохранение результатов
```

### Основные классы serp_tracker.py

#### 1. Класс SERPTracker

```python
class SERPTracker:
    def __init__(self, db_path="serp_tracker.db"):
        """Инициализация трекера"""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Инициализация базы данных"""
        # Создание таблиц
        # Настройка индексов
        # Проверка структуры

    def add_site(self, domain, name=None):
        """Добавление сайта для отслеживания"""
        # Валидация домена
        # Сохранение в БД
        # Возврат ID

    def add_keyword(self, site_id, keyword, search_engine="google"):
        """Добавление ключевого слова"""
        # Проверка уникальности
        # Сохранение в БД
        # Связь с сайтом

    def track_keyword(self, keyword_id, keyword, domain, search_engine="google"):
        """Отслеживание позиции по ключевому слову"""
        # Поиск в Google/Yandex
        # Анализ результатов
        # Сохранение позиции
```

#### 2. Функции поиска

```python
def search_google(self, keyword, max_results=10):
    """Поиск в Google"""
    # Настройка запроса
    # Парсинг результатов
    # Извлечение позиций

def search_yandex(self, keyword, max_results=10):
    """Поиск в Yandex"""
    # Настройка запроса
    # Парсинг результатов
    # Извлечение позиций
```

---

## 🗄️ База данных

### Структура таблиц

#### 1. Таблица sites

```sql
CREATE TABLE sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Таблица keywords

```sql
CREATE TABLE keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER,
    keyword TEXT NOT NULL,
    search_engine TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (site_id) REFERENCES sites (id),
    UNIQUE(site_id, keyword, search_engine)
);
```

#### 3. Таблица positions

```sql
CREATE TABLE positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER,
    position INTEGER,
    url TEXT,
    title TEXT,
    snippet TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (keyword_id) REFERENCES keywords (id)
);
```

### Операции с базой данных

#### 1. Подключение

```python
import sqlite3

def get_connection():
    """Получение соединения с БД"""
    return sqlite3.connect(self.db_path)

def close_connection(conn):
    """Закрытие соединения"""
    conn.close()
```

#### 2. CRUD операции

```python
def add_record(self, table, data):
    """Добавление записи"""
    conn = self.get_connection()
    cursor = conn.cursor()

    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

    cursor.execute(query, list(data.values()))
    conn.commit()
    conn.close()

    return cursor.lastrowid

def get_records(self, table, conditions=None):
    """Получение записей"""
    conn = self.get_connection()
    cursor = conn.cursor()

    query = f"SELECT * FROM {table}"
    if conditions:
        query += f" WHERE {conditions}"

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    return results
```

---

## 🔌 API и интеграции

### Интеграция с поисковыми системами

#### 1. Google Search API

```python
def search_google_api(keyword, api_key):
    """Поиск через Google Search API"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': 'your_search_engine_id',
        'q': keyword,
        'num': 10
    }

    response = requests.get(url, params=params)
    return response.json()
```

#### 2. Yandex Search API

```python
def search_yandex_api(keyword, api_key):
    """Поиск через Yandex Search API"""
    url = "https://yandex.ru/search/xml"
    params = {
        'user': 'your_username',
        'key': api_key,
        'query': keyword,
        'maxpassages': 10
    }

    response = requests.get(url, params=params)
    return response.text
```

### Интеграция с внешними сервисами

#### 1. Google Analytics

```python
def get_analytics_data(property_id, start_date, end_date):
    """Получение данных из Google Analytics"""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    credentials = service_account.Credentials.from_service_account_file(
        'path/to/service-account-key.json',
        scopes=['https://www.googleapis.com/auth/analytics.readonly']
    )

    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    response = analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': property_id,
                    'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                    'metrics': [{'expression': 'ga:sessions'}],
                    'dimensions': [{'name': 'ga:date'}]
                }
            ]
        }
    ).execute()

    return response
```

#### 2. Google Search Console

```python
def get_search_console_data(site_url, start_date, end_date):
    """Получение данных из Google Search Console"""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    credentials = service_account.Credentials.from_service_account_file(
        'path/to/service-account-key.json',
        scopes=['https://www.googleapis.com/auth/webmasters.readonly']
    )

    service = build('searchconsole', 'v1', credentials=credentials)

    request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['query', 'page'],
        'rowLimit': 1000
    }

    response = service.searchAnalytics().query(
        siteUrl=site_url,
        body=request
    ).execute()

    return response
```

---

## 🧪 Тестирование

### Типы тестов

#### 1. Модульные тесты

```python
import unittest
from unittest.mock import Mock, patch

class TestSERPTracker(unittest.TestCase):
    def setUp(self):
        """Настройка тестового окружения"""
        self.tracker = SERPTracker(":memory:")

    def test_add_site(self):
        """Тест добавления сайта"""
        site_id = self.tracker.add_site("example.com", "Test Site")
        self.assertIsNotNone(site_id)

        sites = self.tracker.get_sites()
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites[0]['domain'], "example.com")

    def test_add_keyword(self):
        """Тест добавления ключевого слова"""
        site_id = self.tracker.add_site("example.com")
        keyword_id = self.tracker.add_keyword(site_id, "test keyword")

        self.assertIsNotNone(keyword_id)

        keywords = self.tracker.get_keywords(site_id)
        self.assertEqual(len(keywords), 1)
        self.assertEqual(keywords[0]['keyword'], "test keyword")

    @patch('requests.get')
    def test_search_google(self, mock_get):
        """Тест поиска в Google"""
        # Мокаем ответ от Google
        mock_response = Mock()
        mock_response.text = "<html>...</html>"
        mock_get.return_value = mock_response

        results = self.tracker.search_google("test keyword")
        self.assertIsInstance(results, list)
```

#### 2. Интеграционные тесты

```python
class TestIntegration(unittest.TestCase):
    def test_full_analysis_workflow(self):
        """Тест полного процесса анализа"""
        # Подготовка
        site_url = "https://example.com"

        # Выполнение
        with patch('selenium.webdriver.Chrome') as mock_driver:
            mock_driver.return_value.page_source = "<html>...</html>"

            result = run_test(site_url, Mock(), Mock(), Mock(), False, "")

            # Проверка
            self.assertIsNotNone(result)

    def test_serp_tracking_workflow(self):
        """Тест процесса отслеживания позиций"""
        # Подготовка
        keywords = ["test keyword"]
        domain = "example.com"

        # Выполнение
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = "<html>...</html>"
            mock_get.return_value = mock_response

            result = run_serp_tracking(keywords, domain)

            # Проверка
            self.assertIsNotNone(result)
```

#### 3. Тесты производительности

```python
import time
import cProfile
import pstats

class TestPerformance(unittest.TestCase):
    def test_analysis_performance(self):
        """Тест производительности анализа"""
        site_url = "https://example.com"

        # Профилирование
        profiler = cProfile.Profile()
        profiler.enable()

        # Выполнение анализа
        run_test(site_url, Mock(), Mock(), Mock(), False, "")

        profiler.disable()

        # Анализ результатов
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')

        # Проверка времени выполнения
        total_time = stats.total_tt
        self.assertLess(total_time, 30)  # Не более 30 секунд

    def test_memory_usage(self):
        """Тест использования памяти"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Выполнение операций
        for i in range(10):
            run_test(f"https://example{i}.com", Mock(), Mock(), Mock(), False, "")

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Проверка использования памяти (не более 100MB)
        self.assertLess(memory_increase, 100 * 1024 * 1024)
```

### Запуск тестов

```bash
# Запуск всех тестов
python -m unittest discover tests

# Запуск конкретного теста
python -m unittest tests.test_serp_tracker

# Запуск с покрытием
coverage run -m unittest discover tests
coverage report
coverage html
```

---

## 🚀 Развертывание

### Создание исполняемого файла

#### 1. Установка PyInstaller

```bash
pip install pyinstaller
```

#### 2. Создание spec файла

```python
# seo_analyzer.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('requirements.txt', '.'),
        ('README.md', '.')
    ],
    hiddenimports=[
        'selenium',
        'webdriver_manager',
        'flet',
        'pandas',
        'openpyxl',
        'docx'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=a.cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SEO_Analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/seo_icon.ico'
)
```

#### 3. Сборка

```bash
# Создание exe файла
pyinstaller seo_analyzer.spec

# Или простая сборка
pyinstaller --onefile --windowed --icon=assets/seo_icon.ico main.py
```

### Настройка CI/CD

#### 1. GitHub Actions

```yaml
# .github/workflows/build.yml
name: Build and Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest coverage

      - name: Run tests
        run: |
          python -m pytest tests/ --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v1
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller

      - name: Build executable
        run: |
          pyinstaller --onefile --windowed --icon=assets/seo_icon.ico main.py

      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: SEO_Analyzer
          path: dist/
```

#### 2. Автоматическое обновление

```python
# auto_updater.py
import requests
import os
import sys
from packaging import version

def check_for_updates():
    """Проверка обновлений"""
    current_version = "2.0.0"

    # Получение информации о последней версии
    response = requests.get("https://api.github.com/repos/username/seo-analyzer/releases/latest")
    latest_version = response.json()["tag_name"]

    if version.parse(latest_version) > version.parse(current_version):
        return True, latest_version

    return False, current_version

def download_update(version):
    """Загрузка обновления"""
    url = f"https://github.com/username/seo-analyzer/releases/download/{version}/SEO_Analyzer.exe"

    response = requests.get(url, stream=True)

    with open("SEO_Analyzer_new.exe", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return "SEO_Analyzer_new.exe"

def install_update():
    """Установка обновления"""
    import subprocess

    # Запуск процесса обновления
    subprocess.Popen(["updater.exe", "SEO_Analyzer_new.exe"])
    sys.exit(0)
```

---

## 🔧 Устранение неполадок

### Частые проблемы

#### 1. Ошибки WebDriver

```python
# Проблема: ChromeDriver не найден
def fix_chromedriver_issue():
    """Решение проблем с ChromeDriver"""
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    except Exception as e:
        print(f"Ошибка ChromeDriver: {e}")
        # Ручная установка
        print("Скачайте ChromeDriver с https://chromedriver.chromium.org/")
        print("Добавьте в PATH или укажите путь в коде")

# Проблема: Блокировка сайтами
def fix_blocking_issue():
    """Решение проблем с блокировкой"""
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Ротация User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    ]
    import random
    options.add_argument(f"--user-agent={random.choice(user_agents)}")
```

#### 2. Ошибки базы данных

```python
# Проблема: Блокировка БД
def fix_database_lock():
    """Решение проблем с блокировкой БД"""
    import sqlite3

    try:
        conn = sqlite3.connect("serp_tracker.db", timeout=20)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
    except sqlite3.OperationalError as e:
        print(f"Ошибка БД: {e}")
        # Создание резервной копии
        import shutil
        shutil.copy2("serp_tracker.db", "serp_tracker_backup.db")

# Проблема: Повреждение БД
def fix_corrupted_database():
    """Восстановление поврежденной БД"""
    import sqlite3

    try:
        conn = sqlite3.connect("serp_tracker.db")
        conn.execute("PRAGMA integrity_check")
    except sqlite3.DatabaseError:
        print("БД повреждена, восстанавливаем...")

        # Восстановление из резервной копии
        import shutil
        if os.path.exists("serp_tracker_backup.db"):
            shutil.copy2("serp_tracker_backup.db", "serp_tracker.db")
        else:
            # Создание новой БД
            init_database()
```

#### 3. Ошибки памяти

```python
# Проблема: Утечка памяти
def fix_memory_leak():
    """Решение проблем с памятью"""
    import gc

    # Принудительная очистка памяти
    gc.collect()

    # Закрытие неиспользуемых соединений
    if 'driver' in globals():
        driver.quit()

    # Очистка временных файлов
    import tempfile
    import os
    temp_dir = tempfile.gettempdir()
    for file in os.listdir(temp_dir):
        if file.startswith("scrapinghub"):
            os.remove(os.path.join(temp_dir, file))
```

### Логирование ошибок

```python
import logging
import traceback
from datetime import datetime

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('seo_log.txt'),
            logging.StreamHandler()
        ]
    )

def log_error(error, context=""):
    """Логирование ошибок"""
    logger = logging.getLogger(__name__)

    error_info = {
        'timestamp': datetime.now().isoformat(),
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc(),
        'context': context
    }

    logger.error(f"Ошибка: {error_info}")

    # Сохранение в файл для анализа
    with open('error_log.json', 'a') as f:
        json.dump(error_info, f)
        f.write('\n')
```

---

## 🚀 Рекомендации по улучшению

### 1. Производительность

#### Оптимизация WebDriver

```python
def optimize_webdriver():
    """Оптимизация настроек WebDriver"""
    options = ChromeOptions()

    # Отключение ненужных функций
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")

    # Отключение изображений для ускорения
    prefs = {
        "profile.default_content_setting_values.images": 2,
        "profile.managed_default_content_settings.images": 2
    }
    options.add_experimental_option("prefs", prefs)

    return options
```

#### Кэширование результатов

```python
import hashlib
import pickle
import os

class CacheManager:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get_cache_key(self, url, analysis_type):
        """Генерация ключа кэша"""
        content = f"{url}_{analysis_type}"
        return hashlib.md5(content.encode()).hexdigest()

    def get_cached_result(self, url, analysis_type):
        """Получение результата из кэша"""
        cache_key = self.get_cache_key(url, analysis_type)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        if os.path.exists(cache_file):
            # Проверка актуальности (24 часа)
            if time.time() - os.path.getmtime(cache_file) < 86400:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)

        return None

    def save_to_cache(self, url, analysis_type, result):
        """Сохранение результата в кэш"""
        cache_key = self.get_cache_key(url, analysis_type)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)
```

### 2. Масштабируемость

#### Многопоточность

```python
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def analyze_multiple_sites(sites_list, max_workers=5):
    """Анализ нескольких сайтов параллельно"""
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Создание задач
        future_to_site = {
            executor.submit(analyze_single_site, site): site
            for site in sites_list
        }

        # Обработка результатов
        for future in as_completed(future_to_site):
            site = future_to_site[future]
            try:
                result = future.result()
                results[site] = result
            except Exception as e:
                results[site] = {'error': str(e)}

    return results

def analyze_single_site(site_url):
    """Анализ одного сайта"""
    # Логика анализа
    return {'url': site_url, 'status': 'completed'}
```

#### Очереди задач

```python
import queue
import threading
import time

class TaskQueue:
    def __init__(self, max_workers=3):
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.workers = []
        self.max_workers = max_workers
        self.running = True

        # Запуск воркеров
        for _ in range(max_workers):
            worker = threading.Thread(target=self._worker)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

    def _worker(self):
        """Воркер для обработки задач"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                result = self._process_task(task)
                self.result_queue.put(result)
                self.task_queue.task_done()
            except queue.Empty:
                continue

    def _process_task(self, task):
        """Обработка задачи"""
        task_type = task.get('type')

        if task_type == 'seo_analysis':
            return self._analyze_seo(task['url'])
        elif task_type == 'serp_tracking':
            return self._track_serp(task['keyword'], task['domain'])
        else:
            return {'error': 'Unknown task type'}

    def add_task(self, task):
        """Добавление задачи в очередь"""
        self.task_queue.put(task)

    def get_result(self, timeout=None):
        """Получение результата"""
        return self.result_queue.get(timeout=timeout)

    def stop(self):
        """Остановка очереди"""
        self.running = False
        for worker in self.workers:
            worker.join()
```

### 3. Безопасность

#### Валидация входных данных

```python
import re
from urllib.parse import urlparse

def validate_url(url):
    """Валидация URL"""
    if not url:
        return False, "URL не может быть пустым"

    # Проверка формата
    if not re.match(r'^https?://', url):
        return False, "URL должен начинаться с http:// или https://"

    # Парсинг URL
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return False, "Некорректный домен"
    except Exception:
        return False, "Некорректный формат URL"

    # Проверка длины
    if len(url) > 2048:
        return False, "URL слишком длинный"

    return True, "URL корректен"

def sanitize_input(text):
    """Очистка входных данных"""
    if not text:
        return ""

    # Удаление опасных символов
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        text = text.replace(char, '')

    # Ограничение длины
    if len(text) > 1000:
        text = text[:1000]

    return text.strip()
```

#### Защита от атак

```python
import hashlib
import secrets

class SecurityManager:
    def __init__(self):
        self.salt = secrets.token_hex(16)

    def hash_sensitive_data(self, data):
        """Хеширование чувствительных данных"""
        if not data:
            return None

        # Создание хеша с солью
        salted_data = data + self.salt
        return hashlib.sha256(salted_data.encode()).hexdigest()

    def validate_api_key(self, api_key):
        """Валидация API ключа"""
        if not api_key:
            return False

        # Проверка формата
        if not re.match(r'^[A-Za-z0-9]{32,}$', api_key):
            return False

        return True

    def rate_limit(self, ip_address, action, limit=100):
        """Ограничение частоты запросов"""
        import time

        current_time = time.time()
        key = f"{ip_address}_{action}"

        # Проверка лимита (упрощенная реализация)
        # В реальном проекте используйте Redis или подобное
        return True
```

### 4. Мониторинг

#### Система мониторинга

```python
import psutil
import time
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.metrics = []

    def collect_metrics(self):
        """Сбор метрик системы"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict()
        }

        self.metrics.append(metrics)

        # Ограничение размера истории
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]

        return metrics

    def get_alerts(self):
        """Получение предупреждений"""
        alerts = []

        if len(self.metrics) == 0:
            return alerts

        latest = self.metrics[-1]

        if latest['cpu_percent'] > 80:
            alerts.append("Высокое использование CPU")

        if latest['memory_percent'] > 85:
            alerts.append("Высокое использование памяти")

        if latest['disk_usage'] > 90:
            alerts.append("Мало места на диске")

        return alerts

    def generate_report(self):
        """Генерация отчета о производительности"""
        if len(self.metrics) == 0:
            return "Нет данных для отчета"

        avg_cpu = sum(m['cpu_percent'] for m in self.metrics) / len(self.metrics)
        avg_memory = sum(m['memory_percent'] for m in self.metrics) / len(self.metrics)

        return {
            'period': f"{self.metrics[0]['timestamp']} - {self.metrics[-1]['timestamp']}",
            'avg_cpu': round(avg_cpu, 2),
            'avg_memory': round(avg_memory, 2),
            'total_metrics': len(self.metrics)
        }
```

### 5. Автоматизация

#### Планировщик задач

```python
import schedule
import time
import threading

class TaskScheduler:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        """Запуск планировщика"""
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Остановка планировщика"""
        self.running = False
        if self.thread:
            self.thread.join()

    def _run_scheduler(self):
        """Запуск планировщика в отдельном потоке"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def schedule_daily_analysis(self, sites_list, time="09:00"):
        """Планирование ежедневного анализа"""
        schedule.every().day.at(time).do(self._run_daily_analysis, sites_list)

    def schedule_serp_tracking(self, keywords_list, domain, time="10:00"):
        """Планирование отслеживания позиций"""
        schedule.every().day.at(time).do(self._run_serp_tracking, keywords_list, domain)

    def _run_daily_analysis(self, sites_list):
        """Выполнение ежедневного анализа"""
        print(f"Запуск ежедневного анализа для {len(sites_list)} сайтов")
        # Логика анализа

    def _run_serp_tracking(self, keywords_list, domain):
        """Выполнение отслеживания позиций"""
        print(f"Запуск отслеживания позиций для домена {domain}")
        # Логика трекинга
```

---

## 📚 Дополнительные ресурсы

### Полезные ссылки

- [Документация Selenium](https://selenium-python.readthedocs.io/)
- [Документация Flet](https://flet.dev/docs/)
- [Документация Pandas](https://pandas.pydata.org/docs/)
- [Документация SQLite](https://www.sqlite.org/docs.html)

### Рекомендуемые инструменты

- **PyCharm** - IDE для Python разработки
- **Postman** - тестирование API
- **SQLite Browser** - просмотр базы данных
- **Chrome DevTools** - отладка веб-скрапинга

### Стандарты кодирования

- **PEP 8** - стиль кода Python
- **PEP 257** - документация
- **Type Hints** - типизация кода

---

## 🤝 Поддержка

### Контакты для разработчиков

- **Email**: developer@seo-analyzer.com
- **GitHub Issues**: https://github.com/username/seo-analyzer/issues
- **Discord**: https://discord.gg/seo-analyzer

### Процесс внесения изменений

1. Создайте issue с описанием проблемы/улучшения
2. Форкните репозиторий
3. Создайте feature branch
4. Внесите изменения с тестами
5. Создайте Pull Request
6. Дождитесь code review
7. После одобрения изменения будут слиты

---

**Удачной разработки! 🚀**
