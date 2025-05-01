from telegram import Update
from telegram.ext import ContextTypes
from bot.services.storage import JSONStorage
import logging

logger = logging.getLogger(__name__)
storage = JSONStorage()

async def unsubscribe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para cancelar inscrição"""
    try:
        user_id = update.effective_user.id
        storage.remove_subscription(user_id)
        
        await update.message.reply_text(
            "🔕 Inscrição cancelada com sucesso!\n"
            "Você não receberá mais notificações.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Erro no cancelamento: {str(e)}")
        await update.message.reply_text("❌ Falha no cancelamento. Tente novamente.")