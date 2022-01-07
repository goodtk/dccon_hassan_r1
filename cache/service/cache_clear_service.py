import os
import shutil
import env.hassan_env as hassan_env

from log.logger import system_log

# 캐시 클리어
def clear_cache(user_id, owner_id):

    if not (owner_id == user_id):
        system_log(f'{user_id} attempted to clear cache.')
        return '권한이 없습니다. 관리자에게 문의하세요.'

    if os.path.isdir(hassan_env.CACHE_PATH) and not os.path.islink(hassan_env.CACHE_PATH):
        shutil.rmtree(hassan_env.CACHE_PATH)
        system_log(f'cache cleared by shutil.rmtree({hassan_env.CACHE_PATH})')
    elif os.path.exists(hassan_env.CACHE_PATH):
        os.remove(hassan_env.CACHE_PATH)
        system_log(f'cache cleared by os.remove({hassan_env.CACHE_PATH})')

    return '캐시를 정리했습니다.'
