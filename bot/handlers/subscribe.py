from telegram import Update
from telegram.ext import ContextTypes
from bot.services.storage import JSONStorage
import logging

logger = logging.getLogger(__name__)
storage = JSONStorage()

async def subscribe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para inscrição de notificações"""
    try:
        user_id = update.effective_user.id
        storage.add_subscription(user_id)
        
        await update.message.reply_text(
            "✅ Você foi inscrito nas notificações!\n"
            "Receberá alertas 1 hora antes das partidas.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Erro na inscrição: {str(e)}")
        await update.message.reply_text("❌ Falha na inscrição. Tente novamente.")