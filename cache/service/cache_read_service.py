import os
import io
import env.hassan_env as hassan_env

# 로컬 캐시에 디시콘 있으면 버퍼와 파일명 반환
def find_dccon(package_name, idx):

    if hassan_env.CACHE_MAX == 0:                                                                                              # 캐시 사용하지 않는 경우
        return

    cache_file_name = _find_cache_from_file(package_name, idx)

    if not cache_file_name == '':
        cache_file_path = os.path.join(hassan_env.CACHE_PATH, cache_file_name)
        buffer=''

        if not os.path.exists(cache_file_path):                                                                     # 캐시 파일이 존재하지 않는 경우
            return

        with open(cache_file_path, 'rb') as fin:
            buffer = io.BytesIO(fin.read())

        return [buffer, cache_file_name]

# 캐시 파일 찾기
# 디시콘 패키지명과 idx(디시콘명)으로 탐색해서, 있으면 파일명 반환
def _find_cache_from_file(package_name, idx):
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