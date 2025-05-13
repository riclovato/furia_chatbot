import logging
from datetime import datetime, timedelta
from telegram import Bot
from .storage import JSONStorage

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, bot_token: str):
        self.bot = Bot(token=bot_token)
        self.storage = JSONStorage()

    async def check_and_notify(self, context):
        """Job principal para verificar notificações"""
        try:
            matches = self.storage.get_matches()
            subscriptions = self.storage.get_subscriptions()
            now = datetime.now()

            for match in matches:
                if self._should_skip_match(match):
                    continue

                try:
                    await self._process_match(match, subscriptions, now)
                except Exception as e:
                    logger.error(f"Erro na partida {match.get('id')}: {str(e)}")

        except Exception as e:
            logger.error(f"Erro geral: {str(e)}")

    def _should_skip_match(self, match):
        return (
            match.get('time') == "TBA" or 
            match.get('notified', False) or
            not match.get('time')
        )

    async def _process_match(self, match, subscriptions, now):
        match_time = datetime.strptime(match['time'], "%Y-%m-%d %H:%M")
        notify_time = match_time - timedelta(hours=1)

        if notify_time <= now < match_time:
            await self._send_notifications(match, subscriptions)
            self.storage.update_match_status(match['id'], True)

    async def _send_notifications(self, match, subscriptions):
        message = self._build_message(match)
        for user_id_str, match_ids in subscriptions.items():
            if match['id'] in match_ids:
                await self._notify_user(user_id_str, message)

    def _build_message(self, match):
        return (
            "⏰ **Notificação de Partida!**\n\n"
            f"🆚 Adversário: {match['opponent']}\n"
            f"🏆 Evento: {match['event']}\n"
            f"⏰ Horário: {match['time']}\n"
            f"🔗 Detalhes: {match['link']}"
        )

    async def _notify_user(self, user_id_str, message):
        try:
            await self.bot.send_message(
                chat_id=int(user_id_str),
                text=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Erro ao notificar {user_id_str}: {str(e)}")