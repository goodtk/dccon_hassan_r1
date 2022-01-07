import os
import env.hassan_env as hassan_env
from log.logger import log
from util.file_util import get_file_line_cnt
from requests import get
import shutil
from error.favorite_error import FavoriteError

# 요청한 사용자에게 대상 사용자의 즐겨찾기 목록을 전송
def get_favorites_file(ctx, user_id):
    file_name = user_id + '.txt'
    file_path = os.path.join(hassan_env.FAVORITE_PATH, file_name)

    if (not os.path.exists(file_path)) or (get_file_line_cnt(file_path) == 0):
        raise FavoriteError('<@' + user_id + '>님의 즐겨찾기 목록이 존재하지 않습니다.')

    msg = '<@' + user_id + '>님의 즐겨찾기 목록을 업로드했습니다.'
    return [msg, file_path, file_name]

# 즐겨찾기 복원
def restore_favorites(ctx, download_url):
    user_id = str(ctx.author.id)
    save_file_path = os.path.join(hassan_env.FAVORITE_PATH, user_id) + '.txt.tmp'

    _download_file(download_url, save_file_path) # ID.txt.tmp 로 파일 임시로 저장

    new_favorites_line_length = get_file_line_cnt(save_file_path)

    if (new_favorites_line_length <= 0) or (new_favorites_line_length > hassan_env.FAVORITE_MAX): # 유저가 보낸 즐겨찾기 파일의 줄 수가 0보다 작거나 MAX보다 크면 교체하지 않음.
        log(ctx, 'restore_favorites ' + user_id + '\'s favorites restore blocked')
        os.remove(save_file_path)
        return '<@' + user_id + '>님이 업로드한 즐겨찾기 파일이 빈 파일이거나 최대치를 넘깁니다. 복원할 수 없습니다.'

    # TODO: 파일 사이즈, 확장자 검사 필요

    shutil.move(save_file_path, save_file_path[:-4])                                   # 즐겨찾기 교체
    log(ctx, 'restore_favorites restored ' + user_id + '\'s favorites')
    return '<@' + user_id + '>님의 즐겨찾기 목록을 복원했습니다.'

# 유저가 올린 URL로부터 파일을 다운
def _download_file(download_url, file_name = None):
	if not file_name:
		file_name = download_url.split('/')[-1]

	with open(file_name, "wb") as file:
            response = get(download_url)               
            file.write(response.content)

