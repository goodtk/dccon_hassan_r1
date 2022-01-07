import os
import env.hassan_env as hassan_env
from logger.logger import log

# 즐겨찾기 검색
def search_favorite(ctx, keyword):
    log(ctx, 'search_favorite command')

    author_id = str(ctx.author.id)
    file_path = os.path.join(hassan_env.FAVORITE_PATH, author_id) + '.txt'

    if not os.path.exists(file_path):
        return '<@' + author_id + '>님의 즐겨찾기 목록이 존재하지 않습니다.'

    file = open(file_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    file.close()

    search_results = ''

    cnt = 0

    for line in lines:
        splited = line.split('\t')
        if keyword in splited[0]:
            cnt += 1
            search_results += str(cnt) + '\t"' + splited[0] + '" "' + splited[1] + '" "' + splited[2].rstrip() + '"\n'

    if not search_results == '':
        log(ctx, f'search_favorite {keyword} searched successfully')

        return ctx.author.name + f'님의 단축어 "{keyword}" 검색 결과 ({cnt}/{len(lines)}) \n'+ search_results
    else:
        log(ctx, f'search_favorite {keyword} not found')
        return ctx.author.name + f'님의 단축어 "{keyword}" 검색 결과가 없습니다.'