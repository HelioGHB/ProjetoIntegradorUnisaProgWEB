"""SQLite local por padrão; PostgreSQL apenas quando publicado."""
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv


class Config:
    def __init__(self):
        if os.getenv('APP_ENV') != 'production':
            load_dotenv(Path(__file__).with_name('.env.local'), override=False)
        self.APP_ENV = os.getenv('APP_ENV', 'development')
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        if self.APP_ENV != 'production' and not self.SECRET_KEY:
            self.SECRET_KEY = secrets.token_hex(32)
        self.SQLALCHEMY_DATABASE_URI = (
            os.getenv('DATABASE_URL') if self.APP_ENV == 'production'
            else 'sqlite:///sigetec.sqlite3'
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SQLALCHEMY_ENGINE_OPTIONS = {'hide_parameters': True, 'pool_pre_ping': True}
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SAMESITE = 'Lax'
        self.SESSION_COOKIE_SECURE = self.APP_ENV == 'production'
        self.MAX_CONTENT_LENGTH = 64 * 1024
        self.DEMO_MODE = os.getenv('DEMO_MODE', 'false').lower() == 'true'

        self.INIT_DB_ON_START = os.getenv('INIT_DB_ON_START', 'false').lower() == 'true'
        self.CREATE_ADMIN_ON_START = os.getenv('CREATE_ADMIN_ON_START', 'false').lower() == 'true'
        self.BOOTSTRAP_ADMIN_NAME = os.getenv('BOOTSTRAP_ADMIN_NAME')
        self.BOOTSTRAP_ADMIN_EMAIL = os.getenv('BOOTSTRAP_ADMIN_EMAIL')
        self.BOOTSTRAP_ADMIN_PASSWORD = os.getenv('BOOTSTRAP_ADMIN_PASSWORD')
