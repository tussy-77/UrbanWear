import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Si DATABASE_URL no existe o es PostgreSQL sin conexión, usa SQLite para desarrollo
    db_url = os.getenv("DATABASE_URL", "").strip()
    if not db_url or db_url.startswith("postgresql"):
        SQLALCHEMY_DATABASE_URI = "sqlite:///urbanwear.db"
    else:
        SQLALCHEMY_DATABASE_URI = db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
