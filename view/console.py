import env.hassan_env as hassan_env
from logger.logger import system_log

def print_on_ready():
    system_log('Bot ready')
    system_log(f'BOT_TOKEN : {hassan_env.BOT_TOKEN}')
    system_log(f'OWNER_ID : {hassan_env.OWNER_ID}')
    system_log(f'FAVORITE_PATH : {hassan_env.FAVORITE_PATH}')
    system_log(f'FAVORITE_MAX : {hassan_env.FAVORITE_MAX}')
    system_log(f'CACHE_PATH : {hassan_env.CACHE_PATH}')
    system_log(f'CACHE_MAX : {hassan_env.CACHE_MAX}')
    system_log(f'CONCMD_AUTODEL_CHANNEL_PATH : {hassan_env.CMD_AUTODEL_CHANNEL_PATH}')