import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start"""
    welcome_msg = (
        "🟡⚫ <b>Bem-vindo ao FURIA CS2 Bot!</b> ⚫🟡\n\n"
        "⚡ <b>Comandos disponíveis:</b>\n"
        "/start - Mostra esta mensagem\n"
        "/team - Mostra o elenco atual\n"
        "/matches - Próximos jogos (use /matches force para atualizar)\n"
        "/store - Compre itens da loja\n"
        "/socials - Redes sociais da FURIA\n"
        "🐅 <i>A Paixão que Impulsiona!</i> 🐅"
    )
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode="HTML"
    )