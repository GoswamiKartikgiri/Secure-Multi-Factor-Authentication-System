import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MySQL compatibility
pymysql.install_as_MySQLdb()


class Config:

    # =====================================
    # Flask Configuration
    # =====================================

    SECRET_KEY = os.getenv("SECRET_KEY")

    # =====================================
    # Database Configuration
    # =====================================

    SQLALCHEMY_DATABASE_URI = (
        f"mysql://{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}/"
        f"{os.getenv('DB_NAME')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =====================================
    # Flask-Mail Configuration
    # =====================================

    MAIL_SERVER = os.getenv("MAIL_SERVER")

    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))

    MAIL_USE_TLS = True

    MAIL_USE_SSL = False

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")

    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")

    MAIL_MAX_EMAILS = None

    MAIL_ASCII_ATTACHMENTS = False