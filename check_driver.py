import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def test_driver():
    print("🛠️ Testando configuração do ChromeDriver no Windows...")
    
    # 1. Verifica se o arquivo existe
    chrome_driver_path = r"C:\chromedriver-win64\chromedriver.exe"
    if not os.path.exists(chrome_driver_path):
        print(f"❌ ERRO: Arquivo não encontrado em:\n{chrome_driver_path}")
        print("\nPor favor verifique:")
        print("1. Se o caminho está exatamente como mostrado acima")
        print("2. Se o arquivo 'chromedriver.exe' realmente existe nessa pasta")
        print("3. Se você baixou a versão correta para seu Windows (32/64 bits)")
        return False

    # 2. Testa a conexão com o Chrome
    try:
        print("\n🔍 Iniciando teste...")
        options = Options()
        options.add_argument('--headless')  # Execução invisível
        options.add_argument('--disable-gpu')
        options.add_argument('--log-level=3')  # Reduz logs do Chrome
        
        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        print("🌐 Conectando ao Google...")
        driver.get("https://www.google.com")
        print(f"✅ Título da página: '{driver.title}'")
        
        driver.quit()
        print("\n🎉 Teste concluído com sucesso! Seu ChromeDriver está configurado corretamente.")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO durante o teste: {str(e)}")
        print("\nPossíveis soluções:")
        print("1. Verifique se seu Chrome está atualizado (chrome://settings/help)")
        print("2. Baixe a versão do ChromeDriver compatível com sua versão do Chrome")
        print("3. Desative temporariamente antivírus/firewall que possam bloquear a execução")
        print("4. Execute como Administrador se houver problemas de permissão")
        return False

if __name__ == "__main__":
    test_driver()
    input("\nPressione Enter para sair...")  # Mantém a janela aberta
    