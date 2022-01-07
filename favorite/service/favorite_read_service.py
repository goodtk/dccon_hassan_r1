import os
import env.hassan_env as hassan_env
from logger.logger import log
from util.file_util import get_file_line_cnt
from error.favorite_error import FavoriteError

# 즐겨찾기 사용
def find_favorite_one(ctx, shortcut_name):
    log(ctx, 'send_favorite command')

    author_id = str(ctx.author.id)

    file_path = os.path.join(hassan_env.FAVORITE_PATH, author_id) + '.txt'
    if not os.path.exists(file_path):
        raise FavoriteError('<@' + author_id + '>님의 즐겨찾기 목록이 존재하지 않습니다.')

    dccon = _find_matches_from_file(ctx, shortcut_name)
    if dccon[0] == '':
        log(ctx, f'send_favorite "{shortcut_name}" cannot found')
        raise FavoriteError('<@' + author_id + f'>님의 즐겨찾기 목록에서 "{shortcut_name}" 단축어를 찾을 수 없습니다.')

    return dccon


# 즐겨찾기 단축어로 탐색
# 패키지명과 디시콘명 가져오기. 단축어와 근접한 디시콘명 가져옴
def _find_matches_from_file(ctx, shortcut_name):
    file_path = os.path.join(hassan_env.FAVORITE_PATH, str(ctx.author.id)) +'.txt'

    resultArr = ['', '']

    file = open(file_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        splited = line.split('\t')
        if shortcut_name in splited[0]:
            resultArr[0] = splited[1]                    # 반환할 패키지명 저장
            resultArr[1] = splited[2].rstrip('\n')       # 반환할 디시콘명 저장
            if shortcut_name == splited[0]:              # 단축어와 완전히 동일하면 탐색종료
                break
    file.close()

    return resultArr

# 즐겨찾기 목록 조회
def show_favorites(ctx):
    log(ctx, 'show_favorites command')

    author_id = str(ctx.author.id)
    
    file_path = os.path.join(hassan_env.FAVORITE_PATH, author_id) + '.txt'

    if not os.path.exists(file_path):
        return ['<@' + author_id + '>님의 즐겨찾기 목록이 존재하지 않습니다.']

    favorites = _read_all_favorite_from_file(file_path)

    # 즐겨찾기 목록 표시 + 사용자 표시
    favorites_cnt = get_file_line_cnt(file_path)
    sender_tag = ctx.author.name + f'님의 즐겨찾기 목록이에요. ({favorites_cnt}/{hassan_env.FAVORITE_MAX})\n'
    header = '#\t단축어\t패키지명\t디시콘명\n'

    msg = sender_tag + header + favorites
    return _group_message(msg)

    
def _read_all_favorite_from_file(file_path):
    favorites = ''
    cnt = 0

    file = open(file_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        splited = line.split('\t')
        cnt += 1
        favorites += str(cnt) + '\t"' + splited[0] + '" "' + splited[1] + '" "' + splited[2].rstrip() + '"\n'
    file.close()

    return favorites

# 즐겨찾기 목록이 MSG_MAX_LENGTH 이상일 때도 보낼 수 있게 하였음
def _group_message(msg):
    start = 0
    end = hassan_env.MSG_MAX_LENGTH - 1

    result = []
    while True:
        splited_msg = msg[start:end]
        result.append(splited_msg)

        left_len = len(msg[end:])

        if left_len <= 0:
            break

        if left_len < hassan_env.MSG_MAX_LENGTH:
            result.append(msg[end:])
            break

        else:
            start = end + 1
            end += hassan_env.MSG_MAX_LENGTH

    return result