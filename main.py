import os
from discord import Game, Embed, File
from discord.ext import commands

from log.logger import log, system_log
from util.directory_util import create_directory
from cache import cache_controller
from env.env_loader import load_env
import env.hassan_env as hassan_env
from favorite import favorite_controller
from util.string_util import combine_words
from dccon import core
from error.favorite_error import FavoriteError

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
    if not args or len(args) > 2:
        log(ctx, 'empty args')
        await ctx.channel.send('사용법을 참고해주세요. (!도움)')
        await ctx.channel.send('디시콘 패키지명이나 디시콘명에 공백이 있을 경우 큰따옴표로 묶어야 합니다.')
        return

    package_name = args[0]

    if len(args) < 2:
        await core.send_dccon_list(ctx, package_name)
    else:
        idx = args[1]
        await core.send_dccon(ctx, package_name, idx)
        

############################################################ 모듈화 ############################################################


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

    try:
        result_pair = favorite_controller.find_favorite_one(ctx, shortcut_name)
        await send_dccon(ctx, *result_pair)
    except FavoriteError as e:
        await ctx.channel.send(str(e))
    

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
    try:
        results = favorite_controller.get_favorites_file(ctx, user_id)
        msg = results[0]
        file_path = results[1]
        file_name = results[2]
        
        await ctx.author.send(file=File(file_path, file_name), content=msg)
    except FavoriteError as e:
        await ctx.channel.send(str(e))


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

# 캐시 정리
@bot.command(name='캐시 정리')
async def controller_clear_cache(ctx, *args):
    user_id = str(ctx.author.id)
    owner_id = hassan_env.OWNER_ID                            ## TODO: 해당 서버의 주인 id get
    
    msg = cache_controller.clear_cache(user_id, owner_id)

    await ctx.channel.send(msg)

@bot.event
async def on_command_error(ctx, error):
    log(ctx, error)
    await ctx.channel.send(error)

if __name__ == "__main__":
    bot.run(hassan_env.BOT_TOKEN)
