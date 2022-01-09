from logger.logger import log
from cache import cache_controller
from . import command_autoclear_service, dccon_download_service, dccon_parse_service
from send import sender
from error.dccon_error import DcconDownloadError, DcconPackageNotFoundError

# 디시콘 목록 출력
async def send_dccon_list(ctx, package_name):
    try:
        package_data = dccon_parse_service.parse_package_data(ctx, package_name)
    except DcconPackageNotFoundError as e:
        await sender.send(ctx, str(e))
        return

    package_detail_json = package_data[0]
    package_search_req = package_data[1]
    target_package_num = package_data[2]
    package_name = package_data[3]

    log(ctx, f'send_dccon_list, interpreted: {package_name}.')
    
    message = _list_print(package_detail_json, package_name, package_search_req, target_package_num)
    await sender.send(ctx, message)

# TODO: view로 이동
# 디시콘 목록과 디시콘샵 URL 반환
def _list_print(package_detail_json, package_name, package_search_req, target_package_num):
    available_dccon_list = []
    for dccon in package_detail_json['detail']:
        available_dccon_list.append(dccon['title'])

    result = f'"{package_name}"에서 사용 가능한 디시콘 : ' + ', '.join(available_dccon_list).rstrip(', ')
    result += '\n' + '디시콘샵 URL : ' + package_search_req.request.url + '#' + target_package_num
    return result



# 디시콘 출력
async def send_dccon(ctx, package_name, idx):
    try:
        package_data = dccon_parse_service.parse_package_data(ctx, package_name)
    except DcconPackageNotFoundError as e:
        await sender.send(ctx, str(e))
        return

    package_detail_json = package_data[0]
    package_name = package_data[3]

    log(ctx, f'send_dccon, interpreted: {package_name}, {idx}.')

    try:
        buffer, file_name = _get_dccon_file(ctx, package_detail_json, idx)
        await sender.send_with_dccon(ctx, buffer, file_name)
        log(ctx, 'succeed')
    except DcconDownloadError as e:
        await sender.send(ctx, str(e))
    except:
        log(ctx, 'not found')
        await sender.send(ctx, f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 찾지 못했습니다.')
        await sender.send(ctx, '인자로 패키지 이름만 넘길 경우 사용 가능한 디시콘 목록이 출력됩니다.')
    
    if command_autoclear_service.is_command_autodelete_channel(ctx):
        await ctx.message.delete()                      # 명령어 메시지 삭제

# 디시콘 파일명, 버퍼를 다운 혹은 캐시를 통해 반환
# respect https://github.com/gw1021/dccon-downloader/blob/master/python/app.py#L7:L18
def _get_dccon_file(ctx, package_detail_json, idx):
    package_name = package_detail_json['info']['title']

    buffer, file_name  = cache_controller.find_cache(package_name, idx)                                                                 # 2020-02-09 캐시에서 탐색

    if buffer and file_name:
        log(ctx, 'use cache')
    else:
        buffer, file_name = dccon_download_service.download_dccon_by_package(ctx, idx, package_detail_json)

    return buffer, file_name
        
