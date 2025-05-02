import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class MatchesScraper:
    def __init__(self):
        self.chrome_options = Options()
        self._setup_chrome_options()
        self.cache_ttl = 3600  # 1 hora de cache
        self.last_update = 0
        self.cached_matches = []

    def _setup_chrome_options(self):
        """Configura as opções do Chrome para o modo headless"""
        self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920x1080")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--enable-unsafe-swiftshader")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    def _get_driver(self):
        """Inicializa e retorna o WebDriver usando o Chrome e ChromeDriver já instalados"""
        try:
           
            logger.info("Iniciando ChromeDriver diretamente")
            return webdriver.Chrome(options=self.chrome_options)
        except Exception as e:
            logger.error(f"Erro ao iniciar ChromeDriver: {str(e)}")
            raise

    def _is_cache_valid(self):
        """Verifica se o cache ainda é válido"""
        return (time.time() - self.last_update) < self.cache_ttl

    def get_furia_matches(self, force_update=False):
        """Obtém as partidas da FURIA com cache"""
        if not force_update and self._is_cache_valid() and self.cached_matches:
            return self.cached_matches
            
        try:
            driver = self._get_driver()
            matches = self._scrape_matches(driver)
            self.cached_matches = matches
            self.last_update = time.time()
            return matches
        except Exception as e:
            logger.error(f"Erro ao obter partidas: {str(e)}")
            return self.cached_matches if not force_update else []
        finally:
            if 'driver' in locals():
                driver.quit()

    def _scrape_matches(self, driver):
        """Faz o scraping das partidas no site"""
        logger.info("Acessando draft5.gg para obter partidas da FURIA...")
        driver.get("https://draft5.gg/equipe/330-FURIA/proximas-partidas")
        time.sleep(5)  # Espera o carregamento completo

        # Nova verificação de partidas
        no_matches = driver.find_elements(By.XPATH, "//div[contains(@class, 'no-matches')]")
        if no_matches:
            return []

        # Seletores atualizados
        matches = []
        match_items = driver.find_elements(By.XPATH, "//div[contains(@class, 'match-card')]")
        
        for item in match_items:
            try:
                match_data = self._extract_match_data(item.text)
                if match_data:
                    matches.append(match_data)
            except Exception as e:
                logger.error(f"Erro ao processar partida: {str(e)}")
                continue
                
        return matches

    def _extract_match_data(self, match_text):
        """Extrai os dados de uma partida do texto"""
      
        teams = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', match_text)
        away_team = next((t for t in teams if t.lower() != "furia"), "Desconhecido")

        # Extração de data/hora com timezone
        date_time = self._extract_datetime(match_text) + " -03"

        # Detecção de formato de jogo
        match_format = re.search(r'(BO\d+|MD\d+)', match_text)
        
        return {
            'opponent': away_team,
            'event': self._extract_event(match_text),
            'format': match_format.group(1) if match_format else "BO3",
            'time': date_time,
            'link': 'https://draft5.gg/equipe/330-FURIA/proximas-partidas'
        }

    def _extract_event(self, text):
        """Extrai o nome do evento com precisão"""
        event_match = re.search(r'(?P<event>[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\s\d{4}', text)
        return event_match.group('event') if event_match else "Evento desconhecido"

    def _extract_datetime(self, text):
        """Extrai data e hora com validação reforçada"""
        try:
            # Padrão internacional
            dt_match = re.search(r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2})', text)
            if dt_match:
                datetime.strptime(f"{dt_match.group(1)} {dt_match.group(2)}", "%d/%m/%Y %H:%M")
                return f"{dt_match.group(1)} {dt_match.group(2)}"
            
            # Padrão localizado
            date_match = re.search(r'(\d{1,2})\s+DE\s+([A-ZÇ]+)\s+DE\s+(\d{4})', text, re.IGNORECASE)
            time_match = re.search(r'(\d{2}:\d{2})', text)
            
            if date_match and time_match:
                months = {
                    'JANEIRO': '01', 'FEVEREIRO': '02', 'MARÇO': '03',
                    'ABRIL': '04', 'MAIO': '05', 'JUNHO': '06',
                    'JULHO': '07', 'AGOSTO': '08', 'SETEMBRO': '09',
                    'OUTUBRO': '10', 'NOVEMBRO': '11', 'DEZEMBRO': '12'
                }
                return f"{date_match.group(1).zfill(2)}/{months[date_match.group(2).upper()]}/{date_match.group(3)} {time_match.group(1)}"
        except Exception as e:
            logger.warning(f"Formato de data inválido: {str(e)}")
        
        return datetime.now().strftime("%d/%m/%Y %H:%M")

matches_scraper = MatchesScraper()