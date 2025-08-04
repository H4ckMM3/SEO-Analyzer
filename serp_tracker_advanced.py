import os
import sys
import re
import json
import time
import threading
import requests
import flet as ft
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import urllib3
import logging
from io import BytesIO
import base64
import sqlite3
from urllib.parse import quote_plus, urlparse
import random
import schedule
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Подавление логов
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Константы
DATABASE_FILE = "serp_tracker_advanced.db"
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

class AdvancedSERPTracker:
    def __init__(self):
        self.db_init()
        self.proxies = []
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0"
        ]
        self.scheduled_tasks = {}
    
    def db_init(self):
        """Инициализация расширенной базы данных"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Таблица для отслеживания позиций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_url TEXT NOT NULL,
                keyword TEXT NOT NULL,
                search_engine TEXT NOT NULL,
                position INTEGER,
                url_found TEXT,
                title_found TEXT,
                snippet_found TEXT,
                date_checked DATETIME DEFAULT CURRENT_TIMESTAMP,
                response_time REAL,
                proxy_used TEXT,
                user_agent TEXT,
                ip_address TEXT
            )
        ''')
        
        # Таблица для проектов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                site_url TEXT NOT NULL,
                keywords TEXT NOT NULL,
                search_engines TEXT NOT NULL,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_checked DATETIME,
                status TEXT DEFAULT 'active',
                check_frequency TEXT DEFAULT 'daily',
                email_notifications BOOLEAN DEFAULT 0,
                email_address TEXT,
                position_threshold INTEGER DEFAULT 10
            )
        ''')
        
        # Таблица для конкурентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                competitor_url TEXT NOT NULL,
                competitor_name TEXT,
                added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Таблица для уведомлений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                keyword TEXT NOT NULL,
                search_engine TEXT NOT NULL,
                old_position INTEGER,
                new_position INTEGER,
                change_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                notification_sent BOOLEAN DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Таблица для настроек
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_webdriver(self, use_proxy=False, proxy=None, headless=True):
        """Создает WebDriver с расширенными настройками"""
        options = ChromeOptions()
        
        if headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Ускоряет загрузку
        options.add_argument("--disable-javascript")  # Для некоторых проверок
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2
        })
        
        # Случайный User-Agent
        user_agent = random.choice(self.user_agents)
        options.add_argument(f'--user-agent={user_agent}')
        
        if use_proxy and proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            return driver, user_agent
        except Exception as e:
            print(f"Ошибка создания WebDriver: {e}")
            return None, None
    
    def search_google_advanced(self, keyword, target_url, proxy=None):
        """Расширенный поиск в Google с дополнительной информацией"""
        try:
            driver, user_agent = self.create_webdriver(use_proxy=bool(proxy), proxy=proxy)
            if not driver:
                return None, None, None, None, None
            
            start_time = time.time()
            
            # Формируем URL поиска
            search_url = f"https://www.google.com/search?q={quote_plus(keyword)}&num=100"
            driver.get(search_url)
            
            # Ждем загрузки результатов
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
            )
            
            response_time = time.time() - start_time
            
            # Ищем результаты
            results = driver.find_elements(By.CSS_SELECTOR, "div.g")
            position = None
            url_found = None
            title_found = None
            snippet_found = None
            
            for i, result in enumerate(results[:100], 1):
                try:
                    link = result.find_element(By.CSS_SELECTOR, "a")
                    url = link.get_attribute("href")
                    
                    if url and target_url in url:
                        position = i
                        url_found = url
                        
                        # Получаем заголовок
                        try:
                            title_elem = result.find_element(By.CSS_SELECTOR, "h3")
                            title_found = title_elem.text
                        except:
                            title_found = "Заголовок не найден"
                        
                        # Получаем сниппет
                        try:
                            snippet_elem = result.find_element(By.CSS_SELECTOR, "div.VwiC3b")
                            snippet_found = snippet_elem.text
                        except:
                            snippet_found = "Сниппет не найден"
                        
                        break
                except:
                    continue
            
            driver.quit()
            return position, url_found, title_found, snippet_found, response_time
            
        except Exception as e:
            print(f"Ошибка поиска в Google: {e}")
            if 'driver' in locals():
                driver.quit()
            return None, None, None, None, None
    
    def search_yandex_advanced(self, keyword, target_url, proxy=None):
        """Расширенный поиск в Яндекс с дополнительной информацией"""
        try:
            driver, user_agent = self.create_webdriver(use_proxy=bool(proxy), proxy=proxy)
            if not driver:
                return None, None, None, None, None
            
            start_time = time.time()
            
            # Формируем URL поиска
            search_url = f"https://yandex.ru/search/?text={quote_plus(keyword)}&numdoc=100"
            driver.get(search_url)
            
            # Ждем загрузки результатов
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".serp-item"))
            )
            
            response_time = time.time() - start_time
            
            # Ищем результаты
            results = driver.find_elements(By.CSS_SELECTOR, ".serp-item")
            position = None
            url_found = None
            title_found = None
            snippet_found = None
            
            for i, result in enumerate(results[:100], 1):
                try:
                    link = result.find_element(By.CSS_SELECTOR, "a.link")
                    url = link.get_attribute("href")
                    
                    if url and target_url in url:
                        position = i
                        url_found = url
                        
                        # Получаем заголовок
                        try:
                            title_elem = result.find_element(By.CSS_SELECTOR, ".organic__url-text")
                            title_found = title_elem.text
                        except:
                            title_found = "Заголовок не найден"
                        
                        # Получаем сниппет
                        try:
                            snippet_elem = result.find_element(By.CSS_SELECTOR, ".organic__content-wrapper")
                            snippet_found = snippet_elem.text
                        except:
                            snippet_found = "Сниппет не найден"
                        
                        break
                except:
                    continue
            
            driver.quit()
            return position, url_found, title_found, snippet_found, response_time
            
        except Exception as e:
            print(f"Ошибка поиска в Яндекс: {e}")
            if 'driver' in locals():
                driver.quit()
            return None, None, None, None, None
    
    def check_position_advanced(self, site_url, keyword, search_engine, proxy=None):
        """Расширенная проверка позиции"""
        if search_engine.lower() == 'google':
            position, url_found, title_found, snippet_found, response_time = self.search_google_advanced(keyword, site_url, proxy)
        elif search_engine.lower() == 'yandex':
            position, url_found, title_found, snippet_found, response_time = self.search_yandex_advanced(keyword, site_url, proxy)
        else:
            return None
        
        # Получаем IP адрес (если используется прокси)
        ip_address = None
        if proxy:
            try:
                response = requests.get('https://api.ipify.org?format=json', proxies={'http': proxy, 'https': proxy})
                ip_address = response.json()['ip']
            except:
                pass
        
        # Сохраняем результат в БД
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO positions (site_url, keyword, search_engine, position, url_found, title_found, snippet_found, response_time, proxy_used, user_agent, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (site_url, keyword, search_engine, position, url_found, title_found, snippet_found, response_time, proxy, user_agent, ip_address))
        conn.commit()
        conn.close()
        
        return {
            'position': position,
            'url_found': url_found,
            'title_found': title_found,
            'snippet_found': snippet_found,
            'response_time': response_time,
            'proxy': proxy,
            'user_agent': user_agent,
            'ip_address': ip_address
        }
    
    def add_project_advanced(self, name, site_url, keywords, search_engines, check_frequency='daily', email_notifications=False, email_address=None, position_threshold=10):
        """Добавляет новый проект с расширенными настройками"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, site_url, keywords, search_engines, check_frequency, email_notifications, email_address, position_threshold)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, site_url, keywords, search_engines, check_frequency, email_notifications, email_address, position_threshold))
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return project_id
    
    def add_competitor(self, project_id, competitor_url, competitor_name=None):
        """Добавляет конкурента для отслеживания"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO competitors (project_id, competitor_url, competitor_name)
            VALUES (?, ?, ?)
        ''', (project_id, competitor_url, competitor_name or competitor_url))
        conn.commit()
        conn.close()
    
    def get_competitors(self, project_id):
        """Получает список конкурентов проекта"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM competitors WHERE project_id = ?', (project_id,))
        competitors = cursor.fetchall()
        conn.close()
        return competitors
    
    def check_competitor_positions(self, project_id, keyword, search_engine):
        """Проверяет позиции конкурентов"""
        competitors = self.get_competitors(project_id)
        results = []
        
        for competitor in competitors:
            competitor_url = competitor[2]
            competitor_name = competitor[3]
            
            if search_engine.lower() == 'google':
                position, url_found, title_found, snippet_found, response_time = self.search_google_advanced(keyword, competitor_url)
            elif search_engine.lower() == 'yandex':
                position, url_found, title_found, snippet_found, response_time = self.search_yandex_advanced(keyword, competitor_url)
            else:
                continue
            
            results.append({
                'competitor_name': competitor_name,
                'competitor_url': competitor_url,
                'position': position,
                'url_found': url_found,
                'title_found': title_found,
                'snippet_found': snippet_found,
                'response_time': response_time
            })
        
        return results
    
    def schedule_tracking(self, project_id, frequency='daily'):
        """Планирует автоматическое отслеживание"""
        def tracking_job():
            try:
                # Получаем данные проекта
                conn = sqlite3.connect(DATABASE_FILE)
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
                project = cursor.fetchone()
                conn.close()
                
                if project:
                    site_url = project[2]
                    keywords = project[3]
                    search_engines = project[4]
                    
                    # Запускаем отслеживание
                    results = self.run_tracking_advanced(site_url, keywords, search_engines)
                    
                    # Проверяем изменения позиций
                    self.check_position_changes(project_id, results)
                    
                    # Обновляем время последней проверки
                    conn = sqlite3.connect(DATABASE_FILE)
                    cursor = conn.cursor()
                    cursor.execute('UPDATE projects SET last_checked = CURRENT_TIMESTAMP WHERE id = ?', (project_id,))
                    conn.commit()
                    conn.close()
                    
            except Exception as e:
                print(f"Ошибка в запланированном задании для проекта {project_id}: {e}")
        
        # Настраиваем расписание
        if frequency == 'hourly':
            schedule.every().hour.do(tracking_job)
        elif frequency == 'daily':
            schedule.every().day.at("09:00").do(tracking_job)
        elif frequency == 'weekly':
            schedule.every().monday.at("09:00").do(tracking_job)
        
        # Сохраняем задание
        self.scheduled_tasks[project_id] = {
            'job': tracking_job,
            'frequency': frequency
        }
    
    def check_position_changes(self, project_id, results):
        """Проверяет изменения позиций и отправляет уведомления"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        for result in results:
            keyword = result['keyword']
            engine = result['engine']
            new_position = result['result']['position'] if result['result'] else None
            
            # Получаем предыдущую позицию
            cursor.execute('''
                SELECT position FROM positions 
                WHERE site_url = (SELECT site_url FROM projects WHERE id = ?)
                AND keyword = ? AND search_engine = ?
                ORDER BY date_checked DESC LIMIT 1 OFFSET 1
            ''', (project_id, keyword, engine))
            
            prev_result = cursor.fetchone()
            old_position = prev_result[0] if prev_result else None
            
            if old_position != new_position:
                # Сохраняем изменение
                cursor.execute('''
                    INSERT INTO notifications (project_id, keyword, search_engine, old_position, new_position)
                    VALUES (?, ?, ?, ?, ?)
                ''', (project_id, keyword, engine, old_position, new_position))
                
                # Проверяем, нужно ли отправить уведомление
                cursor.execute('''
                    SELECT email_notifications, email_address, position_threshold 
                    FROM projects WHERE id = ?
                ''', (project_id,))
                
                project_settings = cursor.fetchone()
                if project_settings and project_settings[0] and project_settings[1]:
                    email_address = project_settings[1]
                    threshold = project_settings[2]
                    
                    # Отправляем уведомление если позиция ухудшилась или улучшилась значительно
                    if (new_position and new_position > threshold) or (old_position and new_position and new_position < old_position - 5):
                        self.send_email_notification(email_address, keyword, engine, old_position, new_position)
        
        conn.commit()
        conn.close()
    
    def send_email_notification(self, email_address, keyword, engine, old_position, new_position):
        """Отправляет email уведомление"""
        try:
            # Настройки SMTP (замените на свои)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "your-email@gmail.com"  # Замените на свой email
            sender_password = "your-app-password"  # Замените на свой пароль приложения
            
            # Создаем сообщение
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email_address
            msg['Subject'] = f"Изменение позиции: {keyword}"
            
            # Формируем текст сообщения
            if old_position and new_position:
                if new_position < old_position:
                    change_text = f"улучшилась с {old_position} на {new_position}"
                else:
                    change_text = f"ухудшилась с {old_position} на {new_position}"
            else:
                change_text = f"теперь {new_position if new_position else 'не найдено'}"
            
            body = f"""
            Изменение позиции в поисковой системе {engine}
            
            Ключевое слово: {keyword}
            Изменение: {change_text}
            
            Проверьте детали в панели управления SERP Tracker.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Отправляем email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, email_address, text)
            server.quit()
            
            print(f"Уведомление отправлено на {email_address}")
            
        except Exception as e:
            print(f"Ошибка отправки email: {e}")
    
    def run_tracking_advanced(self, site_url, keywords, search_engines, progress_callback=None, stop_event=None):
        """Расширенное отслеживание позиций"""
        keywords_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        engines_list = [eng.strip() for eng in search_engines.split(',') if eng.strip()]
        
        total_checks = len(keywords_list) * len(engines_list)
        current_check = 0
        results = []
        
        for keyword in keywords_list:
            if stop_event and stop_event.is_set():
                break
                
            for engine in engines_list:
                if stop_event and stop_event.is_set():
                    break
                
                # Выбираем случайный прокси если есть
                proxy = random.choice(self.proxies) if self.proxies else None
                
                result = self.check_position_advanced(site_url, keyword, engine, proxy)
                results.append({
                    'keyword': keyword,
                    'engine': engine,
                    'result': result
                })
                
                current_check += 1
                if progress_callback:
                    progress_callback(current_check, total_checks, f"Проверяем '{keyword}' в {engine}")
                
                # Пауза между запросами
                time.sleep(random.uniform(2, 5))
        
        return results
    
    def generate_advanced_report(self, project_id, days=30):
        """Генерирует расширенный отчет"""
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Получаем данные проекта
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        project = cursor.fetchone()
        
        if not project:
            conn.close()
            return None
        
        site_url = project[2]
        keywords = project[3]
        search_engines = project[4]
        
        # Получаем историю позиций
        keywords_list = [kw.strip() for kw in keywords.split(',') if kw.strip()]
        engines_list = [eng.strip() for eng in search_engines.split(',') if eng.strip()]
        
        report_data = []
        
        for keyword in keywords_list:
            for engine in engines_list:
                cursor.execute('''
                    SELECT position, date_checked, response_time, title_found, snippet_found
                    FROM positions
                    WHERE site_url = ? AND keyword = ? AND search_engine = ?
                    AND date_checked >= datetime('now', '-{} days')
                    ORDER BY date_checked
                '''.format(days), (site_url, keyword, engine))
                
                history = cursor.fetchall()
                
                if history:
                    latest = history[-1]
                    best_position = min([h[0] for h in history if h[0] is not None], default=None)
                    avg_position = sum([h[0] for h in history if h[0] is not None]) / len([h[0] for h in history if h[0] is not None]) if any(h[0] for h in history) else None
                    
                    report_data.append({
                        'Ключевое слово': keyword,
                        'Поисковая система': engine,
                        'Текущая позиция': latest[0] if latest[0] else 'Не найдено',
                        'Лучшая позиция': best_position,
                        'Средняя позиция': round(avg_position, 1) if avg_position else None,
                        'Последняя проверка': latest[1],
                        'Время ответа': f"{latest[2]:.2f}s" if latest[2] else '',
                        'Заголовок': latest[3] or '',
                        'Сниппет': latest[4] or ''
                    })
        
        conn.close()
        
        # Создаем Excel файл
        if report_data:
            df = pd.DataFrame(report_data)
            filename = f"{REPORT_DIR}/advanced_serp_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Позиции', index=False)
                
                # Добавляем графики
                workbook = writer.book
                worksheet = writer.sheets['Позиции']
                
                # Создаем график позиций
                chart_data = []
                for keyword in keywords_list[:3]:  # Первые 3 ключевых слова
                    for engine in engines_list:
                        conn = sqlite3.connect(DATABASE_FILE)
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT position, date_checked
                            FROM positions
                            WHERE site_url = ? AND keyword = ? AND search_engine = ?
                            AND date_checked >= datetime('now', '-{} days')
                            ORDER BY date_checked
                        '''.format(days), (site_url, keyword, engine))
                        
                        history = cursor.fetchall()
                        conn.close()
                        
                        if history:
                            dates = [datetime.strptime(h[1], '%Y-%m-%d %H:%M:%S') for h in history]
                            positions = [h[0] if h[0] else 100 for h in history]
                            
                            chart_data.append({
                                'keyword': keyword,
                                'engine': engine,
                                'dates': dates,
                                'positions': positions
                            })
            
            return filename
        
        return None

def main(page: ft.Page):
    """Главная функция расширенного SERP Tracker"""
    page.title = "Advanced SERP Tracker"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1400
    page.window_height = 900
    
    # Инициализация трекера
    tracker = AdvancedSERPTracker()
    
    # Переменные состояния
    current_project = None
    stop_event = threading.Event()
    
    # UI элементы
    project_name_input = ft.TextField(
        label="Название проекта",
        hint_text="Мой сайт - цветы",
        width=400,
        border_color=ft.Colors.PURPLE_300
    )
    
    site_url_input = ft.TextField(
        label="URL сайта",
        hint_text="https://example.com",
        width=400,
        border_color=ft.Colors.BLUE_400
    )
    
    keywords_input = ft.TextField(
        label="Ключевые слова",
        hint_text="купить цветы, доставка цветов, цветы москва",
        width=400,
        border_color=ft.Colors.GREEN_400,
        multiline=True,
        min_lines=3,
        max_lines=5
    )
    
    search_engines_input = ft.TextField(
        label="Поисковые системы",
        hint_text="google, yandex",
        value="google, yandex",
        width=400,
        border_color=ft.Colors.ORANGE_400
    )
    
    check_frequency_dropdown = ft.Dropdown(
        label="Частота проверки",
        width=200,
        options=[
            ft.dropdown.Option("hourly", "Каждый час"),
            ft.dropdown.Option("daily", "Ежедневно"),
            ft.dropdown.Option("weekly", "Еженедельно")
        ],
        value="daily"
    )
    
    email_notifications_checkbox = ft.Checkbox(
        label="Email уведомления",
        value=False
    )
    
    email_input = ft.TextField(
        label="Email для уведомлений",
        hint_text="your@email.com",
        width=400,
        border_color=ft.Colors.CYAN_300,
        visible=False
    )
    
    position_threshold_input = ft.TextField(
        label="Порог позиции для уведомлений",
        hint_text="10",
        value="10",
        width=200,
        border_color=ft.Colors.RED_400
    )
    
    competitor_url_input = ft.TextField(
        label="URL конкурента",
        hint_text="https://competitor.com",
        width=400,
        border_color=ft.Colors.YELLOW_300
    )
    
    competitor_name_input = ft.TextField(
        label="Название конкурента",
        hint_text="Конкурент 1",
        width=400,
        border_color=ft.Colors.YELLOW_300
    )
    
    progress_bar = ft.ProgressBar(width=400, visible=False)
    progress_text = ft.Text("", size=12, color=ft.Colors.GREY_500)
    
    results_area = ft.TextField(
        label="Результаты отслеживания",
        multiline=True,
        min_lines=15,
        max_lines=25,
        read_only=True,
        border_color=ft.Colors.BLUE_200
    )
    
    def update_progress(current, total, message):
        """Обновляет прогресс"""
        if total > 0:
            progress_bar.value = current / total
        progress_text.value = message
        page.update()
    
    def start_tracking(e):
        """Запускает отслеживание позиций"""
        site_url = site_url_input.value.strip()
        keywords = keywords_input.value.strip()
        search_engines = search_engines_input.value.strip()
        
        if not all([site_url, keywords, search_engines]):
            results_area.value = "❌ Заполните все обязательные поля!"
            page.update()
            return
        
        # Показываем прогресс
        progress_bar.visible = True
        progress_text.value = "Начинаем отслеживание..."
        page.update()
        
        # Сбрасываем событие остановки
        stop_event.clear()
        
        def tracking_worker():
            try:
                results = tracker.run_tracking_advanced(
                    site_url, keywords, search_engines, 
                    update_progress, stop_event
                )
                
                # Формируем расширенный отчет
                report = "📊 РЕЗУЛЬТАТЫ РАСШИРЕННОГО ОТСЛЕЖИВАНИЯ\n"
                report += "=" * 60 + "\n\n"
                
                for result in results:
                    keyword = result['keyword']
                    engine = result['engine']
                    data = result['result']
                    
                    if data and data['position']:
                        report += f"✅ '{keyword}' в {engine}: позиция {data['position']}\n"
                        if data['url_found']:
                            report += f"   URL: {data['url_found']}\n"
                        if data['title_found']:
                            report += f"   Заголовок: {data['title_found']}\n"
                        if data['snippet_found']:
                            report += f"   Сниппет: {data['snippet_found'][:100]}...\n"
                        report += f"   Время ответа: {data['response_time']:.2f}s\n"
                        if data['proxy']:
                            report += f"   Прокси: {data['proxy']}\n"
                        if data['ip_address']:
                            report += f"   IP: {data['ip_address']}\n"
                    else:
                        report += f"❌ '{keyword}' в {engine}: не найдено в топ-100\n"
                    report += "\n"
                
                # Обновляем UI
                results_area.value = report
                progress_bar.visible = False
                progress_text.value = "Отслеживание завершено"
                page.update()
                
            except Exception as e:
                results_area.value = f"❌ Ошибка: {str(e)}"
                progress_bar.visible = False
                progress_text.value = "Ошибка при отслеживании"
                page.update()
        
        # Запускаем в отдельном потоке
        threading.Thread(target=tracking_worker, daemon=True).start()
    
    def stop_tracking(e):
        """Останавливает отслеживание"""
        stop_event.set()
        progress_text.value = "Остановка отслеживания..."
        page.update()
    
    def save_project(e):
        """Сохраняет проект с расширенными настройками"""
        name = project_name_input.value.strip()
        site_url = site_url_input.value.strip()
        keywords = keywords_input.value.strip()
        search_engines = search_engines_input.value.strip()
        frequency = check_frequency_dropdown.value
        email_notifications = email_notifications_checkbox.value
        email_address = email_input.value.strip() if email_notifications else None
        position_threshold = int(position_threshold_input.value) if position_threshold_input.value.isdigit() else 10
        
        if not all([name, site_url, keywords, search_engines]):
            results_area.value = "❌ Заполните все обязательные поля!"
            page.update()
            return
        
        try:
            project_id = tracker.add_project_advanced(
                name, site_url, keywords, search_engines, 
                frequency, email_notifications, email_address, position_threshold
            )
            
            # Настраиваем автоматическое отслеживание
            if frequency != 'manual':
                tracker.schedule_tracking(project_id, frequency)
            
            results_area.value = f"✅ Проект '{name}' сохранен с ID: {project_id}\nАвтоматическое отслеживание настроено: {frequency}"
            page.update()
            
        except Exception as e:
            results_area.value = f"❌ Ошибка сохранения проекта: {str(e)}"
            page.update()
    
    def add_competitor(e):
        """Добавляет конкурента"""
        if not current_project:
            results_area.value = "❌ Сначала создайте или выберите проект!"
            page.update()
            return
        
        competitor_url = competitor_url_input.value.strip()
        competitor_name = competitor_name_input.value.strip()
        
        if not competitor_url:
            results_area.value = "❌ Введите URL конкурента!"
            page.update()
            return
        
        try:
            tracker.add_competitor(current_project, competitor_url, competitor_name)
            results_area.value = f"✅ Конкурент '{competitor_name or competitor_url}' добавлен"
            page.update()
        except Exception as e:
            results_area.value = f"❌ Ошибка добавления конкурента: {str(e)}"
            page.update()
    
    def generate_report(e):
        """Генерирует расширенный отчет"""
        if not current_project:
            results_area.value = "❌ Сначала создайте или выберите проект!"
            page.update()
            return
        
        try:
            filename = tracker.generate_advanced_report(current_project)
            if filename:
                results_area.value = f"✅ Расширенный отчет создан: {filename}"
            else:
                results_area.value = "❌ Нет данных для отчета"
            page.update()
        except Exception as e:
            results_area.value = f"❌ Ошибка создания отчета: {str(e)}"
            page.update()
    
    def toggle_email_input(e):
        """Показывает/скрывает поле email"""
        email_input.visible = email_notifications_checkbox.value
        page.update()
    
    # Привязываем обработчик
    email_notifications_checkbox.on_change = toggle_email_input
    
    # Кнопки
    start_btn = ft.ElevatedButton(
        "🚀 Начать отслеживание",
        on_click=start_tracking,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN_600,
            padding=20
        )
    )
    
    stop_btn = ft.ElevatedButton(
        "⏹ Остановить",
        on_click=stop_tracking,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_600,
            padding=20
        )
    )
    
    save_btn = ft.ElevatedButton(
        "💾 Сохранить проект",
        on_click=save_project,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_600,
            padding=20
        )
    )
    
    add_competitor_btn = ft.ElevatedButton(
        "👥 Добавить конкурента",
        on_click=add_competitor,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.YELLOW_600,
            padding=20
        )
    )
    
    report_btn = ft.ElevatedButton(
        "📊 Создать отчет",
        on_click=generate_report,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.PURPLE_600,
            padding=20
        )
    )
    
    # Создаем интерфейс
    page.add(
        ft.Container(
            content=ft.Column([
                # Заголовок
                ft.Container(
                    content=ft.Text(
                        "🔍 Advanced SERP Tracker - Расширенное отслеживание позиций",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    ),
                    alignment=ft.alignment.center,
                    padding=20
                ),
                
                # Основная форма
                ft.Container(
                    content=ft.Column([
                        ft.Text("📋 Настройки проекта", size=18, weight=ft.FontWeight.BOLD),
                        project_name_input,
                        site_url_input,
                        keywords_input,
                        search_engines_input,
                        
                        ft.Row([
                            check_frequency_dropdown,
                            position_threshold_input
                        ], alignment=ft.MainAxisAlignment.START),
                        
                        ft.Row([
                            email_notifications_checkbox,
                            email_input
                        ], alignment=ft.MainAxisAlignment.START),
                        
                        ft.Row([
                            start_btn,
                            stop_btn,
                            save_btn
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        
                        progress_bar,
                        progress_text
                    ], spacing=15),
                    padding=20,
                    border=ft.border.all(1, ft.Colors.GREY_500),
                    border_radius=10,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Конкуренты
                ft.Container(
                    content=ft.Column([
                        ft.Text("👥 Управление конкурентами", size=18, weight=ft.FontWeight.BOLD),
                        competitor_url_input,
                        competitor_name_input,
                        ft.Row([
                            add_competitor_btn,
                            report_btn
                        ], alignment=ft.MainAxisAlignment.CENTER)
                    ], spacing=15),
                    padding=20,
                    border=ft.border.all(1, ft.Colors.GREY_500),
                    border_radius=10,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Результаты
                ft.Container(
                    content=ft.Column([
                        ft.Text("📊 Результаты", size=18, weight=ft.FontWeight.BOLD),
                        results_area
                    ], spacing=15),
                    padding=20,
                    border=ft.border.all(1, ft.Colors.GREY_500),
                    border_radius=10
                )
            ]),
            padding=20
        )
    )

if __name__ == "__main__":
    ft.app(target=main) 