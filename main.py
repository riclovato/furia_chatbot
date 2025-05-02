import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler
from bot.handlers import start, players, matches, social, subscribe, unsubscribe
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Configuração básica
load_dotenv()

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cria app Flask
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🟡⚫ FURIA Bot está online! ⚫🟡", 200

@flask_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    """Inicia o servidor Flask em uma thread separada"""
    flask_app.run(host='0.0.0.0', port=8080)

def main():
    try:
        logger.info("Iniciando o bot...")
        
        # Inicia servidor Flask em thread separada
        Thread(target=run_flask, daemon=True).start()
        
        # Cria a aplicação do Telegram
        app = ApplicationBuilder() \
            .token(os.getenv("BOT_TOKEN")) \
            .build()
        
        # Adiciona handlers
        app.add_handler(CommandHandler("start", start.start_handler))
        app.add_handler(CommandHandler("team", players.team_handler))
        app.add_handler(CommandHandler("matches", matches.matches_handler))
        app.add_handler(CommandHandler("social", social.social_handler))
        app.add_handler(CommandHandler("subscribe", subscribe.subscribe_handler))
        app.add_handler(CommandHandler("unsubscribe", unsubscribe.unsubscribe_handler))
        app.add_handler(CallbackQueryHandler(players.button_handler))

        # Handler para mensagens desconhecidas
        app.add_handler(
            MessageHandler(
                filters.ALL & ~filters.COMMAND,
                start.start_handler  # Reutiliza o handler de start
            ),
            group=1
        )
 
        # Keep-alive
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(lambda: logger.info("🟢 Keep-alive"), 'interval', minutes=14)
        scheduler.start()

        logger.info("Bot iniciado com sucesso")
        app.run_polling()
        
    except Exception as e:
        logger.critical(f"Falha ao iniciar o bot: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()