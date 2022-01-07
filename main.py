import os
from discord import Game, Embed, File
from discord.ext import commands
from discord.flags import Intents
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option, create_choice

from logger.logger import log, system_log
from util.directory_util import create_directory
from env.env_loader import load_env
import env.hassan_env as hassan_env
from favorite import favorite_controller
from cache import cache_controller
from util.string_util import combine_words
from dccon import core
from error.favorite_error import FavoriteError
from view import help

bot = commands.Bot(command_prefix='!', intents=Intents.default())
slash = SlashCommand(bot, sync_commands=True)

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

@slash.slash(
    name="help",
    description="도움말을 볼 수 있습니다.",
    options=[]
)
async def slash_help(ctx):
    await help.send_help(ctx)

@bot.command(name='도움')
async def manual_help(ctx):
    await help.send_help(ctx)

@slash.slash(
    name="about",
    description="디시콘 핫산에 대해 알아볼 수 있습니다.",
)
async def slash_about(ctx):
    await help.send_about(ctx)

@bot.command(name='대하여')
async def manual_about(ctx):
    await help.send_about(ctx)

############################################################ 디시콘 ############################################################

@slash.slash(
    name="dccon",
    description="디시콘을 사용할 수 있습니다.",
    options=[
        create_option(
            name="package",
            description="디시콘 패키지 이름",
            option_type=3,
            required=True
        ),
        create_option(
            name="name",
            description="패키지 내 파일 이름",
            option_type=3,
            required=True
        )
    ],
    connector={
        'package': 'package_name', 
        'name': 'idx'
        }
)
async def slash_send_dccon(ctx, package_name, idx):
    await core.send_dccon(ctx, package_name, idx)

@bot.command(name='콘')
async def manual_send_dccon(ctx, *args):
    if not args or len(args) > 2:
        log(ctx, 'empty args')
        await ctx.channel.send('사용법을 참고해주세요. (!도움)' + '\n디시콘 패키지명이나 디시콘명에 공백이 있을 경우 큰따옴표로 묶어야 합니다.')
        return

    if len(args) < 2:
        await core.send_dccon_list(ctx, args[0])
    else:
        await core.send_dccon(ctx, args[0], args[1])
        
@slash.slash(
    name="dccon_list",
    description="디시콘 목록을 조회할 수 있습니다.",
    options=[
        create_option(
            name="package",
            description="디시콘 패키지 이름",
            option_type=3,
            required=True
        )
    ],
    connector={
        'package': 'package_name'
        }
)
async def slash_send_dccon_list(ctx, package_name):
    await core.send_dccon_list(ctx, package_name)
        

############################################################ 즐겨찾기 ############################################################

@slash.slash(
    name="favor",
    description="단축어로 저장해둔 디시콘을 보낼 수 있습니다.",
    options=[
        create_option(
            name="단축어",
            description="단축어",
            option_type=3,
            required=True
        )
    ],
    connector={
        '단축어': 'keyword'
        }
)
async def slash_send_favorite(ctx, keyword):
    await manual_send_favorite(ctx, keyword)

# 즐겨찾기
@bot.command(name='즐찾')
async def favorite_command_selector(ctx, *args):
    if not args:
        help.send_help_favorite(ctx)
        return

    if not os.path.isdir(hassan_env.FAVORITE_PATH):
        if not create_directory(hassan_env.FAVORITE_PATH):                                        # 즐겨찾기 폴더가 존재하지 않으면 생성. 생성 실패시 오류메시지 출력.
            await ctx.send('경로 생성에 실패하였습니다. 관리자에게 문의하세요!')
    
    command = args[0]

    if command == '추가':
        await add_favorite(ctx, *args);

    elif command == '목록':
        await show_favorites(ctx)

    elif command == '삭제':
        await delete_favorite(ctx, *args)

    elif command == '검색':
        await search_favorite(ctx, *args)

    elif command == '사용':
        await ctx.send('즐겨찾기 사용은 !ㅋ "단축어" 으로 사용해주세요.')

    elif command == '백업':
        await favorite_backup(ctx, *args)

    elif command == '복원':
        await restore_favorites(ctx, *args)

    elif command == '초기화':
        await reset_favorites(ctx, *args)

    else:
        await ctx.send('올바르지 않은 명령어입니다. 사용법을 참고해주세요. (!즐찾)')

async def add_favorite(ctx, *args):
    log(ctx, 'add_favorite command')

    if not len(args) == 4:
        log(ctx, 'add_favorite wrong arg count')
        await ctx.send('인자수가 올바르지 않습니다. (!즐찾 추가 "단축어" "디시콘 패키지명" "디시콘 명")')
        return

    shortcut_name = args[1]
    package_name = args[2]
    dccon_name = args[3]

    msg =  favorite_controller.add_favorite(ctx, shortcut_name, package_name, dccon_name)
   
    await ctx.send(msg)


@slash.slash(
    name="favorite_list",
    description="단축어 목록을 조회합니다.",
)
async def slash_show_favorites(ctx):
    await show_favorites(ctx)

# 즐겨찾기 목록 조회
async def show_favorites(ctx):
    await ctx.defer()
    result = favorite_controller.show_favorites(ctx)
    for msg in result:
        await ctx.author.send(msg)
    await ctx.send('DM으로 단축어 목록을 전송했습니다.')

# 즐겨찾기 삭제
async def delete_favorite(ctx, *args):
    log(ctx, 'delete_favorite command')

    if len(args) < 2:
        log(ctx, 'delete_favorite wrong arg count')
        await ctx.send('인자수가 올바르지 않습니다. (!즐찾 삭제 "단축어")')
        return

    shortcut_name = combine_words(args[1:])

    msg = favorite_controller.delete_favorite(ctx, shortcut_name)
    await ctx.send(msg)


# 즐겨찾기 검색
async def search_favorite(ctx, *args):
    log(ctx, 'search_favorite command')

    if len(args) < 2:
        log(ctx, 'search_favorite wrong arg count')
        await ctx.send('인자수가 올바르지 않습니다. (!즐찾 검색 "단축어")')
        return

    keyword = combine_words(args[1:])
    msg = favorite_controller.serach_favorites(ctx, keyword)

    await ctx.author.send(msg)


# 즐겨찾기 사용
@bot.command(name='ㅋ')
async def manual_send_favorite(ctx, *args):
    log(ctx, 'send_favorite command')

    if len(args) <= 0:
        log(ctx, 'send_favorite wrong arg count')
        await ctx.send('인자수가 올바르지 않습니다. (!ㅋ "단축어")')
        return

    shortcut_name = combine_words(args)

    try:
        result_pair = favorite_controller.find_favorite_one(ctx, shortcut_name)
        await manual_send_dccon(ctx, *result_pair)
    except FavoriteError as e:
        await ctx.send(str(e))
    

# 즐겨찾기 백업
@bot.command(pass_context=True)
async def favorite_backup(ctx, *args):

    user_id = str(ctx.author.id)

    if len(args) == 2:                          # 인자가 1개인 경우에는 해당 사용자의 즐겨찾기 목록을 백업
        user_id = args[1]
    elif len(args) > 2:
        log(ctx, 'favorite_backup wrong arg count')
        await ctx.send('인자수가 올바르지 않습니다. (!즐찾 백업 "사용자ID")')
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
        await ctx.send('DM으로 즐겨찾기 목록을 전송했습니다.')
    except FavoriteError as e:
        await ctx.send(str(e))


# 즐겨찾기 복원
async def restore_favorites(ctx, *args):
    if not len(args) == 2:
        log(ctx, 'restore_favorites wrong arg count')
        await ctx.send('인자수가 올바르지 않습니다. (!즐찾 복원 "파일URL")')
        return

    download_url = args[1]
    msg = favorite_controller.resotre_favorites(ctx, download_url)
    await ctx.send(msg)

async def slash_reset_favorites(ctx):
    await reset_favorites(ctx)

# 즐겨찾기 초기화
async def reset_favorites(ctx):
    msg = favorite_controller.reset_favorites(ctx)
    await ctx.send(msg)

############################################################################################################

# 캐시 정리
@bot.command(name='캐시 정리')
async def controller_clear_cache(ctx, *args):
    user_id = str(ctx.author.id)
    owner_id = hassan_env.OWNER_ID                            ## TODO: 해당 서버의 주인 id get
    
    msg = cache_controller.clear_cache(user_id, owner_id)

    await ctx.send(msg)

@bot.event
async def on_command_error(ctx, error):
    log(ctx, error)
    await ctx.send(error)

if __name__ == "__main__":
    bot.run(hassan_env.BOT_TOKEN)
