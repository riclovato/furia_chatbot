# FURIA Fans Telegram Bot

Bot de Telegram para fãs do time de CS:GO FURIA!  
Receba informações sobre próximos jogos, elenco atual, resultados e notícias diretamente no seu Telegram.

## 🛠 Tecnologias Utilizadas

- Python 3.11+
- [python-telegram-bot](https://python-telegram-bot.org/)
- Requests (consumo de APIs)
- Dotenv (gestão de variáveis de ambiente)
- Hospedagem: [Render.com](https://render.com/)

## 🚀 Como Rodar Localmente

1. Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/furia-fans-telegram-bot.git
    cd furia-fans-telegram-bot
    ```

2. Crie e ative o ambiente virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    .\venv\Scripts\activate    # Windows
    ```

3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4. Configure as variáveis de ambiente:
    - Copie o `.env.example` para `.env`
    - Preencha o arquivo `.env`:
      ```
      BOT_TOKEN=seu_token_do_telegram
      API_KEY=sua_api_key
      ```

5. Execute o bot:
    ```bash
    python main.py
    ```

## 🧩 Comandos Implementados

- `/start` - Boas-vindas
- `/matches` - Próximos jogos da FURIA
- `/players` - Lista de jogadores e estatísticas
- *(Novos comandos serão adicionados em breve!)*

## 🌐 Deploy no Render

- Este projeto já está configurado para deploy automático via Render.com.
- Basta conectar o repositório no Render e definir as variáveis de ambiente.

---
