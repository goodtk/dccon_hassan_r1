import requests
import os
import urllib
import io
import shutil

from datetime import datetime
from io import BytesIO
from bs4 import BeautifulSoup
from discord import Game, Embed, File
from discord.ext import commands
from dotenv import load_dotenv
from requests import get
from urllib import parse

load_dotenv()  # load bot token


def from_text(ctx):
    # msg_fr = msg.server.name + ' > ' + msg.channel.name + ' > ' + msg.author.name
    # msg.server --> msg.guild
    # https://discordpy.readthedocs.io/en/latest/migrating.html#server-is-now-guild
    
    channel_type = ctx.channel.type.value
    if channel_type == 1:
        return f'DM > {ctx.author.name}'

    else:
        return f'{ctx.guild.name} > {ctx.channel.name} > {ctx.author.name}'


def log(fr, text):
    print(f'{fr} | {str(datetime.now())} | {text}')  # TODO: 시간대 조정


BOT_TOKEN = os.getenv('BOT_TOKEN')
DCCON_HOME_URL = 'https://dccon.dcinside.com/'
DCCON_SEARCH_URL = 'https://dccon.dcinside.com/hot/1/title/'
DCCON_DETAILS_URL = 'https://dccon.dcinside.com/index/package_detail'
EMBED_COLOR = 0x4559e9
INVITE_URL = 'https://discordapp.com/oauth2/authorize?client_id=629279090716966932&scope=bot&permissions=101376'
OWNER_ID = os.getenv('OWNER_ID')
MSG_MAX_LENGTH = 2000

FAVORITE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/favorites/'
FAVORITE_MAX = int(os.getenv('FAVORITE_MAX'))

CACHE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/.cache/'
CACHE_MAX = int(os.getenv('CACHE_MAX'))

CONCMD_AUTODEL_CHANEL_PATH = os.path.dirname(os.path.abspath(__file__)) + '/.concmdAutodelChannel'

bot = commands.Bot(command_prefix='!')


'''
@bot.command(name='콘')
async def send_dccon(ctx, *args):
    await ctx.channel.send(args)

'''


@bot.event
async def on_ready():
    await bot.change_presence(activity=Game(name='!도움'))
    log('SYSTEM', 'Bot ready')
    log('SYSTEM', f'BOT_TOKEN : {BOT_TOKEN}')
    log('SYSTEM', f'OWNER_ID : {OWNER_ID}')
    log('SYSTEM', f'FAVORITE_PATH : {FAVORITE_PATH}')
    log('SYSTEM', f'FAVORITE_MAX : {FAVORITE_MAX}')
    log('SYSTEM', f'CACHE_PATH : {CACHE_PATH}')
    log('SYSTEM', f'CACHE_MAX : {CACHE_MAX}')


@bot.command(name='도움')
async def help(ctx):
    log(from_text(ctx), 'help command')
    embed = Embed(title='안녕하세요! 디시콘 핫산이에요!',
                  description='명령어들은 아래에서 전부 보실 수 있어요.',
                  color=EMBED_COLOR)
    embed.add_field(name='사용 방법', value='!콘 "디시콘 패키지 제목" "콘 이름"', inline=False)
    embed.add_field(name='사용 예시 1', value='!콘 멘헤라콘 15, !콘 "마히로콘 리메이크" 꿀잠, !콘 "좋은말콘 스페셜 에디션" 응원, ...', inline=False)
    embed.add_field(name='사용 예시 2', value='!콘 "나나히라 라인", !콘 카구야는인사받고싶어, ... (디시콘 패키지 이름만 입력 시 디시콘 목록 출력)', inline=False)
    embed.add_field(name='명령어', value='!콘, !도움, !대하여, !ㅋ, !즐찾', inline=False)

    embed.set_footer(text='그코좆망겜')
    await ctx.channel.send(embed=embed)


@bot.command(name='대하여')
async def about(ctx):
    log(from_text(ctx), 'about command')
    embed = Embed(title='디시콘 핫산',
                  description='디시콘을 디스코드에서 쓸 수 있게 해주는 디스코드 봇입니다.',
                  color=EMBED_COLOR)
    embed.add_field(name='Repository', value='https://github.com/dldhk97/KITZzamBot', inline=False)
    await ctx.channel.send(embed=embed)


@bot.command(name='콘')
async def send_dccon(ctx, *args):
    log(from_text(ctx), 'send_dccon command')

    if not args or len(args) > 2:
        log(from_text(ctx), 'empty args')
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

    log(from_text(ctx), f'interpreted: {package_name}, {idx}. list_print_mode: {list_print_mode}')

    await ctx.channel.trigger_typing()

    ############################################################################################################
    # respect https://github.com/gw1021/dccon-downloader/blob/master/python/app.py#L7:L18

    # TODO: 변수명 간단히

    session = requests.Session()

    package_name_encoded = urllib.parse.quote(package_name)                                                             # 2020-02-07 패키지명을 URL 인코딩하도록 수정하였음.
    package_search_url = DCCON_SEARCH_URL + package_name_encoded

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
            log(from_text(ctx), 'pick first dccon package (bs4 obj) from search list')
        else:
            log(from_text(ctx), 'exactly same dccon found')

        target_package_name = target_package.find('strong', {'class' : 'dcon_name'}).string                             # 대상 패키지명 추출
    except IndexError as e:  # maybe no search result w/ IndexError?
        log(from_text(ctx), 'error! (maybe no search result) : ' + str(e))
        await ctx.channel.send(f'"{package_name}" 디시콘 패키지 정보를 찾을 수 없습니다.')
    except UnboundLocalError as e:
        log(from_text(ctx), 'error! (maybe no search result) : ' + str(e))
        await ctx.channel.send(f'"{package_name}" 디시콘 패키지 정보를 찾을 수 없습니다.')
    else:
        target_package_num = target_package.get('package_idx')  # get dccon number of target dccon package
        log(from_text(ctx), 'processing with: ' + target_package_num)

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
                        log(from_text(ctx), 'dccon download failed')
                        await ctx.channel.send(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 다운받는데 실패하였습니다.')
                        return
                else:
                    log(from_text(ctx), 'no dccon in package')
                    await ctx.channel.send(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 찾을 수 없습니다.')
                    return

            succeed = await dccon_send_with_tag(ctx, buffer, file_name)

            # 콘 명령어 자동 삭제 채널에 포함이 된다면 명령어 삭제
            if os.path.exists(CONCMD_AUTODEL_CHANEL_PATH): 
                file = open(CONCMD_AUTODEL_CHANEL_PATH, mode='rt', encoding='utf-8')
                lines = file.readlines()
                file.close()

                for line in lines:
                    print(str(ctx.channel.id) + ' vs ' + line.replace('\n',''))
                    if str(ctx.channel.id) == line.replace('\n',''): 
                        await ctx.message.delete()      # 명령어 메시지 삭제
                        print('콘 명령어 자동 삭제 완료')
                        break

            if succeed:
                log(from_text(ctx), 'succeed(cached)' if cached else 'succeed')
            else:
                log(from_text(ctx), 'not found')

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

    if CACHE_MAX == 0:                                                                                              # 캐시 사용하지 않는 경우
        return resultArr

    cache_file_name = get_cache_file_name(package_name, idx)

    if not cache_file_name == '':
        cache_file_path = CACHE_PATH + cache_file_name
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

    package_detail_req = session.post(DCCON_DETAILS_URL,
                                # content-type: application/x-www-form-urlencoded; charset=UTF-8
                                cookies={'ci_c': package_search_req.cookies['ci_c'],
                                            'PHPSESSID': package_search_req.cookies['PHPSESSID']},
                                headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                            'Referer': DCCON_SEARCH_URL + str(package_name.encode('utf-8')),
                                            'Origin': DCCON_HOME_URL,
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
        dccon_img_request = session.get(dccon_img, headers={'Referer': DCCON_HOME_URL})

        buffer = BytesIO(dccon_img_request.content)
        file_name = package_name + '_' + dccon['title'] + '.' + dccon['ext']

        if not (CACHE_MAX == 0):
            cache = BytesIO(dccon_img_request.content)
            await acc_cache(package_name, idx, file_name, cache)                     # 캐시에 추가
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
        log(from_text(ctx), 'favorite_help command')
        embed = Embed(title='안녕하세요! 디시콘 핫산이에요!',
                  description=f'즐겨찾기는 개인당 {FAVORITE_MAX}개 까지만 추가 가능해요.\n띄워쓰기를 포함하려면 "로 묶어주세요.\n단, 인자가 하나인 경우 "로 안묶어도 됩니다.(삭제, 검색, 사용)',
                  color=EMBED_COLOR)
        embed.add_field(name='즐겨찾기 추가', value='!즐찾 추가 "단축어" "디시콘 패키지 제목" "콘 이름"', inline=False)
        embed.add_field(name='사용 예시', value='!즐찾 멘15 멘헤라콘 15, !즐찾 마히리메꿀잠 "마히로콘 리메이크" 꿀잠 , !즐찾 좋은말콘응원 "좋은말콘 스페셜 에디션" 응원, ...', inline=False)
        embed.add_field(name='즐겨찾기 목록 확인', value='!즐찾 목록', inline=False)
        embed.add_field(name='즐겨찾기 삭제', value='!즐찾 삭제 "단축어"', inline=False)
        embed.add_field(name='즐겨찾기 검색', value='!즐찾 검색 "단축어"', inline=False)
        embed.add_field(name='즐겨찾기 사용', value='!ㅋ "단축어"', inline=False)
        embed.add_field(name='즐겨찾기 백업', value='!즐찾 백업 [사용자ID] (ID는 옵션)', inline=False)
        embed.add_field(name='사용 예시', value='!즐찾 백업, !즐찾 백업 123456789, ...', inline=False)
        embed.add_field(name='즐겨찾기 복원', value='!즐찾 복원 "파일URL"', inline=False)
        embed.add_field(name='즐겨찾기 리셋', value='!즐찾 리셋', inline=False)
        embed.set_footer(text='몬헌좆망겜')
        await ctx.channel.send(embed=embed)
        return

    if not os.path.isdir(FAVORITE_PATH):
        if not create_directory(FAVORITE_PATH):                                        # 즐겨찾기 폴더가 존재하지 않으면 생성. 생성 실패시 오류메시지 출력.
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

    elif args[0] == '리셋':
        await reset_favorites(ctx, *args)

    else:
        await ctx.channel.send('올바르지 않은 명령어입니다. 사용법을 참고해주세요. (!즐찾)')


# 즐겨찾기 추가
async def add_favorite(ctx, *args):
    log(from_text(ctx), 'add_favorite command')

    if not len(args) == 4:
        log(from_text(ctx), 'add_favorite wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. (!즐찾 추가 "단축어" "디시콘 패키지명" "디시콘 명")')
        return

    shortcut_name = args[1]
    package_name = args[2]
    dccon_name = args[3]

    file_path = FAVORITE_PATH + str(ctx.author.id) +'.txt'

    registed_count = get_file_line_cnt(file_path)

    if registed_count >= FAVORITE_MAX:                                          # 즐겨찾기 추가횟수 체크
        log(from_text(ctx), 'delete_favorite cannot register favorite (max)')
        await ctx.channel.send('더 이상 즐겨찾기를 추가할 수 없습니다. 즐겨찾기 삭제 후 시도해주세요.')
        return
    elif registed_count > 0 and is_exactly_same_exist(ctx, shortcut_name):     # 해당 단축어가 이미 추가되어있는지 체크
        log(from_text(ctx), f'delete_favorite "{shortcut_name}" already exists.')
        await ctx.channel.send(f'"{shortcut_name}" 단축어으로 추가된 즐겨찾기가 이미 존재합니다.')
        return 

    author_id = str(ctx.author.id)
    file = open(file_path, mode='at', encoding='utf-8')
    file.write(shortcut_name + '\t' + package_name + '\t' + dccon_name + '\n')
    file.close()

    log(from_text(ctx), f'add_favorite {shortcut_name} is saved to {file_path}.')
    await ctx.channel.send('<@' + author_id + f'>님의 즐겨찾기가 추가되었습니다. ({registed_count + 1}/{FAVORITE_MAX})')
    return


# 즐겨찾기 목록 조회
async def show_favorites(ctx):
    log(from_text(ctx), 'show_favorites command')

    author_id = str(ctx.author.id)
    
    file_path = FAVORITE_PATH + author_id +'.txt'

    if not os.path.exists(file_path):
        await ctx.channel.send('<@' + author_id + '>님의 즐겨찾기 목록이 존재하지 않습니다.')
        return

    favorites = ''
    cnt = 0

    file = open(file_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        splited = line.split('\t')
        cnt += 1
        favorites += str(cnt) + '\t"' + splited[0] + '" "' + splited[1] + '" "' + splited[2].rstrip() + '"\n'
    file.close()

    # 즐겨찾기 목록 표시 + 사용자 표시
    sender_tag = ctx.author.name + f'님의 즐겨찾기 목록이에요. ({cnt}/{FAVORITE_MAX})\n'
    header = '#\t단축어\t패키지명\t디시콘명\n'

    msg = sender_tag + header + favorites

    # 즐겨찾기 목록이 2000길이 이상일 때도 보낼 수 있게 하였음
    start = 0
    end = MSG_MAX_LENGTH - 1

    while True:
        splited_msg = msg[start:end]
        splited_len = len(splited_msg)
        await ctx.author.send(splited_msg)

        left_len = len(msg[end:])

        if left_len <= 0:
            break

        if left_len < MSG_MAX_LENGTH:
            await ctx.author.send(msg[end:])
            break

        else:
            start = end + 1
            end += MSG_MAX_LENGTH


# 즐겨찾기 삭제
async def delete_favorite(ctx, *args):
    log(from_text(ctx), 'delete_favorite command')

    if len(args) < 2:
        log(from_text(ctx), 'delete_favorite wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. (!즐찾 삭제 "단축어")')
        return

    author_id = str(ctx.author.id)
    file_path = FAVORITE_PATH + author_id +'.txt'

    if not os.path.exists(file_path):
        await ctx.channel.send('<@' + author_id + '>님의 즐겨찾기 목록이 존재하지 않습니다.')
        return

    shortcut_name = ''

    for i, arg in enumerate(args):
        if i > 0:
            shortcut_name += arg + ' '

    shortcut_name = shortcut_name.strip()

    file = open(file_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    file.close()

    new_lines = ''
    isExist = False;

    for line in lines:
        splited = line.split('\t')
        if splited[0] == shortcut_name:
            isExist = True
        else:
            new_lines += line

    if isExist:
        file = open(file_path, mode='wt', encoding='utf-8')
        file.writelines(new_lines)
        file.close()

        log(from_text(ctx), f'delete_favorite {shortcut_name} is delete from {file_path}.')
        await ctx.channel.send('<@' + author_id + f'>님의 즐겨찾기 목록에서 "{shortcut_name}" 단축어가 삭제되었습니다.')
    else:
        log(from_text(ctx), f'delete_favorite "{shortcut_name}" cannot found')
        await ctx.channel.send('<@' + author_id + f'>님의 즐겨찾기 목록에서 "{shortcut_name}" 단축어를 찾을 수 없습니다.')


# 즐겨찾기 검색
async def search_favorite(ctx, *args):
    log(from_text(ctx), 'search_favorite command')

    if len(args) < 2:
        log(from_text(ctx), 'search_favorite wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. (!즐찾 검색 "단축어")')
        return

    author_id = str(ctx.author.id)
    file_path = FAVORITE_PATH + author_id +'.txt'

    if not os.path.exists(file_path):
        await ctx.channel.send('<@' + author_id + '>님의 즐겨찾기 목록이 존재하지 않습니다.')
        return

    search_word = ''

    for i, arg in enumerate(args):
        if i > 0:
            search_word += arg + ' '

    search_word = search_word.strip()

    file = open(file_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    file.close()

    search_results = ''
    isExist = False;

    cnt = 0

    for line in lines:
        splited = line.split('\t')
        if search_word in splited[0]:
            cnt += 1
            search_results += str(cnt) + '\t"' + splited[0] + '" "' + splited[1] + '" "' + splited[2].rstrip() + '"\n'

    if not search_results == '':
        log(from_text(ctx), f'search_favorite {search_word} searched successfully')

        await ctx.author.send(ctx.author.name + f'님의 단축어 "{search_word}" 검색 결과 ({cnt}/{len(lines)}) \n'+ search_results)
    else:
        log(from_text(ctx), f'search_favorite {search_word} not found')
        await ctx.author.send(ctx.author.name + f'님의 단축어 "{search_word}" 검색 결과가 없습니다.')


# 즐겨찾기 사용
@bot.command(name='ㅋ')
async def send_favorite(ctx, *args):
    log(from_text(ctx), 'send_favorite command')

    shortcut_name = ''

    if len(args) <= 0:
        log(from_text(ctx), 'send_favorite wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. (!ㅋ "단축어")')
        return

    for arg in args:
        shortcut_name += arg + ' '

    shortcut_name = shortcut_name.strip()
    author_id = str(ctx.author.id)

    file_path = FAVORITE_PATH + author_id +'.txt'
    if not os.path.exists(file_path):
        await ctx.channel.send('<@' + author_id + '>님의 즐겨찾기 목록이 존재하지 않습니다.')
        return

    res = find_favorite(ctx, shortcut_name)
    if res[0] == '':
        log(from_text(ctx), f'send_favorite "{shortcut_name}" cannot found')
        await ctx.channel.send('<@' + author_id + f'>님의 즐겨찾기 목록에서 "{shortcut_name}" 단축어를 찾을 수 없습니다.')
        return

    await send_dccon(ctx, *res)


# 파일 줄 개수 조회
def get_file_line_cnt(file_path):
    if not os.path.exists(file_path):                  # 즐겨찾기 목록이 존재하지 않으면 0 반환
        return 0

    file = open(file_path, mode='rt', encoding='utf-8')
    count = len(file.readlines())
    file.close()

    return count

# 추가 시 중복 체크
def is_exactly_same_exist(ctx, shortcut_name):
    file_path = FAVORITE_PATH + str(ctx.author.id) +'.txt'

    exist = False

    file = open(file_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        splited = line.split('\t')
        if splited[0] == shortcut_name:
            log(from_text(ctx), f'add_favorite {shortcut_name} is exist.')
            exist = True
            break
    file.close()

    return exist

# 즐겨찾기 단축어로 탐색
# 패키지명과 디시콘명 가져오기. 단축어와 근접한 디시콘명 가져옴
def find_favorite(ctx, shortcut_name):
    file_path = FAVORITE_PATH + str(ctx.author.id) +'.txt'

    resultArr = ['', '']

    file = open(file_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        splited = line.split('\t')
        if shortcut_name in splited[0]:
            resultArr[0] = splited[1]                    # 반환할 패키지명 저장
            resultArr[1] = splited[2].rstrip('\n')       # 반환할 디시콘명 저장
            if shortcut_name == splited[0]:              # 단축어와 완전히 동일하면 탐색종료
                break
    file.close()

    return resultArr


# 즐겨찾기 백업
@bot.command(pass_context=True)
async def favorite_backup(ctx, *args):

    user_id = str(ctx.author.id)

    if len(args) == 2:                          # 인자가 1개인 경우에는 해당 사용자의 즐겨찾기 목록을 백업
        user_id = args[1]
    elif len(args) > 2:
        log(from_text(ctx), 'favorite_backup wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. (!즐찾 백업 "사용자ID")')
        return

    await send_favorites(ctx, user_id)


# 요청한 사용자에게 대상 사용자의 즐겨찾기 목록을 전송
@bot.command(pass_context=True)
async def send_favorites(ctx, user_id):
    fileName = user_id + '.txt'
    file_path = FAVORITE_PATH + fileName

    if (not os.path.exists(file_path)) or (get_file_line_cnt(file_path) == 0):
        await ctx.channel.send('<@' + user_id + '>님의 즐겨찾기 목록이 존재하지 않습니다.')
        return

    await ctx.author.send(file=File(file_path, fileName), content=ctx.author.name + '님의 즐겨찾기 목록을 업로드했습니다.')


# 즐겨찾기 복원
async def restore_favorites(ctx, *args):
    if not len(args) == 2:
        log(from_text(ctx), 'restore_favorites wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. (!즐찾 복원 "파일URL")')
        return

    url = args[1]
    user_id = str(ctx.author.id)
    save_file_path = FAVORITE_PATH + user_id + '.txt.tmp'

    download_file(url, save_file_path)                                                 # ID.txt.tmp 로 파일 임시로 저장

    new_favorites_line_length = get_file_line_cnt(save_file_path)

    if (new_favorites_line_length <= 0) or (new_favorites_line_length > FAVORITE_MAX): # 유저가 보낸 즐겨찾기 파일의 줄 수가 0보다 작거나 MAX보다 크면 교체하지 않음.
        log(from_text(ctx), 'restore_favorites ' + user_id + '\'s favorites restore blocked')
        await ctx.channel.send('<@' + user_id + '>님이 업로드한 즐겨찾기 파일이 빈 파일이거나 최대치를 넘깁니다. 복원할 수 없습니다.')
        os.remove(save_file_path)
        return

    a=save_file_path[:-4]
    shutil.move(save_file_path, save_file_path[:-4])                                   # 즐겨찾기 교체
    log(from_text(ctx), 'restore_favorites restored ' + user_id + '\'s favorites')
    await ctx.channel.send('<@' + user_id + '>님의 즐겨찾기 목록을 복원했습니다.')


def download_file(url, file_name = None):
	if not file_name:
		file_name = url.split('/')[-1]

	with open(file_name, "wb") as file:
            response = get(url)               
            file.write(response.content)


async def reset_favorites(ctx, *args):
    user_id = str(ctx.author.id)
    file_path = FAVORITE_PATH + user_id + '.txt'

    if os.path.exists(file_path):
        os.remove(file_path)

    log(from_text(ctx), 'reset_favorites reset ' + user_id + '\'s favorites')
    await ctx.channel.send('<@' + user_id + '>님의 즐겨찾기 목록을 리셋했습니다.')

############################################################################################################
############################################################################################################

# 캐시 클리어
@bot.command(name='캐시클리어')
async def clear_cache(ctx, *args):
    user_id = str(ctx.author.id)

    if not (OWNER_ID == user_id):
        log(from_text(ctx), f'{user_id} attempted to clear cache.')
        await ctx.channel.send('권한이 없습니다. 관리자에게 문의하세요.')
        return

    if os.path.isdir(CACHE_PATH) and not os.path.islink(CACHE_PATH):
        shutil.rmtree(CACHE_PATH)
        log(from_text(ctx), f'cache cleared by shutil.rmtree({CACHE_PATH})')
    elif os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)
        log(from_text(ctx), f'cache cleared by os.remove({CACHE_PATH})')

    await ctx.channel.send('캐시를 클리어 했습니다.')

# 캐시 추가
async def acc_cache(package_name, idx, file_name, bytes):
    if not os.path.isdir(CACHE_PATH):
        if not create_directory(CACHE_PATH):                                        # 캐시 폴더가 존재하지 않으면 생성. 생성 실패시 오류메시지 출력.
            log('SYSTEM', 'creating cache directory failed')

    # 캐시 개수 체크
    if get_cache_count() >= CACHE_MAX:
        remove_lastest_cache()

    # 이미지 저장
    with open(CACHE_PATH + f'{file_name}','wb') as out: ## Open temporary file as bytes
        out.write(bytes.read())                         ## Read bytes into file

    # 캐시 인덱스에 append
    # 캐시 인덱스에 중복추가안하게 해라
    file_path = CACHE_PATH + 'cacheIdx.txt'
    file = open(file_path, mode='at', encoding='utf-8')
    file.write(package_name + '\t' + idx + '\t' + file_name + '\n')
    file.close()


# 캐시 탐색
# 디시콘 패키지명과 idx(디시콘명)으로 탐색해서, 있으면 파일명 반환
def get_cache_file_name(package_name, idx):
    file_path = CACHE_PATH + 'cacheIdx.txt'

    cache_file_name = ''

    if not os.path.isdir(CACHE_PATH):
        return cache_file_name

    file = open(file_path, mode='rt', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        splited = line.split('\t')
        if (package_name == splited[0]) and (idx == splited[1]):
            cache_file_name = splited[2].rstrip('\n')                   # 반환할 디시콘 파일명
            break
    file.close()

    if not os.path.exists(CACHE_PATH + cache_file_name):               # 캐시 이미지가 실제로 존재하지 않으면
        cache_file_name

    return cache_file_name

# 캐시 개수 조회
def get_cache_count():
    file_path = CACHE_PATH + 'cacheIdx.txt'

    if not os.path.exists(file_path):                  # 캐시 인덱스 파일이 존재하지 않으면 0 반환
        return 0

    file = open(file_path, mode='rt', encoding='utf-8')
    count = len(file.readlines())
    file.close()

    return count

# 캐시 리스트에서 한줄 삭제 + 이미지 삭제
def remove_lastest_cache():
    file_path = CACHE_PATH + 'cacheIdx.txt'
    file = open(file_path, mode='rt', encoding='utf-8')

    # 헤드(가장 오래된 캐시) 탐색
    lastest_cache = file.readline()
    splited = lastest_cache.split('\t')
    lastest_cache_path = CACHE_PATH + splited[2].rstrip('\n')
    
    # 나머지줄 로드
    lines = file.readlines()

    new_lines = ''
    isExist = False;

    for line in lines:
        new_lines += line

    file.close()

    # 나머지줄만 저장
    file = open(file_path, mode='wt', encoding='utf-8')
    file.writelines(new_lines)
    file.close()

    # 가장 오래된 캐시 삭제
    if os.path.exists(lastest_cache_path):
        os.remove(lastest_cache_path)


# 폴더 생성
def create_directory(path):
    try:
        if not(os.path.isdir(path)):
            log('SYSTEM', f'creating directory at {path}')
            os.makedirs(os.path.join(path))
            log('SYSTEM', f'directory created at {path}')
        
        return True
    except OSError as e:
        if e.errno != errno.EEXIST:
            log(from_text(ctx), f'failed to create directory at {path}!')
        
        return False

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
    log(from_text(ctx), error)
    await ctx.channel.send(error)


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
