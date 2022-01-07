import requests
import env.hassan_env as hassan_env
from io import BytesIO
from cache import cache_controller

# 디시 서버에서 디시콘 다운로드하여 버퍼와 파일명 반환
async def dccon_download(dccon, package_name, idx):
    resultArr = ['', '']

    try:
        session = requests.Session()
        dccon_img = "http://dcimg5.dcinside.com/dccon.php?no=" + dccon['path']
        dccon_img_request = session.get(dccon_img, headers={'Referer': hassan_env.DCCON_HOME_URL})

        buffer = BytesIO(dccon_img_request.content)
        file_name = package_name + '_' + dccon['title'] + '.' + dccon['ext']

        cache = BytesIO(dccon_img_request.content)
        await cache_controller.add_cache(package_name, idx, file_name, cache)                     # 캐시에 추가
            
    except:
        return resultArr
    else:
        resultArr[0] = buffer
        resultArr[1] = file_name
        return resultArr