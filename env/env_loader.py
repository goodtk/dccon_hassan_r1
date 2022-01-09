import os
from dotenv import load_dotenv
from env import hassan_env

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))

def load_env():
    load_dotenv()  # load bot token

    _load_dcinside_env()
    _load_discord_env()
    _load_favorite_env()
    _load_cache_env()

def _load_dcinside_env():
    hassan_env.DCCON_HOME_URL = 'https://dccon.dcinside.com/'
    hassan_env.DCCON_SEARCH_URL = 'https://dccon.dcinside.com/hot/1/title/'
    hassan_env.DCCON_DETAILS_URL = 'https://dccon.dcinside.com/index/package_detail'

def _load_discord_env():
    hassan_env.BOT_TOKEN = os.getenv('BOT_TOKEN')
    hassan_env.EMBED_COLOR = 0x4559e9
    hassan_env.INVITE_URL = 'https://discordapp.com/oauth2/authorize?client_id=629279090716966932&scope=bot&permissions=101376'
    hassan_env.OWNER_ID = os.getenv('OWNER_ID')
    hassan_env.CMD_AUTODEL_CHANNEL_PATH = os.path.join(ROOT_DIR, '.concmdAutodelChannel')
    hassan_env.MSG_MAX_LENGTH = 2000

def _load_favorite_env():
    hassan_env.FAVORITE_PATH = os.path.join(ROOT_DIR, '.favorites')
    hassan_env.FAVORITE_MAX = int(os.getenv('FAVORITE_MAX'))

def _load_cache_env():
    hassan_env.CACHE_PATH = os.path.join(ROOT_DIR, '.cache')
    hassan_env.CACHE_MAX = int(os.getenv('CACHE_MAX'))