import logging
import re
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MatchesScraper:
    def __init__(self):
        self.chrome_options = Options()
        self._setup_chrome_options()
        self.cache_ttl = 3600  # 1 hora
        self.last_update = 0
        self.cached_matches = []

    def _setup_chrome_options(self):
        self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920x1080")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

    def _is_cache_valid(self):
        return (time.time() - self.last_update) < self.cache_ttl

    def _get_driver(self):
        try:
            return webdriver.Chrome(options=self.chrome_options)
        except Exception as e:
            logger.error(f"Erro ao iniciar o driver: {e}")
            raise

    def get_furia_matches(self, force_update=False):
        if not force_update and self._is_cache_valid() and self.cached_matches:
            return self.cached_matches

        driver = None
        try:
            driver = self._get_driver()
            matches = self._scrape_matches(driver)
            self.cached_matches = matches
            self.last_update = time.time()
            return matches
        except Exception as e:
            logger.error(f"Erro no scraping: {e}")
            return self.cached_matches if not force_update else []
        finally:
            if driver:
                driver.quit()

    def _extract_page_date(self, driver):
        try:
            el = driver.find_element(
                By.CSS_SELECTOR, 'p[class*="MatchList__MatchListDate"]'
            )
            text = el.text.strip()
            m = re.search(r'(\d{1,2}) de (\w+) de (\d{4})', text, re.IGNORECASE)
            if not m:
                raise ValueError("Formato de data não reconhecido")
            day, month_str, year = m.groups()
            month_str = month_str.lower()
            month_map = {
                'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
                'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
            }
            month = month_map.get(month_str)
            if not month:
                raise ValueError(f"Mês desconhecido: {month_str}")
            return datetime(int(year), month, int(day))
        except Exception as e:
            logger.warning(f"Não foi possível extrair data da página: {e}")
            return datetime.now()

    def _scrape_matches(self, driver):
        driver.get("https://draft5.gg/equipe/330-FURIA/proximas-partidas")
        time.sleep(5)
        page_date = self._extract_page_date(driver)
        containers = driver.find_elements(
            By.CSS_SELECTOR, 'a[class*="MatchCardSimple__MatchContainer"]'
        )

        matches = []
        for container in containers:
            try:
                teams = container.find_elements(
                    By.CSS_SELECTOR, 'div[class*="TeamNameAndLogo"] span'
                )
                team_names = [t.text.strip() for t in teams if t.text.strip()]
                opponent = next(
                    (t for t in team_names if t.lower() != "furia"), "Desconhecido"
                )

                format_text = container.find_element(
                    By.CSS_SELECTOR, 'div[class*="Badge"]'
                ).text.strip() if container.find_elements(
                    By.CSS_SELECTOR, 'div[class*="Badge"]'
                ) else ""

                event_text = container.find_element(
                    By.CSS_SELECTOR, 'div[class*="Tournament"]'
                ).text.strip() if container.find_elements(
                    By.CSS_SELECTOR, 'div[class*="Tournament"]'
                ) else ""

                datetime_info = self._extract_date_time(container, page_date)
                matches.append({
                    'opponent': opponent,
                    'date': datetime_info['date_str'],
                    'time': datetime_info['time_str'],
                    'format': format_text,
                    'event': event_text,
                    'link': container.get_attribute('href')
                })
            except Exception as e:
                logger.error(f"Erro ao processar partida: {e}")

        return matches

    def _extract_date_time(self, container, page_date):
        try:
            time_el = container.find_element(
                By.CSS_SELECTOR, 'small[class*="MatchTime"]'
            )
            time_text = time_el.text.strip().upper()
        except:
            time_text = "TBA"

        if "TBA" in time_text:
            return {'date_str': page_date.strftime("%Y-%m-%d"), 'time_str': "TBA"}

        time_match = re.search(r'(\d{1,2}:\d{2})', time_text)
        if not time_match:
            return {'date_str': page_date.strftime("%Y-%m-%d"), 'time_str': "TBA"}

        hour_text = time_match.group(1)

        try:
            raw = container.text
            day_match = re.search(r'(\d{1,2})\s+de\s+\w+', raw) or re.search(r'(\d{1,2})[/-]', raw)
            day = int(day_match.group(1)) if day_match else page_date.day
        except:
            day = page_date.day

        try:
            dt = datetime.strptime(
                f"{page_date.year}-{page_date.month}-{day} {hour_text}",
                "%Y-%m-%d %H:%M"
            )
            dt -= timedelta(hours=3)
            return {
                'date_str': dt.strftime("%Y-%m-%d"),
                'time_str': dt.strftime("%H:%M")
            }
        except:
            return {'date_str': page_date.strftime("%Y-%m-%d"), 'time_str': "TBA"}

matches_scraper = MatchesScraper()