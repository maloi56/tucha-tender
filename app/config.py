import os


class base_config(object):
    """Default configuration options."""
    SITE_NAME = os.environ.get('APP_NAME', 'tenders')

    SECRET_KEY = os.environ.get('SECRET_KEY', '7e05aef5e3609333d0ac992767e26bfcf88cdd87')  # testing
    JSON_AS_ASCII = False
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:MASTERKEY@localhost/tender'


class dev_config(base_config):
    """Development configuration options."""
    ASSETS_DEBUG = True
    WTF_CSRF_ENABLED = False


class test_config(base_config):
    """Testing configuration options."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    DEBUG = True
