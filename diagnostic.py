#!/usr/bin/env python3
"""
Script para testar o novo scraper de partidas diretamente.
Execute com: python3 test_scraper.py
"""

import logging
import sys
import json
from datetime import datetime

# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper_test.log")
    ]
)

# Importar o scraper
try:
    print("Importando o scraper...")
    # Importe o seu scraper aqui
    # Se estiver em um módulo, substitua a linha abaixo pelo import correto
    # Por exemplo: from bot.services.matches_scraper import matches_scraper
    
    # Para teste standalone, copie o arquivo matches_scraper.py para o mesmo diretório
    # e use o import abaixo:
    from matches_scraper import matches_scraper
    print("Scraper importado com sucesso!")
except Exception as e:
    print(f"ERRO AO IMPORTAR SCRAPER: {str(e)}")
    sys.exit(1)

def run_test():
    """Executar teste do scraper e salvar resultados"""
    print("\n====== TESTE DO SCRAPER DE PARTIDAS ======\n")
    
    try:
        print("Obtendo partidas (forçando atualização)...")
        start_time = datetime.now()
        matches = matches_scraper.get_furia_matches(force_update=True)
        end_time = datetime.now()
        
        # Imprimir tempo de execução
        duration = (end_time - start_time).total_seconds()
        print(f"Tempo de execução: {duration:.2f} segundos")
        
        # Verificar resultados
        if not matches:
            print("\n❌ NENHUMA PARTIDA ENCONTRADA")
            print("Isso pode significar:")
            print("1. Realmente não há partidas agendadas para a FURIA")
            print("2. O scraper não conseguiu extrair os dados corretamente")
            print("\nVerificando manualmente se há partidas...")
            
            # Tente obter mais informações do scraper para diagnóstico
            print("\nVerificando cache:")
            print(f"- Cache TTL: {matches_scraper.cache_ttl}")
            print(f"- Último update: {datetime.fromtimestamp(matches_scraper.last_update) if matches_scraper.last_update > 0 else 'Nunca'}")
            print(f"- Partidas em cache: {len(matches_scraper.cached_matches)}")
        else:
            print(f"\n✅ PARTIDAS ENCONTRADAS: {len(matches)} partidas")
            
            # Imprimir detalhes das partidas
            for i, match in enumerate(matches, 1):
                print(f"\nPartida {i}:")
                for key, value in match.items():
                    print(f"  {key}: {value}")
            
            # Salvar resultados em JSON para referência
            with open("matches_results.json", "w", encoding="utf-8") as f:
                json.dump(matches, f, indent=2, ensure_ascii=False)
            print("\nResultados salvos em matches_results.json")
    
    except Exception as e:
        print(f"\n❌ ERRO DURANTE O TESTE: {str(e)}")
        logging.exception("Erro durante o teste do scraper")
    
    print("\n====== TESTE CONCLUÍDO ======")
    print("\nVerifique o arquivo 'scraper_test.log' para detalhes completos")

if __name__ == "__main__":
    run_test()