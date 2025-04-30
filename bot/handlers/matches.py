import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.services.matches_scraper import matches_scraper
from datetime import datetime

logger = logging.getLogger(__name__)

async def matches_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mostrar próximos jogos da FURIA"""
    try:
        # Verifica se o usuário quer forçar atualização
        force_update = False
        if context.args and context.args[0].lower() == 'force':
            force_update = True
            await update.message.reply_text("⏳ Atualizando dados das partidas...")

        await update.message.reply_text("🔍 Buscando próximos jogos da FURIA...")
        
        # Obtém os dados com cache
        matches = matches_scraper.get_furia_matches(force_update=force_update)
        
        # Formata a mensagem
        message = format_matches_message(matches)
        
        await update.message.reply_text(
            message,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Erro no matches_handler: {str(e)}", exc_info=True)
        await send_fallback_matches(update)

def format_matches_message(matches):
    """Formata mensagem de partidas"""
    if not matches:
        return "📅 Nenhum jogo agendado para a FURIA no momento."
    
    message = "<b>🎮 Próximos Jogos da FURIA:</b>\n\n"
    
    for match in matches:
        message += f"🆚 <b>vs {match['opponent']}</b>\n"
        message += f"🏆 {match['event']} ({match['format']})\n"
        message += f"⏰ {match['time']}\n"
        message += f"🔗 <a href='{match['link']}'>Mais detalhes</a>\n\n"
    
    message += "\nℹ️ Os dados são atualizados a cada hora. Use /matches force para atualizar agora."
    return message

async def send_fallback_matches(update: Update):
    """Mensagem de fallback para partidas"""
    fallback_msg = (
        "⚠️ <b>Calendário de Jogos Indisponível</b>\n\n"
        "Consulte os próximos jogos diretamente no:\n"
        "<a href='https://www.hltv.org/team/8297/furia#tab-matches'>HLTV.org/FURIA</a> ou\n"
        "<a href='https://draft5.gg/equipe/330-FURIA/proximas-partidas'>draft5.gg/FURIA</a>"
    )
    await update.message.reply_text(
        fallback_msg,
        parse_mode="HTML",
        disable_web_page_preview=True
    )