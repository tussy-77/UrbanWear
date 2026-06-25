import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY no está definida en las variables de entorno")
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY no está definida en las variables de entorno")
