import easy_env
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())

USERBOT_NAME = easy_env.get('USERBOT_NAME', 'userbot')
REDIS_URL = easy_env.get_str('REDIS_URL')
API_ID = easy_env.get_int('API_ID', raise_error=True)
API_HASH = easy_env.get('API_HASH', raise_error=True)

USER_PHONE = easy_env.get('USER_PHONE')
USER_PASSWORD = easy_env.get('USER_PASSWORD')

NOU_LIST = easy_env.get_list('NOU_LIST', ['baka'], separator='|')
