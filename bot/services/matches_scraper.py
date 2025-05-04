import logging
import re
import time
from datetime import datetime

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
        """
        Extrai a data principal da página (e.g. "📅 sábado, 10 de maio de 2025")
        e retorna um objeto datetime com ano, mês e dia.
        """
        try:
            el = driver.find_element(
                By.CSS_SELECTOR, 'p[class*="MatchList__MatchListDate"]'
            )
            text = el.text.strip()
            logger.info(f"Data principal encontrada: {text}")
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

        logger.info("Página carregada. Buscando containers de partidas...")
        containers = driver.find_elements(
            By.CSS_SELECTOR, 'a[class*="MatchCardSimple__MatchContainer"]'
        )
        logger.info(f"Encontrados {len(containers)} containers de partidas")

        matches = []
        for idx, container in enumerate(containers, start=1):
            try:
                logger.info(f"Processando partida {idx}/{len(containers)}")

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

                # Extrair data e hora usando a data base da página
                match_datetime = self._extract_date_time(container, page_date)
                logger.info(f"Data/hora extraída: {match_datetime}")

                matches.append({
                    'opponent': opponent,
                    'time': match_datetime.strftime("%Y-%m-%d %H:%M"),
                    'format': format_text,
                    'event': event_text,
                    'link': container.get_attribute('href')
                })
            except Exception as e:
                logger.error(f"Erro ao processar partida {idx}: {e}")

        return matches

    def _extract_date_time(self, container, page_date):
        """
        Extrai o horário do container e combina com a data base (page_date).
        Se houver indicação de outro dia no próprio container, usa-o.
        """
        # Pega o texto do horário (HH:MM)
        try:
            time_el = container.find_element(
                By.CSS_SELECTOR, 'small[class*="MatchTime"]'
            )
            full_time_text = time_el.text
            # Procurar padrão HH:MM
            m = re.search(r'(\d{1,2}:\d{2})', full_time_text)
            hour_text = m.group(1) if m else full_time_text.strip()
        except:
            logger.warning("Não foi possível extrair o horário, usando 12:00")
            hour_text = "12:00"

        # Determina dia/mês/ano base
        day = page_date.day
        month = page_date.month
        year = page_date.year

        # Tenta encontrar um dia explícito no texto do container
        try:
            raw = container.text
            m_day = re.search(r'(\d{1,2})[^\d]+\d{1,2}:\d{2}', raw)
            if m_day:
                day = int(m_day.group(1))
        except:
            pass

        dt_str = f"{year}-{month:02d}-{day:02d} {hour_text}"
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except ValueError:
            logger.error(f"Falha ao converter datetime '{dt_str}', usando agora()")
            return datetime.now()


# Instância pronta para uso
matches_scraper = MatchesScraper()
