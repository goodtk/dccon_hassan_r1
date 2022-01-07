import os

def get_file_line_cnt(file_path):
    if not os.path.exists(file_path):                  # 즐겨찾기 목록이 존재하지 않으면 0 반환
        return 0

    file = open(file_path, mode='rt', encoding='utf-8')
    count = len(file.readlines())
    file.close()

    return count

