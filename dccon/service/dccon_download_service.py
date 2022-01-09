import requests
import copy
import env.hassan_env as hassan_env
from logger.logger import log, system_log
from io import BytesIO
from error.dccon_error import DcconDownloadError
from cache import cache_controller

# 패키지명과 idx을 이용하여 디시콘 다운로드
def download_dccon_by_package(ctx, idx, package_detail_json):
    package_name = package_detail_json['info']['title']

    for dccon in package_detail_json['detail']:                                                                             # 파싱한 결과에서 탐색
        if dccon['title'] == idx:
            buffer, file_name  = _download_single_dccon(dccon)
            file_name = package_name + '_' + file_name
            
            cache_controller.add_cache(package_name, idx, file_name, copy.deepcopy(buffer))
            
            if buffer and file_name:
                return buffer, file_name
            
            log(ctx, 'dccon download failed')
            raise DcconDownloadError(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 다운받는데 실패하였습니다.')

    log(ctx, 'no dccon in package')
    raise DcconDownloadError(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 찾을 수 없습니다.')

# 디시 서버에서 디시콘 다운로드하여 버퍼와 파일명 반환
def _download_single_dccon(dccon):
    try:
        session = requests.Session()
        dccon_img = "http://dcimg5.dcinside.com/dccon.php?no=" + dccon['path']
        dccon_img_request = session.get(dccon_img, headers={'Referer': hassan_env.DCCON_HOME_URL})

        buffer = BytesIO(dccon_img_request.content)
        file_name = dccon['title'] + '.' + dccon['ext']
        
        return buffer, file_name
    except Exception as e:
        system_log('dccon_download : ' + str(e))

    return ['', '']