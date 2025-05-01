import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class JSONStorage:
    def __init__(self, file_path='data/storage.json'):
        self.file_path = file_path
        self._ensure_data_file()

    def _ensure_data_file(self):
        """Cria o arquivo e diretório se não existirem"""
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump({
                    'matches': [],
                    'subscriptions': []
                }, f)

    def _read_data(self):
        """Lê todos os dados do arquivo"""
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def _write_data(self, data):
        """Escreve dados no arquivo"""
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)

    # Métodos para matches
    def add_match(self, match):
        data = self._read_data()
        if not any(m['id'] == match['id'] for m in data['matches']):
            data['matches'].append(match)
            self._write_data(data)

    def get_matches(self):
        return self._read_data()['matches']

    def clear_matches(self):
        data = self._read_data()
        data['matches'] = []
        self._write_data(data)

    # Métodos para subscriptions
    def add_subscription(self, user_id):
        data = self._read_data()
        if user_id not in data['subscriptions']:
            data['subscriptions'].append(user_id)
            self._write_data(data)

    def remove_subscription(self, user_id):
        data = self._read_data()
        if user_id in data['subscriptions']:
            data['subscriptions'].remove(user_id)
            self._write_data(data)

    def get_subscriptions(self):
        return self._read_data()['subscriptions']

    def clear_subscriptions(self):
        data = self._read_data()
        data['subscriptions'] = []
        self._write_data(data)

    def clear_all(self):
        """Limpa todos os dados do storage"""
        data = self._read_data()
        data['matches'] = []
        data['subscriptions'] = []
        self._write_data(data)