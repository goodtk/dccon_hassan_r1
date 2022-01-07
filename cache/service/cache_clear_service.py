import os
import shutil

from log.logger import system_log

# 캐시 클리어
def clear_cache(user_id, owner_id, cache_path):

    if not (owner_id == user_id):
        system_log(f'{user_id} attempted to clear cache.')
        return '권한이 없습니다. 관리자에게 문의하세요.'

    if os.path.isdir(cache_path) and not os.path.islink(cache_path):
        shutil.rmtree(cache_path)
        system_log(f'cache cleared by shutil.rmtree({cache_path})')
    elif os.path.exists(cache_path):
        os.remove(cache_path)
        system_log(f'cache cleared by os.remove({cache_path})')

    return '캐시를 정리했습니다.'
