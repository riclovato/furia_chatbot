import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from bot.handlers import start, players, matches
from dotenv import load_dotenv

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

async def start_handler(update, context):
    """Handler para o comando /start"""
    welcome_msg = (
        "🟡⚫ <b>Bem-vindo ao FURIA CS2 Bot!</b> ⚫🟡\n\n"
        "⚡ <b>Comandos disponíveis:</b>\n"
        "/start - Mostra esta mensagem\n"
        "/team - Mostra o elenco atual\n"
        "/matches - Próximos jogos (use /matches force para atualizar)\n"
        "🐅 <i>A Paixão que Impulsiona!</i> 🐅"
    )
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode="HTML"
    )

def main():
    try:
        logger.info("Iniciando o bot...")
        
        # Cria a aplicação
        app = ApplicationBuilder() \
            .token(os.getenv("BOT_TOKEN")) \
            .build()
        
        # Handlers principais
        app.add_handler(CommandHandler("start", start_handler))
        app.add_handler(CommandHandler("team", players.team_handler))
        app.add_handler(CommandHandler("matches", matches.matches_handler))

        
        # Handler para callbacks de botões
        app.add_handler(CallbackQueryHandler(players.button_handler))
        
        logger.info("Bot iniciado com sucesso")
        app.run_polling()
        
    except Exception as e:
        logger.critical(f"Falha ao iniciar o bot: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()