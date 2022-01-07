import os

# 캐시 탐색
# 디시콘 패키지명과 idx(디시콘명)으로 탐색해서, 있으면 파일명 반환
def get_cache_file_name(package_name, idx, cache_path):
    file_path = cache_path + 'cacheIdx.txt'

    cache_file_name = ''

    if not os.path.isdir(cache_path):
        return cache_file_name

    file = open(file_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        splited = line.split('\t')
        if (package_name == splited[0]) and (idx == splited[1]):
            cache_file_name = splited[2].rstrip('\n')                   # 반환할 디시콘 파일명
            break
    file.close()

    if not os.path.exists(cache_path + cache_file_name):               # 캐시 이미지가 실제로 존재하지 않으면
        cache_file_name

    return cache_file_name