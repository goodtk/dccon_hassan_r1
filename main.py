import requests
import os
import urllib
import io

from io import BytesIO
from bs4 import BeautifulSoup
from discord import Game, Embed, File
from discord.ext import commands

from log.logger import log, system_log
from util.directory_util import create_directory
from cache import cache_controller
from env.env_loader import load_env
import env.hassan_env as hassan_env
from favorite import favorite_controller
from util.string_util import combine_words

bot = commands.Bot(command_prefix='!')


'''
@bot.command(name='콘')
async def send_dccon(ctx, *args):
    await ctx.channel.send(args)

'''

load_env()

@bot.event
async def on_ready():
    await bot.change_presence(activity=Game(name='!도움'))
    system_log('Bot ready')
    system_log(f'BOT_TOKEN : {hassan_env.BOT_TOKEN}')
    system_log(f'OWNER_ID : {hassan_env.OWNER_ID}')
    system_log(f'FAVORITE_PATH : {hassan_env.FAVORITE_PATH}')
    system_log(f'FAVORITE_MAX : {hassan_env.FAVORITE_MAX}')
    system_log(f'CACHE_PATH : {hassan_env.CACHE_PATH}')
    system_log(f'CACHE_MAX : {hassan_env.CACHE_MAX}')
    system_log(f'CONCMD_AUTODEL_CHANNEL_PATH : {hassan_env.CMD_AUTODEL_CHANNEL_PATH}')



@bot.command(name='도움')
async def help(ctx):
    log(ctx, 'help command')
    embed = Embed(title='안녕하세요! 디시콘 핫산이에요!',
                  description='명령어들은 아래에서 전부 보실 수 있어요.',
                  color=hassan_env.EMBED_COLOR)
    embed.add_field(name='사용 방법', value='!콘 "디시콘 패키지 제목" "콘 이름"', inline=False)
    embed.add_field(name='사용 예시 1', value='!콘 멘헤라콘 15, !콘 "마히로콘 리메이크" 꿀잠, !콘 "좋은말콘 스페셜 에디션" 응원, ...', inline=False)
    embed.add_field(name='사용 예시 2', value='!콘 "나나히라 라인", !콘 카구야는인사받고싶어, ... (디시콘 패키지 이름만 입력 시 디시콘 목록 출력)', inline=False)
    embed.add_field(name='명령어', value='!콘, !도움, !대하여, !ㅋ, !즐찾', inline=False)

    embed.set_footer(text='그코좆망겜')
    await ctx.channel.send(embed=embed)


@bot.command(name='대하여')
async def about(ctx):
    log(ctx, 'about command')
    embed = Embed(title='디시콘 핫산',
                  description='디시콘을 디스코드에서 쓸 수 있게 해주는 디스코드 봇입니다.',
                  color=hassan_env.EMBED_COLOR)
    embed.add_field(name='Repository', value='https://github.com/dldhk97/dccon_hassan', inline=False)
    await ctx.channel.send(embed=embed)


@bot.command(name='콘')
async def send_dccon(ctx, *args):
    log(ctx, 'send_dccon command')

    if not args or len(args) > 2:
        log(ctx, 'empty args')
        await ctx.channel.send('사용법을 참고해주세요. (!도움)')
        await ctx.channel.send('디시콘 패키지명이나 디시콘명에 공백이 있을 경우 큰따옴표로 묶어야 합니다.')
        return

    list_print_mode = False
    package_name = args[0]
    idx = 'list_print_mode'
    if len(args) == 2:
        idx = args[1]
    else:
        list_print_mode = True

    log(ctx, f'interpreted: {package_name}, {idx}. list_print_mode: {list_print_mode}')

    await ctx.channel.trigger_typing()

    ############################################################################################################
    # respect https://github.com/gw1021/dccon-downloader/blob/master/python/app.py#L7:L18

    # TODO: 변수명 간단히

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
        target_package = dccon_find_exactly_same(package_search_list, package_name)                                     # 2020-02-04 완전히 동일한 패키지명이 선택되도록 수정.

        if target_package == '':
            target_package = package_search_list[0]                                                                     # 완전히 동일한 패키지명이 탐색되지 않음.
            log(ctx, 'pick first dccon package (bs4 obj) from search list')
        else:
            log(ctx, 'exactly same dccon found')

        target_package_name = target_package.find('strong', {'class' : 'dcon_name'}).string                             # 대상 패키지명 추출
    except IndexError as e:  # maybe no search result w/ IndexError?
        log(ctx, 'error! (maybe no search result) : ' + str(e))
        await ctx.channel.send(f'"{package_name}" 디시콘 패키지 정보를 찾을 수 없습니다.')
    except UnboundLocalError as e:
        log(ctx, 'error! (maybe no search result) : ' + str(e))
        await ctx.channel.send(f'"{package_name}" 디시콘 패키지 정보를 찾을 수 없습니다.')
    else:
        target_package_num = target_package.get('package_idx')  # get dccon number of target dccon package
        log(ctx, 'processing with: ' + target_package_num)

        package_detail_json = dccon_get_detail(session, package_search_req, package_name, target_package_num)

        # 검색 결과로 바꿔치기
        package_name = package_detail_json['info']['title']

        if list_print_mode:
            available_dccon_list = []
            for dccon in package_detail_json['detail']:
                available_dccon_list.append(dccon['title'])

            await ctx.channel.send(f'"{package_name}"에서 사용 가능한 디시콘 : ' + ', '.join(available_dccon_list).rstrip(', '))
            await ctx.channel.send('미리보기 URL : ' + package_search_req.request.url + '#' + target_package_num)                       # 디시콘 링크 알려줌
        else:
            resultArr = await dccon_use_cache(target_package_name, idx)                                                                 # 2020-02-09 캐시에서 탐색
            cached = False
            buffer = ''
            file_name = ''

            if not resultArr[0] == '':                                                                                                  # 캐시된 이미지가 존재하는 경우
                cached = True
                buffer = resultArr[0]
                file_name = resultArr[1]
            else:                                                                                                                       # 캐시된 이미지가 없을 때
                resultArr = ['', '']
                isExist = False;
                for dccon in package_detail_json['detail']:                                                                             # 파싱한 결과에서 탐색
                    if dccon['title'] == idx:
                        resultArr = await dccon_download(dccon, session, package_name, idx)
                        isExist= True;
                        break

                if isExist:
                    if not resultArr[0] == '':                                                                                              # 디시콘 받아오는데 성공
                        buffer = resultArr[0]
                        file_name = resultArr[1]
                    else:
                        log(ctx, 'dccon download failed')
                        await ctx.channel.send(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 다운받는데 실패하였습니다.')
                        return
                else:
                    log(ctx, 'no dccon in package')
                    await ctx.channel.send(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 찾을 수 없습니다.')
                    return

            succeed = await dccon_send_with_tag(ctx, buffer, file_name)

            # 콘 명령어 자동 삭제 채널에 포함이 된다면 명령어 삭제
            if os.path.exists(hassan_env.CMD_AUTODEL_CHANNEL_PATH): 
                file = open(hassan_env.CMD_AUTODEL_CHANNEL_PATH, mode='rt', encoding='utf-8')
                lines = file.readlines()
                file.close()

                for line in lines:
                    print(str(ctx.channel.id) + ' vs ' + line.replace('\n',''))
                    if str(ctx.channel.id) == line.replace('\n',''): 
                        try:
                            await ctx.message.delete()      # 명령어 메시지 삭제
                            print('콘 명령어 자동 삭제 완료')
                        except Exception as autodelException:
                            print(autodelException)
                        break

            if succeed:
                log(ctx, 'succeed(cached)' if cached else 'succeed')
            else:
                log(ctx, 'not found')

                await ctx.channel.send(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 찾지 못했습니다.')
                await ctx.channel.send('인자로 패키지 이름만 넘길 경우 사용 가능한 디시콘 목록이 출력됩니다.')

############################################################ 모듈화 ############################################################

# 검색결과 중 디시콘 패키지명과 완전히 일치한 패키지가 있는지 탐색
def dccon_find_exactly_same(package_search_list, package_name):
    for searched_package in package_search_list:
        searched_package_name = searched_package.find('strong', {'class' : 'dcon_name'}).string
        if searched_package_name == package_name:                                                                   # 완전히 동일한 패키지명이 탐색되면 해당 패키지 선택한다.
            return searched_package
    return ''


# 로컬 캐시에 디시콘 있으면 버퍼와 파일명 반환
async def dccon_use_cache(package_name, idx):
    resultArr = ['', '']

    if hassan_env.CACHE_MAX == 0:                                                                                              # 캐시 사용하지 않는 경우
        return resultArr

    cache_file_name = cache_controller.read_cache(package_name, idx)

    if not cache_file_name == '':
        cache_file_path = os.path.join(hassan_env.CACHE_PATH, cache_file_name)
        buffer=''

        if not os.path.exists(cache_file_path):                                                                     # 캐시 파일이 존재하지 않는 경우
            return resultArr

        with open(cache_file_path, 'rb') as fin:
            buffer = io.BytesIO(fin.read())

        resultArr[0] = buffer
        resultArr[1] = cache_file_name

    return resultArr


# 디시 서버에서 타겟 디시콘의 세부사항 가져옴
def dccon_get_detail(session, package_search_req, package_name, target_package_num):
    # for i in package_search_req.cookies:
    #     print(i.name, i.value)

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


# 디시 서버에서 디시콘 다운로드하여 버퍼와 파일명 반환
async def dccon_download(dccon, session, package_name, idx):
    resultArr = ['', '']

    try:
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


# 요청자의 태그와 디시콘 전송
async def dccon_send_with_tag(ctx, buffer, file_name):
    sender_tag = "<@" + str(ctx.author.id) + ">"                             # 디시콘 표기 + 콘 사용자 표시
    try:
        await ctx.channel.send(file=File(buffer, file_name), content=sender_tag)
        return True
    except:
        await ctx.channel.send('dccon_send_with_tag : 디시콘 업로드 중 오류 발생.')
        return False

############################################################################################################
############################################################################################################

# 즐겨찾기
@bot.command(name='즐찾')
async def favorite_manage(ctx, *args):
    if not args:
        log(ctx, 'favorite_help command')
        embed = Embed(title='안녕하세요! 디시콘 핫산이에요!',
                  description=f'즐겨찾기는 개인당 {hassan_env.FAVORITE_MAX}개 까지만 추가 가능해요.\n띄워쓰기를 포함하려면 "로 묶어주세요.\n단, 인자가 하나인 경우 "로 안묶어도 됩니다.(삭제, 검색, 사용)',
                  color=hassan_env.EMBED_COLOR)
        embed.add_field(name='즐겨찾기 추가', value='!즐찾 추가 "단축어" "디시콘 패키지 제목" "콘 이름"', inline=False)
        embed.add_field(name='사용 예시', value='!즐찾 멘15 멘헤라콘 15, !즐찾 마히리메꿀잠 "마히로콘 리메이크" 꿀잠 , !즐찾 좋은말콘응원 "좋은말콘 스페셜 에디션" 응원, ...', inline=False)
        embed.add_field(name='즐겨찾기 목록 확인', value='!즐찾 목록', inline=False)
        embed.add_field(name='즐겨찾기 삭제', value='!즐찾 삭제 "단축어"', inline=False)
        embed.add_field(name='즐겨찾기 검색', value='!즐찾 검색 "단축어"', inline=False)
        embed.add_field(name='즐겨찾기 사용', value='!ㅋ "단축어"', inline=False)
        embed.add_field(name='즐겨찾기 백업', value='!즐찾 백업 [사용자ID] (ID는 옵션)', inline=False)
        embed.add_field(name='사용 예시', value='!즐찾 백업, !즐찾 백업 123456789, ...', inline=False)
        embed.add_field(name='즐겨찾기 복원', value='!즐찾 복원 "파일URL"', inline=False)
        embed.add_field(name='즐겨찾기 초기화', value='!즐찾 초기화', inline=False)
        embed.set_footer(text='몬헌좆망겜')
        await ctx.channel.send(embed=embed)
        return

    if not os.path.isdir(hassan_env.FAVORITE_PATH):
        if not create_directory(hassan_env.FAVORITE_PATH):                                        # 즐겨찾기 폴더가 존재하지 않으면 생성. 생성 실패시 오류메시지 출력.
            await ctx.channel.send('경로 생성에 실패하였습니다. 관리자에게 문의하세요!')
    
    if args[0] == '추가':
        await add_favorite(ctx, *args);

    elif args[0] == '목록':
        await show_favorites(ctx)

    elif args[0] == '삭제':
        await delete_favorite(ctx, *args)

    elif args[0] == '검색':
        await search_favorite(ctx, *args)

    elif args[0] == '사용':
        await ctx.channel.send('즐겨찾기 사용은 !ㅋ "단축어" 으로 사용해주세요.')

    elif args[0] == '백업':
        await favorite_backup(ctx, *args)

    elif args[0] == '복원':
        await restore_favorites(ctx, *args)

    elif args[0] == '초기화':
        await reset_favorites(ctx, *args)

    else:
        await ctx.channel.send('올바르지 않은 명령어입니다. 사용법을 참고해주세요. (!즐찾)')


# 즐겨찾기 추가
async def add_favorite(ctx, *args):
    log(ctx, 'add_favorite command')

    if not len(args) == 4:
        log(ctx, 'add_favorite wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. (!즐찾 추가 "단축어" "디시콘 패키지명" "디시콘 명")')
        return

    shortcut_name = args[1]
    package_name = args[2]
    dccon_name = args[3]

    msg =  favorite_controller.add_favorite(ctx, shortcut_name, package_name, dccon_name)
   
    await ctx.channel.send(msg)


# 즐겨찾기 목록 조회
async def show_favorites(ctx):
    result = favorite_controller.show_favorites(ctx)
    for msg in result:
        await ctx.channel.send(msg)


# 즐겨찾기 삭제
async def delete_favorite(ctx, *args):
    log(ctx, 'delete_favorite command')

    if len(args) < 2:
        log(ctx, 'delete_favorite wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. (!즐찾 삭제 "단축어")')
        return

    shortcut_name = combine_words(args[1:])

    msg = favorite_controller.delete_favorite(ctx, shortcut_name)
    await ctx.channel.send(msg)


# 즐겨찾기 검색
async def search_favorite(ctx, *args):
    log(ctx, 'search_favorite command')

    if len(args) < 2:
        log(ctx, 'search_favorite wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. (!즐찾 검색 "단축어")')
        return

    keyword = combine_words(args[1:])
    msg = favorite_controller.serach_favorites(ctx, keyword)

    await ctx.author.send(msg)


# 즐겨찾기 사용
@bot.command(name='ㅋ')
async def send_favorite(ctx, *args):
    log(ctx, 'send_favorite command')

    if len(args) <= 0:
        log(ctx, 'send_favorite wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. (!ㅋ "단축어")')
        return

    shortcut_name = combine_words(args)

    result_pair = favorite_controller.find_favorite_one(ctx, shortcut_name)
    
    is_success = result_pair[0]
    result = result_pair[1]
    
    if is_success:
        await send_dccon(ctx, *result)
    else:
        await ctx.channel.send(result)
    

# 즐겨찾기 백업
@bot.command(pass_context=True)
async def favorite_backup(ctx, *args):

    user_id = str(ctx.author.id)

    if len(args) == 2:                          # 인자가 1개인 경우에는 해당 사용자의 즐겨찾기 목록을 백업
        user_id = args[1]
    elif len(args) > 2:
        log(ctx, 'favorite_backup wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. (!즐찾 백업 "사용자ID")')
        return

    await send_favorites(ctx, user_id)


# 요청한 사용자에게 대상 사용자의 즐겨찾기 목록을 전송
@bot.command(pass_context=True)
async def send_favorites(ctx, user_id):
    results = favorite_controller.dump_favorites(ctx, user_id)
    
    is_succeed = results[0]
    msg = results[1]
    file_path = results[2]
    file_name = results[3]

    if is_succeed:
        await ctx.author.send(file=File(file_path, file_name), content=msg)
    else:
        await ctx.channel.send(msg)


# 즐겨찾기 복원
async def restore_favorites(ctx, *args):
    if not len(args) == 2:
        log(ctx, 'restore_favorites wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. (!즐찾 복원 "파일URL")')
        return

    download_url = args[1]
    msg = favorite_controller.resotre_favorites(ctx, download_url)
    await ctx.channel.send(msg)

# 즐겨찾기 초기화
async def reset_favorites(ctx, *args):
    msg = favorite_controller.reset_favorites(ctx)
    await ctx.channel.send(msg)

############################################################################################################
############################################################################################################

# 캐시 클리어
@bot.command(name='캐시클리어')
async def controller_clear_cache(ctx, *args):
    user_id = str(ctx.author.id)
    owner_id = hassan_env.OWNER_ID                            ## TODO: 해당 서버의 주인 id get
    
    msg = cache_controller.clear_cache(user_id, owner_id)

    await ctx.channel.send(msg)


# DM
async def send_direct_message(user_id, contents):
    user = await bot.fetch_user(user_id)
    dm_channel = user.dm_channel
    if dm_channel is None:
        await user.create_dm()
        dm_channel = user.dm_channel
    await dm_channel.send(content=contents)

@bot.event
async def on_command_error(ctx, error):
    log(ctx, error)
    await ctx.channel.send(error)


if __name__ == "__main__":
    bot.run(hassan_env.BOT_TOKEN)
