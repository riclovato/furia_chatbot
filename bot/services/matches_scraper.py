import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime

logger = logging.getLogger(__name__)

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
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    def _is_cache_valid(self):
        return (time.time() - self.last_update) < self.cache_ttl

    def _get_driver(self):
        try:
            return webdriver.Chrome(options=self.chrome_options)
        except Exception as e:
            logger.error(f"Erro no driver: {str(e)}")
            raise

    def get_furia_matches(self, force_update=False):
        if not force_update and self._is_cache_valid() and self.cached_matches:
            return self.cached_matches
            
        try:
            driver = self._get_driver()
            matches = self._scrape_matches(driver)
            self.cached_matches = matches
            self.last_update = time.time()
            return matches
        except Exception as e:
            logger.error(f"Erro no scraping: {str(e)}")
            return self.cached_matches if not force_update else []
        finally:
            if 'driver' in locals():
                driver.quit()

    def _scrape_matches(self, driver):
        driver.get("https://draft5.gg/equipe/330-FURIA/proximas-partidas")
        time.sleep(5)
        
        matches = []
        containers = driver.find_elements(By.CSS_SELECTOR, 'a[class*="MatchCardSimple__MatchContainer"]')
        
        for container in containers:
            try:
                time_element = container.find_element(By.CSS_SELECTOR, 'small[class*="MatchTime"] span')
                teams = container.find_elements(By.CSS_SELECTOR, 'div[class*="TeamNameAndLogo"] span')
                format_element = container.find_element(By.CSS_SELECTOR, 'div[class*="Badge"]')
                event_element = container.find_element(By.CSS_SELECTOR, 'div[class*="Tournament"]')
                
                opponent = [t.text for t in teams if t.text.lower() != "furia"][0]
                match_time = f"{datetime.now().year}-{datetime.now().month}-10 {time_element.text}"  # Ajuste conforme necessário
                
                matches.append({
                    'opponent': opponent,
                    'time': match_time,
                    'format': format_element.text.strip(),
                    'event': event_element.text.strip(),
                    'link': container.get_attribute('href')
                })
            except Exception as e:
                logger.error(f"Erro ao processar partida: {str(e)}")
        
        return matches

matches_scraper = MatchesScraper()