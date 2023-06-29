import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__name__))
load_dotenv(os.path.join(basedir, '.env'))

token = os.environ.get('TOKEN', 'SECRET')
tg_admin_id = os.environ.get('ADMIN_ID', 'SECRET')
tg_chat_id = os.environ.get('CHAT_ID', '@tuchatenderbot')