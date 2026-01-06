import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///csesa.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email (SMTP)
    MAIL_EMAIL = os.getenv('MAIL_EMAIL')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    # Razorpay (test mode by default)
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')

    # Admin credentials (env or DB)
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@csesa.in')
    # Prefer hashed password via Werkzeug (pbkdf2:sha256)
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH')
    # Fallback plaintext for local dev only
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
