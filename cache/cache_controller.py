import env.hassan_env as hassan_env
from .service import cache_add_service, cache_read_service, cache_clear_service


def clear_cache(user_id, owner_id):
    return cache_clear_service.clear_cache(user_id, owner_id, hassan_env.CACHE_PATH)

async def add_cache(package_name, idx, file_name, bytes):
    cache_add_service.add_cache(package_name, idx, file_name, bytes, hassan_env.CACHE_PATH, hassan_env.CACHE_MAX)

def read_cache(package_name, idx):
    return cache_read_service.get_cache_file_name(package_name, idx, hassan_env.CACHE_PATH)