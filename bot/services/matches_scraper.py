import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

class MatchesScraper:
    def __init__(self):
        self.chrome_options = Options()
        self._setup_chrome_options()
        self.cache_ttl = 3600  # 1 hora
        self.last_update = 0
        self.cached_matches = []
        # Definição do fuso horário do Brasil (Brasília)
        self.brazil_timezone = pytz.timezone('America/Sao_Paulo')

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

    def _parse_match_datetime(self, time_str):
        """
        Converte a string de tempo do site para um objeto datetime no fuso horário do Brasil.
        O site provavelmente apresenta horários em UTC ou outro fuso, então convertemos para o fuso brasileiro.
        Retorna no formato "%Y-%m-%d %H:%M" para compatibilidade com o handler existente.
        """
        try:
            # Assumindo que o formato do site é HH:MM
            current_date = datetime.now()
            day = 10  # Você está usando dia 10 no código original
            
            # Cria um datetime com a data atual e o horário do match
            dt_str = f"{current_date.year}-{current_date.month}-{day} {time_str}"
            
            # Presumindo que o horário original está em UTC
            utc_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            utc_dt = pytz.UTC.localize(utc_dt)
            
            # Converte para o fuso horário do Brasil
            br_dt = utc_dt.astimezone(self.brazil_timezone)
            
            # Retorna apenas no formato esperado pela função que consome os dados
            return br_dt.strftime("%Y-%m-%d %H:%M")
        except Exception as e:
            logger.error(f"Erro ao converter horário: {str(e)}")
            return time_str + " (horário original)"

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
                original_time = time_element.text
                brazil_time = self._parse_match_datetime(original_time)
                
                matches.append({
                    'opponent': opponent,
                    'time': brazil_time,
                    'format': format_element.text.strip(),
                    'event': event_element.text.strip(),
                    'link': container.get_attribute('href')
                })
            except Exception as e:
                logger.error(f"Erro ao processar partida: {str(e)}")
        
        return matches

matches_scraper = MatchesScraper()