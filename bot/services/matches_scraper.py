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

    def _parse_br_date(self, date_text):
        """Converte texto de data em português para objeto datetime"""
        try:
            # Formato: "SEXTA-FEIRA, 16 DE MAIO DE 2025"
            m = re.search(r'(\w+)-FEIRA, (\d{1,2}) DE (\w+) DE (\d{4})', date_text, re.IGNORECASE)
            if not m:
                raise ValueError(f"Formato de data não reconhecido: {date_text}")
            
            weekday, day, month_str, year = m.groups()
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
            logger.warning(f"Erro ao analisar data '{date_text}': {e}")
            return None

    def _scrape_matches(self, driver):
        driver.get("https://draft5.gg/equipe/330-FURIA/proximas-partidas")
        time.sleep(5)

        logger.info("Página carregada. Buscando partidas e suas datas...")
        
        # Obter todas as partidas
        match_containers = driver.find_elements(
            By.CSS_SELECTOR, 'a[class*="MatchCardSimple__MatchContainer"]'
        )
        
        logger.info(f"Encontrados {len(match_containers)} containers de partidas")
        
        # Obter todas as datas
        date_elements = driver.find_elements(
            By.CSS_SELECTOR, 'p[class*="MatchList__MatchListDate"]'
        )
        
        logger.info(f"Encontrados {len(date_elements)} elementos de data")
        
        # Processar partidas e associar às datas corretas
        matches = []
        current_date = None
        
        # Para cada elemento na página (na ordem em que aparecem)
        all_elements = driver.find_elements(
            By.XPATH, '//*[contains(@class, "MatchList__MatchListDate") or contains(@class, "MatchCardSimple__MatchContainer")]'
        )
        
        logger.info(f"Encontrados {len(all_elements)} elementos totais (datas + partidas)")
        
        for element in all_elements:
            try:
                # Verifica se o elemento é uma data
                if "MatchList__MatchListDate" in element.get_attribute("class"):
                    date_text = element.text.strip()
                    logger.info(f"Encontrado elemento de data: {date_text}")
                    current_date = self._parse_br_date(date_text)
                    if not current_date:
                        logger.warning(f"Não foi possível interpretar a data: {date_text}")
                
                # Verifica se o elemento é uma partida
                elif "MatchCardSimple__MatchContainer" in element.get_attribute("class") and current_date:
                    logger.info(f"Processando partida com data {current_date}")
                    match_info = self._process_match(element, current_date)
                    if match_info:
                        matches.append(match_info)
            except Exception as e:
                logger.error(f"Erro ao processar elemento: {e}")
        
        # Se não encontramos partidas com o método acima, tentamos uma abordagem alternativa
        if not matches:
            logger.warning("Método de data + partida falhou. Tentando método alternativo...")
            matches = self._scrape_matches_alternative(driver, match_containers)
        
        return matches

    def _scrape_matches_alternative(self, driver, containers):
        """Método alternativo para extrair partidas e suas datas"""
        matches = []
        
        for idx, container in enumerate(containers, start=1):
            try:
                # Para cada partida, procuramos a data mais próxima antes dela
                date_elements = driver.find_elements(
                    By.XPATH, f'(//a[contains(@class, "MatchCardSimple__MatchContainer")])[{idx}]/preceding::p[contains(@class, "MatchList__MatchListDate")][1]'
                )
                
                current_date = None
                if date_elements:
                    date_text = date_elements[0].text.strip()
                    logger.info(f"Data encontrada antes da partida {idx}: {date_text}")
                    current_date = self._parse_br_date(date_text)
                
                if not current_date:
                    logger.warning(f"Não foi possível determinar a data para partida {idx}")
                    current_date = datetime.now()  # Fallback para data atual
                
                match_info = self._process_match(container, current_date)
                if match_info:
                    matches.append(match_info)
                
            except Exception as e:
                logger.error(f"Erro ao processar partida {idx}: {e}")
        
        return matches
    
    def _process_match(self, container, date):
        """Processa um container de partida e extrai suas informações"""
        try:
            # Extrair times
            teams = container.find_elements(
                By.CSS_SELECTOR, 'div[class*="TeamNameAndLogo"] span'
            )
            team_names = [t.text.strip() for t in teams if t.text.strip()]
            opponent = next(
                (t for t in team_names if t.lower() != "furia"), "Desconhecido"
            )

            # Extrair formato e evento
            try:
                format_text = container.find_element(
                    By.CSS_SELECTOR, 'div[class*="Badge"]'
                ).text.strip()
            except:
                format_text = ""
            try:
                event_text = container.find_element(
                    By.CSS_SELECTOR, 'div[class*="Tournament"]'
                ).text.strip()
            except:
                event_text = ""

            # Extrair hora
            time_info = self._extract_time(container)
            logger.info(f"Horário extraído: {time_info}")
            
            return {
                'opponent': opponent,
                'date': date.strftime("%Y-%m-%d"),
                'time': time_info,
                'format': format_text,
                'event': event_text,
                'link': container.get_attribute('href')
            }
        except Exception as e:
            logger.error(f"Erro ao processar informações da partida: {e}")
            return None
    
    def _extract_time(self, container):
        """Extrai apenas o horário da partida exatamente como aparece no site"""
        try:
            time_el = container.find_element(
                By.CSS_SELECTOR, 'small[class*="MatchTime"]'
            )
            time_text = time_el.text.strip().upper()
            
            if "TBA" in time_text:
                return "TBA"
            
            # Extrair apenas o horário (HH:MM) sem fazer ajustes de fuso
            time_match = re.search(r'(\d{1,2}:\d{2})', time_text)
            if not time_match:
                return "TBA"
            
            # Retorna o horário exatamente como está no site
            return time_match.group(1)
            
        except Exception as e:
            logger.error(f"Erro ao extrair horário: {e}")
            return "TBA"


matches_scraper = MatchesScraper()