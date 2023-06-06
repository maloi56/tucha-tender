import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__name__))
load_dotenv(os.path.join(basedir, '.env'))

POSTS_PER_PAGE = 5
class base_config(object):
    """Default configuration options."""
    SITE_NAME = os.environ.get('APP_NAME', 'tenders')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secrets')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI',
                                             'postgresql+psycopg2://postgres:MASTERKEY@localhost/tender')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASS = os.environ.get('POSTGRES_PASS', 'MASTERKEY')
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'tender')

    ADMIN_LOGIN = os.environ.get('ADMIN_LOGIN', 'admin')
    ADMIN_PASS = os.environ.get('ADMIN_PASS', 'admin')

    SQLALCHEMY_DATABASE_URI = 'postgresql://%s:%s@%s:%s/%s' % (
        POSTGRES_USER,
        POSTGRES_PASS,
        POSTGRES_HOST,
        POSTGRES_PORT,
        POSTGRES_DB
    )
    JSON_AS_ASCII = False
    BOOTSTRAP_BOOTSWATCH_THEME = 'Zephyr'


class dev_config(base_config):
    """Development configuration options."""
    ASSETS_DEBUG = True
    WTF_CSRF_ENABLED = False
    DEBUG = True


class test_config(base_config):
    """Testing configuration options."""
    TESTING = True
    WTF_CSRF_ENABLED = False
