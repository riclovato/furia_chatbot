import logging
import hashlib
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackContext
from bot.services.matches_scraper import matches_scraper
from bot.services.storage import JSONStorage

logger = logging.getLogger(__name__)
storage = JSONStorage()

async def matches_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal para o comando /matches"""
    try:
        # Verifica se é uma callback query
        if update.callback_query:
            return await handle_notification_callback(update, context)

        # Verifica parâmetros de força atualização
        force_update = False
        if context.args and context.args[0].lower() == 'force':
            force_update = True
            await update.message.reply_text("⏳ Atualização forçada iniciada...")

        status_msg = await update.message.reply_text("🔍 Procurando partidas...")

        try:
            # Obtém partidas com tratamento de erros
            matches = matches_scraper.get_furia_matches(force_update)
            
            # Validação rigorosa dos dados
            if not _validate_matches(matches):
                raise ValueError("Dados inválidos do scraper")
            
            # Caso sem partidas
            if not matches:
                await status_msg.edit_text("📅 Nenhuma partida agendada")
                storage.clear_matches()
                return

            # Processamento bem-sucedido
            store_matches(matches)
            await send_matches_list(status_msg, matches)

        except Exception as e:
            logger.error(f"Erro no handler: {str(e)}", exc_info=True)
            await handle_scrape_error(status_msg)

    except Exception as e:
        logger.error(f"Erro crítico: {str(e)}", exc_info=True)
        await send_fallback(update)

def _validate_matches(matches):
    """Valida a estrutura dos dados das partidas"""
    required_keys = ['opponent', 'event', 'time', 'format', 'link']
    return all(
        all(key in match for key in required_keys) and
        isinstance(match['time'], str) and
        len(match['opponent']) > 2
        for match in matches
    )

def store_matches(matches):
    """Armazena partidas com validação de tempo"""
    try:
        storage.clear_matches()
        valid_matches = []
        
        for match in matches:
            try:
                # Gera ID único baseado no tempo e adversário
                match_time = datetime.strptime(match['time'], "%d/%m/%Y %H:%M")
                if match_time < datetime.now():
                    continue
                    
                match_id = hashlib.md5(
                    f"{match_time.timestamp()}_{match['opponent']}".encode()
                ).hexdigest()
                
                valid_matches.append({
                    'id': match_id,
                    'opponent': match['opponent'],
                    'event': match['event'],
                    'time': match['time'],
                    'format': match['format'],
                    'link': match['link'],
                    'notified': False
                })
                
            except ValueError as e:
                logger.warning(f"Partida inválida: {str(e)}")
        
        if valid_matches:
            storage.add_matches(valid_matches)
            
    except Exception as e:
        logger.error(f"Erro no armazenamento: {str(e)}")
        storage.clear_matches()

async def send_matches_list(status_msg, matches):
    """Envia a lista formatada de partidas"""
    message = "<b>🔴 Próximas Partidas da FURIA:</b>\n\n"
    
    for idx, match in enumerate(matches, 1):
        message += (
            f"🏁 <b>Partida {idx}</b>\n"
            f"🆚 Adversário: <b>{match['opponent']}</b>\n"
            f"📅 Data: <code>{match['time']}</code>\n"
            f"🏆 Evento: {match['event']}\n"
            f"⚙ Formato: {match['format']}\n"
            f"🔗 Detalhes: {match['link']}\n\n"
        )
    
    message += "\n🔄 Atualizado em: " + datetime.now().strftime("%d/%m/%Y %H:%M")
    
    await status_msg.edit_text(
        text=message,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔔 Ativar Notificações", callback_data="sub_on"),
            InlineKeyboardButton("🔕 Desativar", callback_data="sub_off")
        ]])
    )

async def handle_scrape_error(status_msg):
    """Lida com erros de scraping"""
    cached_matches = storage.get_matches()
    
    if cached_matches:
        await status_msg.edit_text(
            "⚠️ Dados possivelmente desatualizados:\n\n" +
            "\n".join(f"• {m['opponent']} - {m['time']}" for m in cached_matches) +
            "\n\nUse /matches force para atualizar",
            parse_mode="HTML"
        )
    else:
        await status_msg.edit_text(
            "❌ Falha na conexão. Tente:\n"
            "1. /matches force - Forçar atualização\n"
            "2. Verifique @furiaesports\n"
            "3. Tente novamente mais tarde"
        )

async def handle_notification_callback(update: Update, context: CallbackContext):
    """Gerencia inscrições em notificações"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = query.from_user.id
        action = query.data
        
        if action == "sub_on":
            storage.add_subscription(user_id)
            msg = "✅ Você receberá notificações 1h antes das partidas!"
        elif action == "sub_off":
            storage.remove_subscription(user_id)
            msg = "🔕 Notificações desativadas com sucesso"
        else:
            msg = "⚠️ Comando inválido"
            
        await query.edit_message_text(text=msg, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Erro na callback: {str(e)}")
        await query.edit_message_text(text="⚠️ Erro no processamento")

async def check_and_notify(context: ContextTypes.DEFAULT_TYPE):
    """Verifica partidas pendentes periodicamente"""
    try:
        now = datetime.now()
        matches = storage.get_matches()
        
        for match in matches:
            if not match['notified']:
                try:
                    match_time = datetime.strptime(match['time'], "%d/%m/%Y %H:%M")
                    if (match_time - timedelta(hours=1)) <= now < match_time:
                        await send_notification(context.bot, match)
                        storage.update_match_status(match['id'], True)
                except Exception as e:
                    logger.error(f"Erro na notificação: {str(e)}")
                    
    except Exception as e:
        logger.error(f"Erro no job: {str(e)}")
        context.job_queue.run_once(check_and_notify, 300)  # Tenta novamente em 5 min

async def send_notification(bot, match):
    """Envia notificação para usuários inscritos"""
    message = (
        f"⏰ <b>Notificação de Partida!</b>\n\n"
        f"A partida contra {match['opponent']} começa em 1 hora!\n\n"
        f"🏆 {match['event']}\n"
        f"⏰ {match['time']}\n"
        f"🔗 {match['link']}"
    )
    
    for user_id in storage.get_subscriptions():
        try:
            await bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.warning(f"Falha na notificação para {user_id}: {str(e)}")
            storage.remove_subscription(user_id)

async def send_fallback(update: Update):
    """Mensagem de fallback genérica"""
    await update.message.reply_text(
        "⚠️ Serviço temporariamente indisponível\n\n"
        "Consulte:\n"
        "• Site: https://draft5.gg\n"
        "• Twitter: @furiaesports\n"
        "• Instagram: @furia\n\n"
        "Tente novamente mais tarde!",
        parse_mode="HTML",
        disable_web_page_preview=True
    )