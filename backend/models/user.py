from backend.database import db
from sqlalchemy import Enum
import enum
from flask_bcrypt import generate_password_hash, check_password_hash 


class UserRole(enum.Enum):
    admin = "admin"
    customer = "customer"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(Enum(UserRole, name="user_role"), default=UserRole.customer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    last_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    document = db.Column(db.String(30), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)

    # Método para encriptar la contraseña antes de guardarla
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    
    # Método para verificar si la contraseña ingresada es correcta
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "created_at": self.created_at,
            'last_name': self.last_name or '',
            'phone': self.phone or '',
            'document': self.document or '',
            'gender': self.gender or '',
            'birth_date': str(self.birth_date) if self.birth_date else '',
        }