from telegram import Bot
from datetime import datetime, timedelta
import logging
from database.database import DatabaseManager

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, bot_token):
        self.bot = Bot(token=bot_token)
        self.db = DatabaseManager()

    def check_and_notify(self):
        """Verifica e envia notificações"""
        try:
            matches = self.db.get_upcoming_matches()
            for match in matches:
                match_id, opponent, event, match_time, _ = match
                notify_time = datetime.strptime(match_time, '%Y-%m-%d %H:%M:%S') - timedelta(minutes=30)
                
                if datetime.now() >= notify_time:
                    self._send_notifications(match_id, opponent, event, match_time)
                    self.db.mark_as_notified(match_id)
        except Exception as e:
            logger.error(f"Erro na verificação de notificações: {e}")

    def _send_notifications(self, match_id, opponent, event, match_time):
        """Envia notificações para usuários inscritos"""
        subscribers = self.db.get_subscriptions()
        message = (
            f"⚡️ **Partida da FURIA se aproxima!** ⚡️\n\n"
            f"🆚 **Adversário:** {opponent}\n"
            f"🏆 **Evento:** {event}\n"
            f"⏰ **Horário:** {match_time}"
        )
        
        for user in subscribers:
            try:
                self.bot.send_message(
                    chat_id=user[0],
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Erro ao enviar notificação para {user[0]}: {e}")

    def cleanup_old_matches(self):
        """Limpa partidas antigas"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                DELETE FROM matches 
                WHERE match_time < datetime('now', '-1 day')
            ''')
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"Erro na limpeza de partidas: {e}")