import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class JSONStorage:
    def __init__(self, file_path=None):
        self.file_path = file_path or os.path.join(Path(__file__).parent.parent, 'data', 'storage.json')
        self._ensure_data_file()

    def _ensure_data_file(self):
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            if not os.path.exists(self.file_path):
                with open(self.file_path, 'w') as f:
                    json.dump({'matches': [], 'subscriptions': []}, f)
        except Exception as e:
            logger.error(f"Falha ao criar arquivo: {str(e)}")
            raise

    def _read_data(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro na leitura: {str(e)}")
            return {'matches': [], 'subscriptions': []}

    def _write_data(self, data):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Erro na escrita: {str(e)}")
            raise

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