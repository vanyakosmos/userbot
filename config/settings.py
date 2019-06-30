import os
import re

import easy_env
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

DEBUG = easy_env.get_bool('DEBUG', default=False)
USERBOT_NAME = easy_env.get('USERBOT_NAME', 'userbot')
REDIS_URL = easy_env.get_str('REDIS_URL')
API_ID = easy_env.get_int('API_ID', raise_error=True)
API_HASH = easy_env.get('API_HASH', raise_error=True)

USER_PHONE = easy_env.get('USER_PHONE')
USER_PASSWORD = easy_env.get('USER_PASSWORD')

NOU_LIST = easy_env.get_list('NOU_LIST', ['baka', 'idiot'], separator='|')
NOT_PATTERN = "|".join([f"\\b{w}\\b" for w in NOU_LIST])
NOT_PATTERN = f'.*({NOT_PATTERN}).*'
NOU_LIST_REGEX = re.compile(NOT_PATTERN, re.IGNORECASE)

NAME = easy_env.get('NAME', 'dude')
LOGS_FILE_PATH = easy_env.get('LOGS_FILE_PATH', 'logs.txt')
LOGS_FILE_DIR = os.path.split(LOGS_FILE_PATH)[0]
if LOGS_FILE_DIR:
    os.makedirs(LOGS_FILE_DIR, exist_ok=True)

LOGGING_LEVEL = easy_env.get('LOGGING_LEVEL', 'DEBUG')
LOGGING_LEVEL_ROOT = easy_env.get('LOGGING_LEVEL_ROOT', 'INFO')

MASTER_KEY = easy_env.get('MASTER_KEY', 'key')
PORT = easy_env.get('PORT', 5000)
