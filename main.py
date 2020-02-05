import requests
import os
from datetime import datetime
from io import BytesIO
from bs4 import BeautifulSoup
from discord import Game, Embed, File
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()  # load bot token


def from_text(ctx):
    # msg_fr = msg.server.name + ' > ' + msg.channel.name + ' > ' + msg.author.name
    # msg.server --> msg.guild
    # https://discordpy.readthedocs.io/en/latest/migrating.html#server-is-now-guild
    return f'{ctx.guild.name} > {ctx.channel.name} > {ctx.author.name}'


def log(fr, text):
    print(f'{fr} | {str(datetime.now())} | {text}')  # TODO: 시간대 조정


BOT_TOKEN = os.getenv('BOT_TOKEN')
DCCON_HOME_URL = 'https://dccon.dcinside.com/'
DCCON_SEARCH_URL = 'https://dccon.dcinside.com/hot/1/title/'
DCCON_DETAILS_URL = 'https://dccon.dcinside.com/index/package_detail'
EMBED_COLOR = 0x4559e9
INVITE_URL = 'https://discordapp.com/oauth2/authorize?client_id=629279090716966932&scope=bot&permissions=101376'
FAVORITE_PATH = 'favorites/'
FAVORITE_MAX = 50


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


@bot.command(name='도움')
async def help(ctx):
    log(from_text(ctx), 'help command')
    embed = Embed(title='안녕하세요! 디시콘 핫산이에요!',
                  description='명령어들은 아래에서 전부 보실 수 있어요.',
                  color=EMBED_COLOR)
    embed.add_field(name='사용 방법', value='!콘 "디시콘 패키지 제목" "콘 이름"', inline=False)
    embed.add_field(name='사용 예시 1', value='!콘 멘헤라콘 15, !콘 "마히로콘 리메이크" 꿀잠, !콘 "좋은말콘 스페셜 에디션" 응원, ...', inline=False)
    embed.add_field(name='사용 예시 2', value='!콘 "나나히라 라인", !콘 카구야는인사받고싶어, ... (디시콘 패키지 이름만 입력 시 디시콘 목록 출력)', inline=False)
    embed.add_field(name='명령어', value='!콘, !도움, !대하여, !초대링크, !ㅋ, !즐찾', inline=False)

    embed.set_footer(text='그코좆망겜')
    await ctx.channel.send(embed=embed)


@bot.command(name='초대링크')
async def invite_link(ctx):
    log(from_text(ctx), 'invite_link command')
    await ctx.channel.send(f'봇 초대 링크 : {INVITE_URL}')


@bot.command(name='대하여')
async def about(ctx):
    log(from_text(ctx), 'about command')
    embed = Embed(title='디시콘 핫산',
                  description='디시콘을 디스코드에서 쓸 수 있게 해주는 디스코드 봇입니다.',
                  color=EMBED_COLOR)
    embed.add_field(name='Repository', value='https://github.com/Dogdriip/dccon_hassan', inline=False)
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

    ############################################################################################################
    # respect https://github.com/gw1021/dccon-downloader/blob/master/python/app.py#L7:L18

    # TODO: 변수명 간단히

    s = requests.Session()

    package_search_req = s.get(DCCON_SEARCH_URL + package_name)
    package_search_html = BeautifulSoup(package_search_req.text, 'html.parser')
    package_search_is_empty = package_search_html.select('#right_cont_wrap > div > div.dccon_search_none > p > span')   # 검색결과가 없는경우 체크
    if not package_search_is_empty:
        package_search_list = package_search_html.select('#right_cont_wrap > div > div.dccon_listbox > ul > li')

    try:
        isExactlySameExist = False                                                                                      # 2020-02-04 완전히 동일한 패키지명이 선택되도록 수정.
        for searched_package in package_search_list:                                                                    # 검색결과 중 디시콘 패키지명과 완전히 일치한 패키지가 있는지 탐색한다.
            searched_package_name = searched_package.find('strong', {'class' : 'dcon_name'}).string
            if searched_package_name == package_name:                                                                   # 완전히 동일한 패키지명이 탐색되면 해당 패키지 선택한다.
                target_package = searched_package
                isExactlySameExist = True
                break

        if not isExactlySameExist:                                                                                      # 완전히 동일한 패키지명이 탐색되지 않아 첫번째 패키지를 선택한다.
            target_package = package_search_list[0]                                                                     # pick first dccon package (bs4 obj) from search list
    except IndexError as e:  # maybe no search result w/ IndexError?
        log(from_text(ctx), 'error! (maybe no search result) : ' + str(e))
        await ctx.channel.send(f'"{package_name}" 디시콘 패키지 정보를 찾을 수 없습니다.')
    except UnboundLocalError as e:
        log(from_text(ctx), 'error! (maybe no search result) : ' + str(e))
        await ctx.channel.send(f'"{package_name}" 디시콘 패키지 정보를 찾을 수 없습니다.')
    else:
        target_package_num = target_package.get('package_idx')  # get dccon number of target dccon package
        log(from_text(ctx), 'processing with: ' + target_package_num)

        # for i in package_search_req.cookies:
        #     print(i.name, i.value)

        package_detail_req = s.post(DCCON_DETAILS_URL,
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

        # 검색 결과로 바꿔치기
        package_name = package_detail_json['info']['title']

        if list_print_mode:
            available_dccon_list = []
            for dccon in package_detail_json['detail']:
                available_dccon_list.append(dccon['title'])

            await ctx.channel.send(f'"{package_name}"에서 사용 가능한 디시콘 : ' + ', '.join(available_dccon_list).rstrip(', '))
            # 디시콘 링크 알려줌
            await ctx.channel.send('미리보기 URL : ' + package_search_req.request.url + '#' + target_package_num)
        else:
            succeed = False
            for dccon in package_detail_json['detail']:
                if dccon['title'] == idx:
                    dccon_img = "http://dcimg5.dcinside.com/dccon.php?no=" + dccon['path']
                    dccon_img_request = s.get(dccon_img, headers={'Referer': DCCON_HOME_URL})

                    buffer = BytesIO(dccon_img_request.content)
                    filename = package_name + '_' + dccon['title'] + '.' + dccon['ext']

                    # 디시콘 표기 + 콘 사용자 표시
                    sender_tag = "<@" + str(ctx.author.id) + ">"
                    await ctx.channel.send(file=File(buffer, filename), content=sender_tag)
                    succeed = True
                    break

            if succeed:
                log(from_text(ctx), 'succeed')
            else:
                log(from_text(ctx), 'not found')

                await ctx.channel.send(f'"{package_name}" 디시콘 패키지에서 "{idx}" 디시콘을 찾지 못했습니다.')
                await ctx.channel.send('인자로 패키지 이름만 넘길 경우 사용 가능한 디시콘 목록이 출력됩니다.')
    #
    ############################################################################################################


# 즐겨찾기
@bot.command(name='즐찾')
async def favorite_manage(ctx, *args):
    if not args:
        log(from_text(ctx), 'favorite_help command')
        embed = Embed(title='안녕하세요! 디시콘 핫산이에요!',
                  description=f'즐겨찾기는 개인당 {FAVORITE_MAX}개 까지만 등록 가능해요.\n띄워쓰기를 포함하려면 "로 묶어주세요.\n사용가능한 명령어로 등록, 목록, 삭제, 사용이 있어요.',
                  color=EMBED_COLOR)
        embed.add_field(name='즐겨찾기 등록', value='!즐찾 등록 "단축명" "디시콘 패키지 제목" "콘 이름"', inline=False)
        embed.add_field(name='사용 예시', value='!즐찾 멘15 멘헤라콘 15, !즐찾 마히리메꿀잠 "마히로콘 리메이크" 꿀잠 , !즐찾 좋은말콘응원 "좋은말콘 스페셜 에디션" 응원, ...', inline=False)
        embed.add_field(name='즐겨찾기 목록 확인', value='!즐찾 목록', inline=False)
        embed.add_field(name='즐겨찾기 삭제', value='!즐찾 삭제 "단축명"', inline=False)
        embed.add_field(name='사용 예시', value='!즐찾 삭제 멘15, !즐찾 삭제 마히리메꿀잠, !즐찾 삭제 좋은말콘응원, ...', inline=False)
        embed.add_field(name='즐겨찾기 사용', value='!ㅋ "단축명"', inline=False)
        embed.add_field(name='사용 예시', value='!ㅋ 멘15, !ㅋ 마히리메꿀잠, !ㅋ 좋은말콘응원, ...', inline=False)
        embed.set_footer(text='몬헌좆망겜')
        await ctx.channel.send(embed=embed)
        return

    if not create_favorite_path():                                                               # 즐겨찾기 폴더가 존재하지 않으면 생성. 생성 실패시 오류메시지 출력.
        await ctx.channel.send('즐겨찾기 폴더 생성에 실패하였습니다. 관리자에게 문의하세요!')
        return
    
    if args[0] == '등록':
        await favorite_register(ctx, *args);
        return

    elif args[0] == '목록':
        await favorite_list(ctx)
        return

    elif args[0] == '삭제':
        await ctx.channel.send('삭제삭제맨')
        await favorite_delete(ctx, *args)
        return

    elif args[0] == '사용':
        await ctx.channel.send('즐겨찾기 사용은 !ㅋ "단축명" 으로 사용해주세요.')
        return
    
    else:
        await ctx.channel.send('올바르지 않은 명령어입니다. 사용법을 참고해주세요. (!즐찾)')


# 즐겨찾기 등록
async def favorite_register(ctx, *args):
    log(from_text(ctx), 'favorite_register command')

    if not len(args) == 4:
        log(from_text(ctx), 'favorite_register wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. 사용법을 참고해주세요. (!즐찾)')
        return

    shortcut_name = args[1]
    package_name = args[2]
    dccon_name = args[3]

    registed_count = get_favorite_count(ctx)

    if registed_count >= FAVORITE_MAX:                                          # 즐겨찾기 등록횟수 체크
        log(from_text(ctx), 'favorite_delete cannot register favorite (max)')
        await ctx.channel.send('더 이상 즐겨찾기를 등록할 수 없습니다. 즐겨찾기 삭제 후 시도해주세요.')
        return
    elif registed_count > 0 and find_favorite(ctx, shortcut_name)[0] != '':     # 해당 단축어가 이미 등록되어있는지 체크
        log(from_text(ctx), f'favorite_delete "{shortcut_name}" already exists.')
        await ctx.channel.send('해당 단축명으로 등록된 즐겨찾기가 이미 존재합니다.')
        return 

    filePath = 'favorites/' + str(ctx.author.id) +'.txt'
    file = open(filePath, mode='at', encoding='utf-8')
    file.write(shortcut_name + '\t' + package_name + '\t' + dccon_name + '\n')
    file.close()

    await ctx.channel.send('<@' + str(ctx.author.id) + f'>님의 즐겨찾기가 등록되었습니다. (등록된 즐겨찾기 수 : {registed_count + 1})')
    return


# 즐겨찾기 목록 조회
async def favorite_list(ctx):
    log(from_text(ctx), 'favorite_list command')
    
    filePath = 'favorites/' + str(ctx.author.id) +'.txt'

    if not favorite_isPathExist(filePath):
        await ctx.channel.send('<@' + str(ctx.author.id) + '>님의 즐겨찾기 목록이 존재하지 않습니다.')
        return

    favorite_lists = '\n'
    cnt = 0

    file = open(filePath, mode='rt', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        cnt += 1
        favorite_lists += str(cnt) + '\t' + line
    file.close()

    # 즐겨찾기 목록 표시 + 사용자 표시
    sender_tag = '<@' + str(ctx.author.id) + f'>님의 즐겨찾기 목록이에요. ({cnt}/{FAVORITE_MAX})\n'
    header = '#\t단축명\t패키지명\t디시콘명'

    await ctx.channel.send(sender_tag + header + favorite_lists)


# 즐겨찾기 삭제
async def favorite_delete(ctx, *args):
    log(from_text(ctx), 'favorite_delete command')

    if not len(args) == 2:
        log(from_text(ctx), 'favorite_delete wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. 사용법을 참고해주세요. (!즐찾)')
        return

    filePath = 'favorites/' + str(ctx.author.id) +'.txt'

    if not favorite_isPathExist(filePath):
        await ctx.channel.send('<@' + str(ctx.author.id) + '>님의 즐겨찾기 목록이 존재하지 않습니다.')
        return

    shortcut_name = args[1]

    file = open(filePath, mode='rt', encoding='utf-8')
    lines = file.readlines()

    new_lines = ''
    isExist = False;

    for line in lines:
        splited = line.split('\t')
        if splited[0] == shortcut_name:
            isExist = True
        else:
            new_lines += line

    file.close()

    if isExist:
        file = open(filePath, mode='wt', encoding='utf-8')
        file.writelines(new_lines)
        file.close()

        log(from_text(ctx), f'favorite_delete "{shortcut_name}" deleted')
        await ctx.channel.send('<@' + str(ctx.author.id) + f'>님의 즐겨찾기 목록에서 "{shortcut_name}" 단축어가 삭제되었습니다.')
    else:
        log(from_text(ctx), f'favorite_delete "{shortcut_name}" cannot found')
        await ctx.channel.send('<@' + str(ctx.author.id) + f'>님의 즐겨찾기 목록에서 "{shortcut_name}" 단축어를 찾을 수 없습니다.')

# 즐겨찾기 사용
@bot.command(name='ㅋ')
async def favorite_send(ctx, *args):
    log(from_text(ctx), 'favorite_send command')

    if not len(args) == 1:
        log(from_text(ctx), 'favorite_send wrong arg count')
        await ctx.channel.send('인자수가 올바르지 않습니다. 사용법을 참고해주세요. (!즐찾)')
        return

    shortcut_name = args[0]

    res = find_favorite(ctx, shortcut_name)
    if res[0] == '':
        log(from_text(ctx), f'favorite_send "{shortcut_name}" cannot found')
        await ctx.channel.send('<@' + str(ctx.author.id) + f'>님의 즐겨찾기 목록에서 "{shortcut_name}" 단축어를 찾을 수 없습니다.')
        return

    await send_dccon(ctx, *res)


# 즐겨찾기 관리 폴더 생성
def create_favorite_path():
    try:
        if not(os.path.isdir(FAVORITE_PATH)):                # favorites 폴더가 없으면 생성
            os.makedirs(os.path.join(FAVORITE_PATH))
        return True
    except OSError as e:
        if e.errno != errno.EEXIST:
            log(from_text(ctx), 'failed to create favorite directory!')
            return False


# 등록된 즐겨찾기 개수 조회
def get_favorite_count(ctx):
    filePath = 'favorites/' + str(ctx.author.id) +'.txt'

    if not favorite_isPathExist(filePath):                  # 즐겨찾기 목록이 존재하지 않으면 0 반환
        return 0

    file = open(filePath, mode='rt', encoding='utf-8')
    count = len(file.readlines())
    file.close()

    return count


# 즐겨찾기 사용 / 등록 시 중복 체크
def find_favorite(ctx, shortcut_name):
    filePath = 'favorites/' + str(ctx.author.id) +'.txt'

    resultArr = ['', '']

    file = open(filePath, mode='rt', encoding='utf-8')
    lines = file.readlines()
    for line in lines:
        splited = line.split('\t')
        if splited[0] == shortcut_name:
            log(from_text(ctx), 'favorite_register shortcut_name found')
            resultArr[0] = splited[1]                    # 반환할 패키지명 저장
            resultArr[1] = splited[2].rstrip('\n')       # 반환할 디시콘명 저장
            break
    file.close()

    return resultArr


# 즐겨찾기 관리 폴더가 있는지, 해당 파일이 있는지 체크함.
def favorite_isPathExist(filePath):
    if not(os.path.isdir(FAVORITE_PATH)):
        return False

    if not os.path.exists(filePath):
        return False

    return True

@bot.event
async def on_command_error(ctx, error):
    log(from_text(ctx), error)
    await ctx.channel.send(error)


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
