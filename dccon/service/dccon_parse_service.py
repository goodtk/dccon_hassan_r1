import requests
import urllib
from bs4 import BeautifulSoup
import env.hassan_env as hassan_env
from error.dccon_error import DcconPackageNotFoundError
from logger.logger import log

# 패키지 데이터 파싱
def parse_package_data(ctx, package_name):
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
        return package_detail_json, package_search_req, target_package_num, target_package_name

    except (IndexError, UnboundLocalError) as e:  # maybe no search result w/ IndexError?
        log(ctx, 'error! (maybe no search result) : ' + str(e))
        raise DcconPackageNotFoundError(f'"{package_name}" 디시콘 패키지 정보를 찾을 수 없습니다.')


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
                                cookies={'ci_c': package_search_req.cookies['ci_c']},
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