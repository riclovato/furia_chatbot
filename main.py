import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler
from bot.handlers import matches, players, social, start
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🟡⚫ FURIA Bot está online! ⚫🟡", 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


def main():
    try:
        logger.info("Iniciando o bot...")
        Thread(target=run_flask, daemon=True).start()
        
        app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
        
        # Adiciona handlers
        app.add_handler(CommandHandler("start", start.start_handler))
        app.add_handler(CommandHandler("team", players.team_handler))
        app.add_handler(CommandHandler("matches", matches.matches_handler))
        app.add_handler(CommandHandler("socials", social.social_handler))
       

         # Callback handlers com padrões específicos
        app.add_handler(CallbackQueryHandler(matches.handle_notification_callback, pattern="^notif_"))  
        app.add_handler(CallbackQueryHandler(players.button_handler, pattern="^player_"))

        # Handler para mensagens desconhecidas
        app.add_handler(
            MessageHandler(
                filters.ALL & ~filters.COMMAND,
                start.start_handler  # Reutiliza o handler de start
            ),
            group=1
        )
 
        # Agendador de notificações
        job_queue = app.job_queue
        job_queue.run_repeating(matches.check_and_notify, interval=300, first=10)
        
        logger.info("Bot iniciado com sucesso")
        app.run_polling()
        
    except Exception as e:
        logger.critical(f"Falha ao iniciar o bot: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()