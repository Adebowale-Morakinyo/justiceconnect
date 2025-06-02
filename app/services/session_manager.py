# app/services/session_manager.py
from datetime import datetime


class SessionManager:
    def __init__(self):
        self.sessions = {}  # {phone: {state: str, data: dict, timestamp: datetime}}
        self.SESSION_TIMEOUT = 1800  # 30 minutes

    def get_session(self, phone):
        self._cleanup_expired()
        return self.sessions.get(phone, {"state": "NEW", "data": {}})

    def update_session(self, phone, state, data=None):
        self.sessions[phone] = {
            "state": state,
            "data": data or {},
            "timestamp": datetime.now(),
        }

    def _cleanup_expired(self):
        now = datetime.now()
        expired = [
            phone
            for phone, sess in self.sessions.items()
            if (now - sess["timestamp"]).seconds > self.SESSION_TIMEOUT
        ]
        for phone in expired:
            del self.sessions[phone]
