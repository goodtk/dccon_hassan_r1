import os
import env.hassan_env as hassan_env

# 캐시 탐색
# 디시콘 패키지명과 idx(디시콘명)으로 탐색해서, 있으면 파일명 반환
def get_cache_file_name(package_name, idx):
    cache_idx_path = os.path.join(hassan_env.CACHE_PATH, 'cacheIdx.txt')

    cache_file_name = ''

    if not os.path.isdir(hassan_env.CACHE_PATH):
        return cache_file_name
    
    if not os.path.isfile(cache_idx_path):
        return cache_file_name

    file = open(cache_idx_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        splited = line.split('\t')
        if (package_name == splited[0]) and (idx == splited[1]):
            cache_file_name = splited[2].rstrip('\n')                   # 반환할 디시콘 파일명
            break
    file.close()

    cache_path = os.path.join(hassan_env.CACHE_PATH, cache_file_name)
    if not os.path.exists(cache_path):               # 캐시 이미지가 실제로 존재하지 않으면
        cache_file_name = ''

    return cache_file_name