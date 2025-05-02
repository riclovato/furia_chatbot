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
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump({'matches': [], 'subscriptions': []}, f)

    def _read_data(self):
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def _write_data(self, data):
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)

    # Métodos de matches
    def add_matches(self, matches):
        data = self._read_data()
        data['matches'] = matches
        self._write_data(data)

    def get_matches(self):
        return self._read_data()['matches']

    def clear_matches(self):
        data = self._read_data()
        data['matches'] = []
        self._write_data(data)

    # Métodos de subscriptions
    def add_subscription(self, user_id):
        data = self._read_data()
        if user_id not in data['subscriptions']:
            data['subscriptions'].append(user_id)
            self._write_data(data)
            logger.info(f"Usuário {user_id} inscrito")

    def remove_subscription(self, user_id):
        data = self._read_data()
        if user_id in data['subscriptions']:
            data['subscriptions'].remove(user_id)
            self._write_data(data)
            logger.info(f"Usuário {user_id} removido")

    def get_subscriptions(self):
        return self._read_data()['subscriptions']

    def update_match_status(self, match_id, status):
        data = self._read_data()
        for match in data['matches']:
            if match['id'] == match_id:
                match['notified'] = status
        self._write_data(data)