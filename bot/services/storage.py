import json
import os
from typing import List, Dict
from datetime import datetime

class JSONStorage:
    def __init__(self, file_path: str = "data/storage.json"):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {'matches': [], 'subscriptions': {}}

    def save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add_matches(self, matches: List[Dict]):
        self.data['matches'] = matches
        self.save()

    def get_matches(self) -> List[Dict]:
        return self.data.get('matches', [])

    def clear_matches(self):
        self.data['matches'] = []
        self.save()

    def add_subscription(self, user_id: int, match_id: str):
        subs = self.data['subscriptions']
        user_subs = subs.get(str(user_id), [])
        if match_id not in user_subs:
            user_subs.append(match_id)
            subs[str(user_id)] = user_subs
            self.save()

    def remove_subscription(self, user_id: int, match_id: str):
        subs = self.data['subscriptions']
        user_subs = subs.get(str(user_id), [])
        if match_id in user_subs:
            user_subs.remove(match_id)
            self.save()

    def get_subscriptions(self) -> Dict[str, List[str]]:
        return self.data.get('subscriptions', {})

    def update_match_status(self, match_id: str, notified: bool):
        for match in self.data['matches']:
            if match['id'] == match_id:
                match['notified'] = notified
        self.save()