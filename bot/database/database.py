import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_name='furia_bot.db'):
        self.conn = sqlite3.connect(db_name)
        self._create_tables()

    def _create_tables(self):
        """Cria as tabelas necessárias"""
        cursor = self.conn.cursor()
        
        # Tabela de partidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id TEXT PRIMARY KEY,
                opponent TEXT NOT NULL,
                event TEXT NOT NULL,
                match_time DATETIME NOT NULL,
                notified BOOLEAN DEFAULT 0
            )
        ''')
        
        # Tabela de inscrições
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER PRIMARY KEY,
                notification_time INTEGER DEFAULT 30
            )
        ''')
        
        self.conn.commit()

    def add_match(self, match):
        """Adiciona uma nova partida ao banco de dados"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO matches 
                (id, opponent, event, match_time)
                VALUES (?, ?, ?, ?)
            ''', (
                f"{match['time']}_{match['opponent']}",
                match['opponent'],
                match['event'],
                match['time']
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Erro ao adicionar partida: {e}")

    def get_upcoming_matches(self):
        """Retorna partidas não notificadas"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM matches 
            WHERE notified = 0 
            AND match_time > datetime('now')
        ''')
        return cursor.fetchall()

    def mark_as_notified(self, match_id):
        """Marca partida como notificada"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE matches 
            SET notified = 1 
            WHERE id = ?
        ''', (match_id,))
        self.conn.commit()

    def add_subscription(self, user_id, minutes=30):
        """Adiciona/atualiza uma inscrição"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO subscriptions 
            (user_id, notification_time) 
            VALUES (?, ?)
        ''', (user_id, minutes))
        self.conn.commit()

    def get_subscriptions(self):
        """Retorna todas as inscrições"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM subscriptions')
        return cursor.fetchall()

    def close(self):
        self.conn.close()