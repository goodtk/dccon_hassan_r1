import os
from util.directory import create_directory
from log.logger import system_log

# 캐시 추가
def add_cache(package_name, idx, file_name, bytes, cache_path, cache_max):
    if cache_max == 0:
        return

    if not os.path.isdir(cache_path):
        if not create_directory(cache_path):                                        # 캐시 폴더가 존재하지 않으면 생성. 생성 실패시 오류메시지 출력.
            system_log('creating cache directory failed')

    # 캐시 개수 체크
    if _get_count_of_cache(cache_path) >= cache_max:
        _remove_latest_cache(cache_path)

    # 이미지 저장
    with open(cache_path + f'{file_name}','wb') as out: ## Open temporary file as bytes
        out.write(bytes.read())                         ## Read bytes into file

    # 캐시 인덱스에 append
    # 캐시 인덱스에 중복추가안하게 해라
    file_path = cache_path + 'cacheIdx.txt'
    file = open(file_path, mode='at', encoding='utf-8')
    file.write(package_name + '\t' + idx + '\t' + file_name + '\n')
    file.close()

# 캐시 개수 조회
def _get_count_of_cache(cache_path):
    file_path = cache_path + 'cacheIdx.txt'

    if not os.path.exists(file_path):                  # 캐시 인덱스 파일이 존재하지 않으면 0 반환
        return 0

    file = open(file_path, mode='rt', encoding='utf-8')
    count = len(file.readlines())
    file.close()

    return count

# 캐시 리스트에서 한줄 삭제 + 이미지 삭제
def _remove_latest_cache(cache_path):
    file_path = cache_path + 'cacheIdx.txt'
    file = open(file_path, mode='rt', encoding='utf-8')

    # 헤드(가장 오래된 캐시) 탐색
    lastest_cache = file.readline()
    splited = lastest_cache.split('\t')
    lastest_cache_path = cache_path + splited[2].rstrip('\n')
    
    # 나머지줄 로드
    lines = file.readlines()

    new_lines = ''
    isExist = False;

    for line in lines:
        new_lines += line

    file.close()

    # 나머지줄만 저장
    file = open(file_path, mode='wt', encoding='utf-8')
    file.writelines(new_lines)
    file.close()

    # 가장 오래된 캐시 삭제
    if os.path.exists(lastest_cache_path):
        os.remove(lastest_cache_path)