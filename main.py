import logging
import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.handlers import matches, players, social, start
from bot.services.notification_service import NotificationService
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import asyncio
import requests
import time

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

# ========== Configuração do Flask para Render ==========
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🟡⚫ FURIA Bot Online ⚫🟡", 200

@flask_app.route('/health')
def health_check():
    return "OK", 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))

# ========== Lógica Principal do Bot ==========
async def telegram_main():
    try:
        application = Application.builder().token(os.getenv("BOT_TOKEN")).build()
        
        # Registro de Handlers
        handlers = [
            CommandHandler("start", start.start_handler),
            CommandHandler("matches", matches.matches_handler),
            CommandHandler("team", players.team_handler),
            CommandHandler("socials", social.social_handler),
            CallbackQueryHandler(matches.handle_notification_callback, pattern="^notif_"),
            CallbackQueryHandler(players.button_handler, pattern="^player_"),
            MessageHandler(filters.ALL & ~filters.COMMAND, start.start_handler)
        ]
        
        for handler in handlers:
            application.add_handler(handler)

        # Configuração do Serviço de Notificações
        notification_service = NotificationService(os.getenv("BOT_TOKEN"))
        application.job_queue.run_repeating(
            notification_service.check_and_notify,
            interval=300,
            first=10
        )

        logger.info("Bot do Telegram inicializado com sucesso")
        await application.run_polling()

    except Exception as e:
        logger.critical(f"Erro crítico: {str(e)}", exc_info=True)
        raise

# ========== Threads Segregadas ==========
def run_telegram():
    asyncio.run(telegram_main())

def keep_alive():
    while True:
        try:
            requests.get(f"https://{os.getenv('RENDER_SERVICE_URL')}/health")
            time.sleep(300)
        except Exception as e:
            logger.warning(f"Erro no keep-alive: {str(e)}")

if __name__ == "__main__":
    # Inicialização do Flask
    Thread(target=run_flask, daemon=True).start()
    
    # Inicialização do Telegram
    Thread(target=run_telegram, daemon=True).start()
    
    # Keep-alive para serviços externos
    Thread(target=keep_alive, daemon=True).start()
    
    # Loop principal de espera
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        logger.info("Encerramento solicitado pelo usuário")