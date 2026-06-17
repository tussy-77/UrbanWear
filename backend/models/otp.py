from backend.database import db
from datetime import datetime


class PendingOTPCode(db.Model):
    __tablename__ = 'pending_otp_codes'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
