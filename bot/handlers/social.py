from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def social_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /social"""
    try:
        social_links = """
        <b>📱 Redes Sociais Oficiais da FURIA:</b>

        🔹 X: <a href="https://x.com/FURIA">@FURIA</a>
        🔸 Instagram: <a href="https://instagram.com/furiagg">@furiagg</a>
        🔹 Facebook: <a href="https://www.facebook.com/furiagg/">/furiagg</a>
        🔸 Site Oficial: <a href="https://furia.gg">furia.gg</a>
        🔹 YouTube: <a href="https://www.youtube.com/@furiaggcs">/furiacs</a>
        🔸 Twitch: <a href="https://www.twitch.tv/furiatv">/furiatv</a>

        📍 Acompanhe todas as novidades!
        """
        await update.message.reply_text(
            social_links,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Erro no /social: {str(e)}")