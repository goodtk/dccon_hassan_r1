import os
import env.hassan_env as hassan_env
from logger.logger import log, system_log
from util.file_util import get_file_line_cnt

# 즐겨찾기 추가
def add_favorite(ctx, keyword, package_name, dccon_name):
    log(ctx, 'add_favorite command')

    file_path =  os.path.join(hassan_env.FAVORITE_PATH, str(ctx.author.id) + '.txt')

    registed_count = get_file_line_cnt(file_path)
    author_id = str(ctx.author.id)

    if registed_count >= hassan_env.FAVORITE_MAX:                                          # 즐겨찾기 추가횟수 체크
        log(ctx, 'delete_favorite cannot register favorite (max)')
        return '더 이상 즐겨찾기를 추가할 수 없습니다. 즐겨찾기 삭제 후 시도해주세요.'
    elif registed_count > 0 and is_exactly_same_exist(author_id, keyword):     # 해당 단축어가 이미 추가되어있는지 체크
        log(ctx, f'delete_favorite "{keyword}" already exists.')
        return keyword + ' 단축어으로 등록된 즐겨찾기가 이미 존재합니다.'

    file = open(file_path, mode='at', encoding='utf-8')
    file.write(keyword + '\t' + package_name + '\t' + dccon_name + '\n')
    file.close()

    log(ctx, f'add_favorite {keyword} is saved to {file_path}.')
    return '<@' + author_id + f'>님의 즐겨찾기가 추가되었습니다. ({registed_count + 1}/{hassan_env.FAVORITE_MAX})'

# 추가 시 중복 체크
def is_exactly_same_exist(author_id, keyword):
    file_path = os.path.join(hassan_env.FAVORITE_PATH, str(author_id) + '.txt')

    exist = False

    file = open(file_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        splited = line.split('\t')
        if splited[0] == keyword:
            system_log(f'add_favorite {keyword} of {author_id} is already exists.')
            exist = True
            break
    file.close()

    return exist