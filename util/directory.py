import os
from log.logger import system_log

# 폴더 생성
def create_directory(path):
    try:
        if not(os.path.isdir(path)):
            system_log(f'creating directory at {path}')
            os.makedirs(os.path.join(path))
            system_log(f'directory created at {path}')
        
        return True
    except OSError as e:
        if e.errno != errno.EEXIST:
            system_log(f'failed to create directory at {path}!')
        
        return False