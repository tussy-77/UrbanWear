from backend.database import db
from datetime import datetime

class Address(db.Model):
    __tablename__ = 'addresses'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    city       = db.Column(db.String(100), nullable=False)
    address    = db.Column(db.String(255), nullable=False)
    extra      = db.Column(db.String(255), nullable=True)
    barrio     = db.Column(db.String(100), nullable=True)
    receiver   = db.Column(db.String(100), nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':         self.id,
            'department': self.department,
            'city':       self.city,
            'address':    self.address,
            'extra':      self.extra or '',
            'barrio':     self.barrio or '',
            'receiver':   self.receiver or '',
            'is_default': self.is_default,
        }