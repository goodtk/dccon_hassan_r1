import requests
import urllib
from bs4 import BeautifulSoup
from log.logger import log
import env.hassan_env as hassan_env
from cache import cache_controller
from .download import downloader
from send import sender
from dccon import autoclear
from error.dccon_error import DcconDownloadError, DcconPackageNotFoundError

async def send_dccon(ctx, args):
    await ctx.channel.trigger_typing()

    package_name = args[0]
    list_print_mode = _is_print_mode(args)

    try:
        package_data = _parse_package_data(ctx, package_name)
    except DcconPackageNotFoundError as e:
        await sender.send(ctx, str(e))
        return

    package_detail_json = package_data[0]
    package_search_req = package_data[1]
    target_package_num = package_data[2]
    package_name = package_data[3]

    if list_print_mode:
        messages = _list_print(package_detail_json, package_name, package_search_req, target_package_num)
        for msg in messages:
            await sender.send(ctx, msg)
        return

    idx = args[1]
    log(ctx, f'interpreted: {package_name}, {idx}. list_print_mode: {list_print_mode}')

    try:
        buffer, file_name = await _get_dccon_file(ctx, package_detail_json, idx)
        await sender.send_with_dccon(ctx, buffer, file_name)
        log(ctx, 'succeed')
    except DcconDownloadError as e:
        await sender.send(ctx, str(e))
    except:
        log(ctx, 'not found')
        await sender.send(ctx, f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 찾지 못했습니다.')
        await sender.send(ctx, '인자로 패키지 이름만 넘길 경우 사용 가능한 디시콘 목록이 출력됩니다.')
    else:
        await autoclear.auto_delete_dccon(ctx)
    
    
def _is_print_mode(args):
    return len(args) < 2

def _parse_package_data(ctx, package_name):
    session = requests.Session()
    package_name_encoded = urllib.parse.quote(package_name)                                                             # 2020-02-07 패키지명을 URL 인코딩하도록 수정하였음.
    package_search_url = hassan_env.DCCON_SEARCH_URL + package_name_encoded
    package_search_req = session.get(package_search_url)
    package_search_html = BeautifulSoup(package_search_req.text, 'html.parser')
    package_search_is_empty = package_search_html.select('#right_cont_wrap > div > div.dccon_search_none > p > span')   # 검색결과가 없는경우 체크

    try:
        if package_search_is_empty:
            raise IndexError

        package_search_list = package_search_html.select('#right_cont_wrap > div > div.dccon_listbox > ul > li')
        target_package = _find_package_by_name(package_search_list, package_name)
        target_package_name = target_package.find('strong', {'class' : 'dcon_name'}).string                             # 대상 패키지명 추출
        target_package_num = target_package.get('package_idx')  # get dccon number of target dccon package
        log(ctx, 'processing with: ' + target_package_num)

        package_detail_json = _dccon_get_detail(session, package_search_req, package_name, target_package_num)
        return [package_detail_json, package_search_req, target_package_num, target_package_name]

    except (IndexError, UnboundLocalError) as e:  # maybe no search result w/ IndexError?
        log(ctx, 'error! (maybe no search result) : ' + str(e))
        raise DcconPackageNotFoundError(f'"{package_name}" 디시콘 패키지 정보를 찾을 수 없습니다.')

def _list_print(package_detail_json, package_name, package_search_req, target_package_num):
    available_dccon_list = []
    for dccon in package_detail_json['detail']:
        available_dccon_list.append(dccon['title'])

    result = [f'"{package_name}"에서 사용 가능한 디시콘 : ' + ', '.join(available_dccon_list).rstrip(', ')]
    result.append('디시콘샵 URL : ' + package_search_req.request.url + '#' + target_package_num)
    return result

# respect https://github.com/gw1021/dccon-downloader/blob/master/python/app.py#L7:L18
async def _get_dccon_file(ctx, package_detail_json, idx):
    package_name = package_detail_json['info']['title']

    results = cache_controller.find_cache(package_name, idx)                                                                 # 2020-02-09 캐시에서 탐색

    buffer = ''
    file_name = ''

    if results:
        log(ctx, 'use cache')
        buffer = results[0]
        file_name = results[1]
    else:
        downloaded = await _download_dccon(ctx, package_name, idx, package_detail_json)
        buffer = downloaded[0]
        file_name = downloaded[1]

    return [buffer, file_name]

async def _download_dccon(ctx, package_name, idx, package_detail_json):
    for dccon in package_detail_json['detail']:                                                                             # 파싱한 결과에서 탐색
        if dccon['title'] == idx:
            results = await downloader.dccon_download(dccon, package_name, idx)
            
            if not results[0] == '':
                return results
            
            log(ctx, 'dccon download failed')
            raise DcconDownloadError(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 다운받는데 실패하였습니다.')

    log(ctx, 'no dccon in package')
    raise DcconDownloadError(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 찾을 수 없습니다.')
        

# 검색결과 중 디시콘 패키지명과 완전히 일치한 패키지가 있는지 탐색
def _find_package_by_name(package_search_list, package_name):
    for searched_package in package_search_list:
        searched_package_name = searched_package.find('strong', {'class' : 'dcon_name'}).string
        if searched_package_name == package_name:                                                                   # 완전히 동일한 패키지명이 탐색되면 해당 패키지 선택한다.
            return searched_package
    return package_search_list[0]

# 디시 서버에서 타겟 디시콘의 세부사항 가져옴
def _dccon_get_detail(session, package_search_req, package_name, target_package_num):
    package_detail_req = session.post(hassan_env.DCCON_DETAILS_URL,
                                # content-type: application/x-www-form-urlencoded; charset=UTF-8
                                cookies={'ci_c': package_search_req.cookies['ci_c'],
                                            'PHPSESSID': package_search_req.cookies['PHPSESSID']},
                                headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                            'Referer': hassan_env.DCCON_SEARCH_URL + str(package_name.encode('utf-8')),
                                            'Origin': hassan_env.DCCON_HOME_URL,
                                            'X-Requested-With': 'XMLHttpRequest'},
                                data={'ci_t': package_search_req.cookies['ci_c'],
                                        'package_idx': target_package_num,
                                        'code': ''})

    # 에러 핸들링 여기서 해야함
        
    package_detail_json = package_detail_req.json()

    '''
        info /  'package_idx'
                'seller_no'
                'seller_id'
                'title'
                'category'
                'path'
                'description'
                'price'
                'period'
                'icon_cnt'
                'state'
                'open'
                'sale_count'
                'reg_date'
                'seller_name'
                'code'
                'seller_type'
                'mandoo'
                'main_img_path'
                'list_img_path'
                'reg_date_short'
                    
        detail /  () /  'idx'
                        'package_idx'
                        'title'
                        'sort'
                        'ext'
                        'path'
    '''
    return package_detail_json