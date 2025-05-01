import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot.handlers import start, players, matches, social, subscribe, unsubscribe
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
    """Handler para o comando /start e mensagens desconhecidas"""
    welcome_msg = (
        "🟡⚫ <b>Bem-vindo ao FURIA CS2 Bot!</b> ⚫🟡\n\n"
        "⚡ <b>Comandos disponíveis:</b>\n"
        "/start - Mostra esta mensagem\n"
        "/team - Mostra o elenco atual\n"
        "/matches - Próximos jogos\n"
        "/social - Redes sociais da FURIA\n"
        "/subscribe - Inscreva-se para notificações\n"
        "/unsubscribe - Cancele sua inscrição\n\n"
        "Follow the steps 🐾"
    )
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode="HTML"
    )

async def unknown_command(update, context):
    """Handler para comandos desconhecidos"""
    await start_handler(update, context)

def main():
    try:
        logger.info("Iniciando o bot...")
        
        # Cria a aplicação
        app = ApplicationBuilder() \
            .token(os.getenv("BOT_TOKEN")) \
            .build()
        
        # Handlers principais (alta prioridade)
        app.add_handler(CommandHandler("start", start_handler))
        app.add_handler(CommandHandler("team", players.team_handler))
        app.add_handler(CommandHandler("matches", matches.matches_handler))
        app.add_handler(CommandHandler("social", social.social_handler))
        app.add_handler(CommandHandler("subscribe", subscribe.subscribe_handler))
        app.add_handler(CommandHandler("unsubscribe", unsubscribe.unsubscribe_handler))
        app.add_handler(CallbackQueryHandler(players.button_handler))

        # Handler para mensagens desconhecidas (baixa prioridade)
        app.add_handler(
            MessageHandler(
                filters.ALL & ~filters.COMMAND,
                unknown_command
            ),
            group=1
        )

        logger.info("Bot iniciado com sucesso")
        app.run_polling()
        
    except Exception as e:
        logger.critical(f"Falha ao iniciar o bot: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()