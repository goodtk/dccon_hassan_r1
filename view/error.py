from logger.logger import log
from send import sender

async def send_send_dccon_error(ctx):
    await sender.send(ctx, '사용법을 참고해주세요. (!도움)' + '\n디시콘 패키지명이나 디시콘명에 공백이 있을 경우 큰따옴표로 묶어야 합니다.')

async def send_error_favorite(ctx, error_type='명령어'):
    await sender.send(ctx, str(error_type) + '이(가) 올바르지 않습니다. (!즐찾)')

async def send_error_send_favorite(ctx):
    await sender.send(ctx, '인자수가 올바르지 않습니다. (!ㅋ "단축어")')

async def send_error_add_favorite(ctx):
    await sender.send(ctx, '인자수가 올바르지 않습니다. (!즐찾 추가 "단축어" "디시콘 패키지명" "디시콘 명")')

async def send_error_delete_favorite(ctx):
    await sender.send(ctx, '인자수가 올바르지 않습니다. (!즐찾 삭제 "단축어")')

async def send_error_search_favorite(ctx):
    await sender.send(ctx, '인자수가 올바르지 않습니다. (!즐찾 검색 "검색어")')

async def send_error_backup_favorite(ctx):
    await sender.send(ctx, '인자수가 올바르지 않습니다. (!즐찾 백업)')

async def send_error_restore_favorite(ctx):
    await sender.send(ctx, '인자수가 올바르지 않습니다. (!즐찾 복원 "파일URL")')

async def send_error_directory_create(ctx):
    await sender.send(ctx, '경로 생성에 실패하였습니다. 관리자에게 문의해주세요.')