import os
import sys
import re
import json
import time
import sqlite3
import requests
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urlparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import urllib3
import logging

# Подавление логов
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SERPTracker:
    def __init__(self, db_path="serp_tracker.db"):
        """Инициализация трекера позиций."""
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Инициализация базы данных."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица для отслеживаемых сайтов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для ключевых слов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER,
                keyword TEXT NOT NULL,
                search_engine TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (site_id) REFERENCES sites (id),
                UNIQUE(site_id, keyword, search_engine)
            )
        ''')
        
        # Таблица для результатов проверок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword_id INTEGER,
                position INTEGER,
                url TEXT,
                title TEXT,
                snippet TEXT,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (keyword_id) REFERENCES keywords (id)
            )
        ''')
        
        # Обновляем структуру существующей таблицы positions
        self._update_positions_table(cursor)
        
        conn.commit()
        conn.close()
    
    def _update_positions_table(self, cursor):
        """Обновляет структуру таблицы positions, добавляя недостающие колонки."""
        try:
            # Проверяем существующие колонки
            cursor.execute("PRAGMA table_info(positions)")
            columns = [column[1] for column in cursor.fetchall()]
            
            print(f"📋 Текущие колонки в таблице positions: {columns}")
            
            # Добавляем колонки, если их нет
            if 'url' not in columns:
                cursor.execute("ALTER TABLE positions ADD COLUMN url TEXT")
                print("✅ Добавлена колонка 'url' в таблицу positions")
            
            if 'title' not in columns:
                cursor.execute("ALTER TABLE positions ADD COLUMN title TEXT")
                print("✅ Добавлена колонка 'title' в таблицу positions")
            
            if 'snippet' not in columns:
                cursor.execute("ALTER TABLE positions ADD COLUMN snippet TEXT")
                print("✅ Добавлена колонка 'snippet' в таблицу positions")
            
            if 'checked_at' not in columns:
                cursor.execute("ALTER TABLE positions ADD COLUMN checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                print("✅ Добавлена колонка 'checked_at' в таблицу positions")
                
        except Exception as e:
            print(f"❌ Ошибка обновления таблицы positions: {e}")
            # Если не удалось обновить, создаем таблицу заново
            try:
                cursor.execute("DROP TABLE IF EXISTS positions")
                cursor.execute('''
                    CREATE TABLE positions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        keyword_id INTEGER,
                        position INTEGER,
                        url TEXT,
                        title TEXT,
                        snippet TEXT,
                        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (keyword_id) REFERENCES keywords (id)
                    )
                ''')
                print("✅ Таблица positions пересоздана с правильной структурой")
            except Exception as e2:
                print(f"❌ Критическая ошибка при пересоздании таблицы: {e2}")
    
    def add_site(self, domain, name=None):
        """Добавляет сайт для отслеживания."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO sites (domain, name) VALUES (?, ?)",
                (domain, name or domain)
            )
            site_id = cursor.lastrowid
            conn.commit()
            return site_id
        except Exception as e:
            print(f"Ошибка добавления сайта: {e}")
            return None
        finally:
            conn.close()
    
    def add_keyword(self, site_id, keyword, search_engine="google"):
        """Добавляет ключевое слово для отслеживания."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO keywords (site_id, keyword, search_engine) VALUES (?, ?, ?)",
                (site_id, keyword, search_engine)
            )
            keyword_id = cursor.lastrowid
            conn.commit()
            return keyword_id
        except Exception as e:
            print(f"Ошибка добавления ключевого слова: {e}")
            return None
        finally:
            conn.close()
    
    def get_sites(self):
        """Получает список всех сайтов."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, domain, name, created_at FROM sites ORDER BY created_at DESC")
        sites = cursor.fetchall()
        conn.close()
        
        return [{"id": row[0], "domain": row[1], "name": row[2], "created_at": row[3]} for row in sites]
    
    def get_keywords(self, site_id=None):
        """Получает список ключевых слов."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if site_id:
            cursor.execute(
                "SELECT k.id, k.keyword, k.search_engine, s.domain, k.created_at FROM keywords k JOIN sites s ON k.site_id = s.id WHERE k.site_id = ? ORDER BY k.created_at DESC",
                (site_id,)
            )
        else:
            cursor.execute(
                "SELECT k.id, k.keyword, k.search_engine, s.domain, k.created_at FROM keywords k JOIN sites s ON k.site_id = s.id ORDER BY k.created_at DESC"
            )
        
        keywords = cursor.fetchall()
        conn.close()
        
        return [{"id": row[0], "keyword": row[1], "search_engine": row[2], "domain": row[3], "created_at": row[4]} for row in keywords]
    
    def get_positions_history(self, keyword_id, days=30):
        """Получает историю позиций для ключевого слова."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT position, url, title, snippet, checked_at FROM positions WHERE keyword_id = ? AND checked_at >= datetime('now', '-{} days') ORDER BY checked_at ASC".format(days),
            (keyword_id,)
        )
        
        positions = cursor.fetchall()
        conn.close()
        
        return [{"position": row[0], "url": row[1], "title": row[2], "snippet": row[3], "checked_at": row[4]} for row in positions]
    
    def create_webdriver(self, headless=True):
        """Создает WebDriver для поиска."""
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"Ошибка создания WebDriver: {e}")
            return None
    
    def search_google(self, keyword, max_results=10):
        """Выполняет поиск в Google."""
        driver = self.create_webdriver()
        if not driver:
            return []
        
        try:
            search_url = f"https://www.google.com/search?q={quote_plus(keyword)}&num={max_results}"
            driver.get(search_url)
            time.sleep(2)
            
            results = []
            search_results = driver.find_elements(By.CSS_SELECTOR, "div.g")
            
            for i, result in enumerate(search_results[:max_results], 1):
                try:
                    link_element = result.find_element(By.CSS_SELECTOR, "a")
                    url = link_element.get_attribute("href")
                    title_element = result.find_element(By.CSS_SELECTOR, "h3")
                    title = title_element.text if title_element else ""
                    
                    # Получаем сниппет
                    snippet_element = result.find_element(By.CSS_SELECTOR, "div.VwiC3b")
                    snippet = snippet_element.text if snippet_element else ""
                    
                    if url and title:
                        results.append({
                            "position": i,
                            "url": url,
                            "title": title,
                            "snippet": snippet
                        })
                except Exception as e:
                    continue
            
            return results
        except Exception as e:
            print(f"Ошибка поиска в Google: {e}")
            return []
        finally:
            driver.quit()
    
    def search_yandex(self, keyword, max_results=10):
        """Выполняет поиск в Яндекс."""
        driver = self.create_webdriver()
        if not driver:
            return []
        
        try:
            search_url = f"https://yandex.ru/search/?text={quote_plus(keyword)}&numdoc={max_results}"
            driver.get(search_url)
            time.sleep(2)
            
            results = []
            search_results = driver.find_elements(By.CSS_SELECTOR, "li.serp-item")
            
            for i, result in enumerate(search_results[:max_results], 1):
                try:
                    link_element = result.find_element(By.CSS_SELECTOR, "a.link")
                    url = link_element.get_attribute("href")
                    title_element = result.find_element(By.CSS_SELECTOR, "a.link .organic__url-text")
                    title = title_element.text if title_element else ""
                    
                    # Получаем сниппет
                    snippet_element = result.find_element(By.CSS_SELECTOR, ".organic__content-wrapper .text")
                    snippet = snippet_element.text if snippet_element else ""
                    
                    if url and title:
                        results.append({
                            "position": i,
                            "url": url,
                            "title": title,
                            "snippet": snippet
                        })
                except Exception as e:
                    continue
            
            return results
        except Exception as e:
            print(f"Ошибка поиска в Яндекс: {e}")
            return []
        finally:
            driver.quit()
    
    def check_position(self, keyword, domain, search_engine="google"):
        """Проверяет позицию сайта по ключевому слову."""
        if search_engine.lower() == "google":
            results = self.search_google(keyword)
        elif search_engine.lower() == "yandex":
            results = self.search_yandex(keyword)
        else:
            return None
        
        # Ищем сайт в результатах
        for result in results:
            if domain in result["url"]:
                return result
        
        return None
    
    def track_keyword(self, keyword_id, keyword, domain, search_engine="google"):
        """Отслеживает позицию по ключевому слову и сохраняет результат."""
        result = self.check_position(keyword, domain, search_engine)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if result:
                cursor.execute(
                    "INSERT INTO positions (keyword_id, position, url, title, snippet) VALUES (?, ?, ?, ?, ?)",
                    (keyword_id, result["position"], result["url"], result["title"], result["snippet"])
                )
            else:
                # Если сайт не найден в топ-10, записываем позицию 0
                cursor.execute(
                    "INSERT INTO positions (keyword_id, position, url, title, snippet) VALUES (?, ?, ?, ?, ?)",
                    (keyword_id, 0, "", "", "")
                )
            
            conn.commit()
            return result
        except Exception as e:
            print(f"Ошибка сохранения позиции: {e}")
            return None
        finally:
            conn.close()
    
    def track_all_keywords(self, site_id=None):
        """Отслеживает все ключевые слова."""
        keywords = self.get_keywords(site_id)
        results = []
        
        for kw in keywords:
            site = self.get_site_by_id(kw["id"])
            if site:
                result = self.track_keyword(kw["id"], kw["keyword"], site["domain"], kw["search_engine"])
                results.append({
                    "keyword": kw["keyword"],
                    "search_engine": kw["search_engine"],
                    "result": result
                })
        
        return results
    
    def get_site_by_id(self, keyword_id):
        """Получает сайт по ID ключевого слова."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT s.id, s.domain, s.name FROM sites s JOIN keywords k ON s.id = k.site_id WHERE k.id = ?",
            (keyword_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {"id": row[0], "domain": row[1], "name": row[2]}
        return None
    
    def generate_position_chart(self, keyword_id, days=30):
        """Генерирует график движения позиций."""
        history = self.get_positions_history(keyword_id, days)
        
        if not history:
            return None
        
        dates = [datetime.strptime(pos["checked_at"], "%Y-%m-%d %H:%M:%S") for pos in history]
        positions = [pos["position"] for pos in history]
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, positions, marker='o', linewidth=2, markersize=6)
        plt.gca().invert_yaxis()  # Инвертируем ось Y (лучшие позиции сверху)
        
        plt.title("Движение позиций по времени", fontsize=14, fontweight='bold')
        plt.xlabel("Дата", fontsize=12)
        plt.ylabel("Позиция", fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Форматирование дат
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
        plt.xticks(rotation=45)
        
        # Добавляем аннотации для лучших и худших позиций
        if positions:
            best_pos = min(positions)
            worst_pos = max(positions)
            best_date = dates[positions.index(best_pos)]
            worst_date = dates[positions.index(worst_pos)]
            
            plt.annotate(f'Лучшая: {best_pos}', xy=(best_date, best_pos), 
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='green', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
            
            plt.annotate(f'Худшая: {worst_pos}', xy=(worst_date, worst_pos), 
                        xytext=(10, -10), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        plt.tight_layout()
        
        # Сохраняем в base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def export_to_excel(self, site_id=None, filename=None):
        """Экспортирует данные в Excel."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"serp_report_{timestamp}.xlsx"
        
        # Получаем данные
        keywords = self.get_keywords(site_id)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Лист с ключевыми словами
            keywords_df = pd.DataFrame(keywords)
            keywords_df.to_excel(writer, sheet_name='Ключевые слова', index=False)
            
            # Лист с позициями
            all_positions = []
            for kw in keywords:
                history = self.get_positions_history(kw["id"])
                for pos in history:
                    all_positions.append({
                        "Ключевое слово": kw["keyword"],
                        "Поисковик": kw["search_engine"],
                        "Домен": kw["domain"],
                        "Позиция": pos["position"],
                        "URL": pos["url"],
                        "Заголовок": pos["title"],
                        "Дата проверки": pos["checked_at"]
                    })
            
            positions_df = pd.DataFrame(all_positions)
            positions_df.to_excel(writer, sheet_name='Позиции', index=False)
            
            # Лист со сводкой
            summary_data = []
            for kw in keywords:
                history = self.get_positions_history(kw["id"])
                if history:
                    current_pos = history[-1]["position"]
                    best_pos = min(pos["position"] for pos in history if pos["position"] > 0)
                    worst_pos = max(pos["position"] for pos in history)
                    
                    summary_data.append({
                        "Ключевое слово": kw["keyword"],
                        "Поисковик": kw["search_engine"],
                        "Домен": kw["domain"],
                        "Текущая позиция": current_pos,
                        "Лучшая позиция": best_pos,
                        "Худшая позиция": worst_pos,
                        "Количество проверок": len(history)
                    })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Сводка', index=False)
        
        return filename
    
    def get_statistics(self, site_id=None):
        """Получает статистику по позициям."""
        keywords = self.get_keywords(site_id)
        stats = {
            "total_keywords": len(keywords),
            "google_keywords": len([kw for kw in keywords if kw["search_engine"] == "google"]),
            "yandex_keywords": len([kw for kw in keywords if kw["search_engine"] == "yandex"]),
            "top_3": 0,
            "top_10": 0,
            "not_found": 0
        }
        
        for kw in keywords:
            history = self.get_positions_history(kw["id"], days=1)  # Только последняя проверка
            if history:
                last_position = history[-1]["position"]
                if last_position == 0:
                    stats["not_found"] += 1
                elif last_position <= 3:
                    stats["top_3"] += 1
                elif last_position <= 10:
                    stats["top_10"] += 1
        
        return stats

def run_serp_tracking(keywords_list, domain, search_engines=["google", "yandex"], update_callback=None):
    """Запускает трекинг позиций для списка ключевых слов."""
    tracker = SERPTracker()
    
    # Добавляем сайт
    site_id = tracker.add_site(domain)
    if not site_id:
        return {"error": "Не удалось добавить сайт"}
    
    results = []
    total_keywords = len(keywords_list) * len(search_engines)
    current = 0
    
    for keyword in keywords_list:
        for engine in search_engines:
            try:
                # Добавляем ключевое слово
                keyword_id = tracker.add_keyword(site_id, keyword, engine)
                if keyword_id:
                    # Отслеживаем позицию
                    result = tracker.track_keyword(keyword_id, keyword, domain, engine)
                    
                    results.append({
                        "keyword": keyword,
                        "search_engine": engine,
                        "position": result["position"] if result else 0,
                        "url": result["url"] if result else "",
                        "title": result["title"] if result else "",
                        "status": "success"
                    })
                else:
                    results.append({
                        "keyword": keyword,
                        "search_engine": engine,
                        "position": 0,
                        "url": "",
                        "title": "",
                        "status": "error"
                    })
                
                current += 1
                if update_callback:
                    update_callback(current, total_keywords, f"Проверено: {keyword} в {engine}")
                
                # Пауза между запросами
                time.sleep(2)
                
            except Exception as e:
                results.append({
                    "keyword": keyword,
                    "search_engine": engine,
                    "position": 0,
                    "url": "",
                    "title": "",
                    "status": f"error: {str(e)}"
                })
                current += 1
    
    return {
        "site_id": site_id,
        "results": results,
        "statistics": tracker.get_statistics(site_id)
    }

def run_detailed_site_analysis(domain, search_engines=["google", "yandex"], update_callback=None):
    """Запускает подробный анализ сайта с автоматическим поиском ключевых слов и трекингом позиций."""
    tracker = SERPTracker()
    
    # Добавляем сайт
    site_id = tracker.add_site(domain)
    if not site_id:
        return {"error": "Не удалось добавить сайт"}
    
    # Автоматически генерируем ключевые слова на основе домена
    auto_keywords = generate_keywords_from_domain(domain)
    
    # Добавляем базовые ключевые слова
    base_keywords = [
        domain.replace('.com', '').replace('.ru', '').replace('.org', '').replace('.net', ''),
        domain,
        f"сайт {domain}",
        f"официальный сайт {domain}"
    ]
    
    all_keywords = list(set(base_keywords + auto_keywords))
    
    results = []
    detailed_results = []
    total_keywords = len(all_keywords) * len(search_engines)
    current = 0
    
    for keyword in all_keywords:
        for engine in search_engines:
            try:
                # Добавляем ключевое слово
                keyword_id = tracker.add_keyword(site_id, keyword, engine)
                if keyword_id:
                    # Получаем детальную информацию о поисковой выдаче
                    search_results = get_detailed_search_results(keyword, domain, engine, tracker)
                    
                    # Отслеживаем позицию
                    result = tracker.track_keyword(keyword_id, keyword, domain, engine)
                    
                    position = result["position"] if result else 0
                    url = result["url"] if result else ""
                    title = result["title"] if result else ""
                    
                    results.append({
                        "keyword": keyword,
                        "search_engine": engine,
                        "position": position,
                        "url": url,
                        "title": title,
                        "status": "success"
                    })
                    
                    # Добавляем детальную информацию
                    detailed_results.append({
                        "keyword": keyword,
                        "search_engine": engine,
                        "position": position,
                        "url": url,
                        "title": title,
                        "snippet": result.get("snippet", "") if result else "",
                        "search_results": search_results,
                        "status": "success"
                    })
                else:
                    results.append({
                        "keyword": keyword,
                        "search_engine": engine,
                        "position": 0,
                        "url": "",
                        "title": "",
                        "status": "error"
                    })
                
                current += 1
                if update_callback:
                    update_callback(current, total_keywords, f"Проверено: '{keyword}' в {engine}")
                
                # Пауза между запросами
                time.sleep(2)
                
            except Exception as e:
                results.append({
                    "keyword": keyword,
                    "search_engine": engine,
                    "position": 0,
                    "url": "",
                    "title": "",
                    "status": f"error: {str(e)}"
                })
                current += 1
    
    return {
        "site_id": site_id,
        "domain": domain,
        "keywords_checked": all_keywords,
        "results": results,
        "detailed_results": detailed_results,
        "statistics": tracker.get_statistics(site_id),
        "charts": generate_charts_for_site(site_id, tracker)
    }

def generate_keywords_from_domain(domain):
    """Генерирует ключевые слова на основе домена."""
    # Убираем расширения домена
    clean_domain = domain.replace('.com', '').replace('.ru', '').replace('.org', '').replace('.net', '')
    
    # Разбиваем на слова
    words = clean_domain.split('.')
    keywords = []
    
    for word in words:
        if len(word) > 2:  # Игнорируем слишком короткие слова
            keywords.extend([
                word,
                f"{word} купить",
                f"{word} заказать",
                f"{word} цена",
                f"{word} отзывы",
                f"{word} официальный сайт"
            ])
    
    return keywords[:20]  # Ограничиваем количество ключевых слов

def get_detailed_search_results(keyword, domain, search_engine, tracker):
    """Получает детальную информацию о поисковой выдаче."""
    try:
        if search_engine == "google":
            results = tracker.search_google(keyword, max_results=10)
        elif search_engine == "yandex":
            results = tracker.search_yandex(keyword, max_results=10)
        else:
            return []
        
        # Находим позицию нашего сайта
        our_position = 0
        our_result = None
        
        for i, result in enumerate(results, 1):
            if domain in result.get("url", ""):
                our_position = i
                our_result = result
                break
        
        return {
            "our_position": our_position,
            "our_result": our_result,
            "all_results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        return {
            "our_position": 0,
            "our_result": None,
            "all_results": [],
            "total_results": 0,
            "error": str(e)
        }

def generate_charts_for_site(site_id, tracker):
    """Генерирует графики для сайта."""
    try:
        keywords = tracker.get_keywords(site_id)
        charts = {}
        
        for kw in keywords:
            chart_data = tracker.generate_position_chart(kw["id"], days=30)
            if chart_data:
                charts[f"{kw['keyword']}_{kw['search_engine']}"] = chart_data
        
        return charts
    except Exception as e:
        return {"error": str(e)} 