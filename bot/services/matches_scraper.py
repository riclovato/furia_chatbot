import logging
from functools import lru_cache
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class MatchesScraper:
    def __init__(self):
        self.chrome_options = Options()
        self._setup_chrome_options()
        self.cache_ttl = 3600  # 1 hora de cache
        self.last_update = 0

    def _setup_chrome_options(self):
        """Configura as opções do Chrome para o modo headless"""
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920x1080")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    def _get_driver(self):
        """Inicializa e retorna o WebDriver"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=self.chrome_options)
        except Exception as e:
            logger.warning(f"Usando ChromeDriver local: {str(e)}")
            return webdriver.Chrome(options=self.chrome_options)

    def _is_cache_valid(self):
        """Verifica se o cache ainda é válido"""
        return (time.time() - self.last_update) < self.cache_ttl

    @lru_cache(maxsize=1)
    def get_furia_matches(self, force_update=False):
        """
        Obtém as partidas da FURIA com cache
        :param force_update: Ignora o cache e força atualização
        :return: Lista de partidas ou lista vazia se não houver
        """
        if not force_update and self._is_cache_valid():
            return self._get_cached_matches()
            
        try:
            driver = self._get_driver()
            matches = self._scrape_matches(driver)
            self.last_update = time.time()
            return matches
        except Exception as e:
            logger.error(f"Erro ao obter partidas: {str(e)}")
            return []
        finally:
            if 'driver' in locals():
                driver.quit()

    def _scrape_matches(self, driver):
        """Faz o scraping das partidas no site"""
        logger.info("Acessando draft5.gg para obter partidas da FURIA...")
        driver.get("https://draft5.gg/equipe/330-FURIA/proximas-partidas")
        time.sleep(3)  # Espera o carregamento

        # Verifica se não há partidas
        no_matches = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'sem partidas') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'nenhuma partida')]")
        if no_matches:
            return []

        # Extrai as partidas
        matches = []
        match_items = driver.find_elements(By.XPATH, "//div[contains(@class, 'match') or contains(@class, 'partida')]")
        
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
        # Times
        teams = re.findall(r'([A-Z]{2,}|[A-Z][a-z]+)', match_text)
        home_team = "FURIA"
        away_team = next((t for t in teams if t != "FURIA"), "Desconhecido")

        # Data e hora
        date_time = self._extract_datetime(match_text)
        
        # Formato
        match_format = re.search(r'(MD\d+|BO\d+)', match_text)
        match_format = match_format.group(1) if match_format else "MD3"

        # Evento
        event = re.search(r'(BLAST|ESL|IEM|Major|Champions|Rivals|Spring|Winter|Fall|Summer).*?\d{4}', match_text)
        event = event.group() if event else "Evento desconhecido"

        return {
            'opponent': away_team,
            'event': event,
            'format': match_format,
            'time': date_time,
            'link': 'https://draft5.gg/equipe/330-FURIA/proximas-partidas'
        }

    def _extract_datetime(self, text):
        """Extrai data e hora do texto"""
        # Tenta formato dd/mm/yyyy hh:mm
        dt_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4}) (\d{1,2}:\d{2})', text)
        if dt_match:
            return f"{dt_match.group(1)} {dt_match.group(2)}"
        
        # Tenta formato "30 DE ABRIL DE 2025 13:30"
        date_match = re.search(r'(\d{1,2}).*?DE.*?([A-Za-zÇç]+).*?(\d{4})', text, re.IGNORECASE)
        time_match = re.search(r'(\d{1,2}:\d{2})', text)
        
        if date_match and time_match:
            day = date_match.group(1).zfill(2)
            month_name = date_match.group(2).upper()
            year = date_match.group(3)
            time_str = time_match.group(1)
            
            months = {
                'JANEIRO': '01', 'FEVEREIRO': '02', 'MARÇO': '03', 'ABRIL': '04',
                'MAIO': '05', 'JUNHO': '06', 'JULHO': '07', 'AGOSTO': '08',
                'SETEMBRO': '09', 'OUTUBRO': '10', 'NOVEMBRO': '11', 'DEZEMBRO': '12'
            }
            
            month = months.get(month_name, '01')
            return f"{day}/{month}/{year} {time_str}"
        
        return "Data desconhecida"

    def _get_cached_matches(self):
        """Método placeholder para o cache"""
        return []

# Instância global do scraper
matches_scraper = MatchesScraper()