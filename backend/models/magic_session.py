from backend.database import db
from datetime import datetime


class MagicLoginSession(db.Model):
    __tablename__ = 'magic_login_sessions'

    id = db.Column(db.Integer, primary_key=True)
    session_token = db.Column(db.String(64), nullable=False, unique=True, index=True)
    email = db.Column(db.String(150), nullable=False)
    access_token = db.Column(db.Text, nullable=True)
    user_name = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
