import os
import env.hassan_env as hassan_env
from logger.logger import log

# 즐겨찾기 삭제
def delete_favorite(ctx, shortcut_name):
    log(ctx, 'delete_favorite command')

    author_id = str(ctx.author.id)
    file_path = os.path.join(hassan_env.FAVORITE_PATH, author_id) + '.txt'

    if not os.path.exists(file_path):
        return '<@' + author_id + '>님의 즐겨찾기 목록이 존재하지 않습니다.'

    file = open(file_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    file.close()

    new_lines = ''
    is_shortcut_exists = False;

    for line in lines:
        splited = line.split('\t')
        if splited[0] == shortcut_name:
            is_shortcut_exists = True
        else:
            new_lines += line

    if is_shortcut_exists:
        file = open(file_path, mode='wt', encoding='utf-8')
        file.writelines(new_lines)
        file.close()

        log(ctx, f'delete_favorite {shortcut_name} is delete from {file_path}.')
        return '<@' + author_id + f'>님의 즐겨찾기 목록에서 "{shortcut_name}" 단축어가 삭제되었습니다.'
    else:
        log(ctx, f'delete_favorite "{shortcut_name}" cannot found')
        return '<@' + author_id + f'>님의 즐겨찾기 목록에서 "{shortcut_name}" 단축어를 찾을 수 없습니다.'

# 즐겨찾기 초기화
def reset_favorites(ctx):
    user_id = str(ctx.author.id)
    file_path = os.path.join(hassan_env.FAVORITE_PATH, user_id) + '.txt'

    if os.path.exists(file_path):
        os.remove(file_path)

    log(ctx, 'reset_favorites reset ' + user_id + '\'s favorites')
    return '<@' + user_id + '>님의 즐겨찾기 목록을 리셋했습니다.'