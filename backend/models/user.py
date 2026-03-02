from backend.database import db
from sqlalchemy import Enum
import enum


class UserRole(enum.Enum):
    admin = "admin"
    customer = "customer"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(
        Enum(UserRole, name="user_role"),
        default=UserRole.customer,
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "created_at": self.created_at
        }