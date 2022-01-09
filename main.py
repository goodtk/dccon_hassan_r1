import os
from discord import Game
from discord.ext import commands
from discord.flags import Intents
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option

from logger.logger import log
from util.directory_util import create_directory
from env.env_loader import load_env
import env.hassan_env as hassan_env
from favorite import favorite_controller
from cache import cache_controller
from util.string_util import combine_words
from dccon import dccon_controller
from view import help, console, error

bot = commands.Bot(command_prefix='!', intents=Intents.default())
slash = SlashCommand(bot, sync_commands=True)

load_env()

@bot.event
async def on_ready():
    await bot.change_presence(activity=Game(name='!도움'))
    console.print_on_ready()

@slash.slash(
    name="도움",
    description="도움말을 볼 수 있습니다.",
    options=[]
)
async def slash_help(ctx):
    await help.send_help(ctx)

@bot.command(name='도움')
async def manual_help(ctx):
    await help.send_help(ctx)

@slash.slash(
    name="대하여",
    description="디시콘 핫산에 대해 알아볼 수 있습니다.",
)
async def slash_about(ctx):
    await help.send_about(ctx)

@bot.command(name='대하여')
async def manual_about(ctx):
    await help.send_about(ctx)

############################################################ 디시콘 ############################################################

@slash.slash(
    name="콘",
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
    await dccon_controller.send_dccon(ctx, package_name, idx)

@bot.command(name='콘')
async def manual_send_dccon(ctx, *args):
    if not args or len(args) > 2:
        return await error.send_send_dccon_error(ctx)
        
    package_name = args[0]

    if len(args) < 2:
        await dccon_controller.send_dccon_list(ctx, package_name)
    else:
        idx = args[1]
        await dccon_controller.send_dccon(ctx, package_name, idx)
        
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
    await dccon_controller.send_dccon_list(ctx, package_name)
        

############################################################ 즐겨찾기 ############################################################

# 즐겨찾기
@bot.command(name='즐찾')
async def favorite_command_selector(ctx, *args):
    if not args:
        return await error.send_error_favorite(ctx, '인자')

    if not os.path.isdir(hassan_env.FAVORITE_PATH):
        if not create_directory(hassan_env.FAVORITE_PATH):
            await error.send_error_directory_create(ctx)
    
    command = args[0]

    if command == '추가':
        await manual_add_favorite(ctx, *args);

    elif command == '목록':
        await manual_show_favorites(ctx)

    elif command == '삭제':
        await manual_delete_favorite(ctx, *args)

    elif command == '검색':
        await manual_search_favorite(ctx, *args)

    elif command == '백업':
        await manual_favorite_backup(ctx, *args)

    elif command == '복원':
        await manual_restore_favorites(ctx, *args)

    elif command == '초기화':
        await manual_reset_favorites(ctx)

    else:
        await error.send_error_favorite(ctx)


# 즐겨찾기 추가
@slash.slash(
    name="즐겨찾기_추가",
    description="즐겨찾기를 추가할 수 있습니다.",
    options=[
        create_option(
            name="keyword",
            description="단축어",
            option_type=3,
            required=True
        ),
        create_option(
            name="package",
            description="디시콘 패키지 이름",
            option_type=3,
            required=True
        ),
        create_option(
            name="name",
            description="콘 이름",
            option_type=3,
            required=True
        )
    ],
    connector={
        'keyword': 'keyword',
        'package': 'package_name',
        'name': 'dccon_name'
        }
)
async def slash_add_favorite(ctx, keyword, package_name, dccon_name):
    await favorite_controller.add_favorite(ctx, keyword, package_name, dccon_name)

async def manual_add_favorite(ctx, *args):
    if not len(args) == 4:
        log(ctx, 'add_favorite wrong arg count')
        return await error.send_error_add_favorite(ctx)

    keyword = args[1]
    package_name = args[2]
    dccon_name = args[3]

    await favorite_controller.add_favorite(ctx, keyword, package_name, dccon_name)


# 즐겨찾기 목록 조회
@slash.slash(
    name="즐겨찾기_목록_조회",
    description="단축어 목록을 조회합니다.",
)
async def slash_show_favorites(ctx):
    await favorite_controller.show_favorites(ctx)

async def manual_show_favorites(ctx):
    await favorite_controller.show_favorites(ctx)

@slash.slash(
    name="즐겨찾기_삭제",
    description="단축어를 삭제합니다.",
    options=[
        create_option(
            name="keyword",
            description="삭제할 단축어",
            option_type=3,
            required=True
        )
    ],
    connector={
        'keyword': 'keyword'
        }
)
async def slash_delete_favorite(ctx, keyword):
    await favorite_controller.delete_favorite(ctx, keyword)


# 즐겨찾기 삭제
async def manual_delete_favorite(ctx, *args):
    log(ctx, 'delete_favorite command')

    if len(args) < 2:
        log(ctx, 'delete_favorite wrong arg count')
        return await error.send_error_delete_favorite(ctx)

    keyword = combine_words(args[1:])
    await favorite_controller.delete_favorite(ctx, keyword)


# 즐겨찾기 검색
@slash.slash(
    name="즐겨찾기_검색",
    description="단축어를 검색합니다.",
    options=[
        create_option(
            name="keyword",
            description="검색할 단축어",
            option_type=3,
            required=True
        )
    ],
    connector={
        'keyword': 'keyword'
        }
)
async def slash_search_favorite(ctx, keyword):
    await favorite_controller.serach_favorites(ctx, keyword)

async def manual_search_favorite(ctx, *args):
    log(ctx, 'search_favorite command')

    if len(args) < 2:
        log(ctx, 'search_favorite wrong arg count')
        await ctx.send('인자수가 올바르지 않습니다. (!즐찾 검색 "단축어")')
        return

    keyword = combine_words(args[1:])
    await favorite_controller.serach_favorites(ctx, keyword)


# 즐겨찾기 사용
@slash.slash(
    name="ㅋ",
    description="단축어로 저장해둔 디시콘을 보낼 수 있습니다.",
    options=[
        create_option(
            name="keyword",
            description="단축어",
            option_type=3,
            required=True
        )
    ],
    connector={
        'keyword': 'keyword'
        }
)
async def slash_send_favorite(ctx, keyword):
    await favorite_controller.send_favorite(ctx, keyword)

@bot.command(name='ㅋ')
async def manual_send_favorite(ctx, *args):
    if len(args) <= 0:
        log(ctx, 'send_favorite wrong arg count')
        return await error.send_error_send_favorite(ctx)

    keyword = combine_words(args)
    await favorite_controller.send_favorite(ctx, keyword)
    

# 즐겨찾기 백업
@slash.slash(
    name="즐겨찾기_백업",
    description="등록한 단축어 목록을 받을 수 있습니다.",
)
async def slash_favorite_backup(ctx):
    await favorite_controller.send_favorites_file(ctx, str(ctx.author.id))

@bot.command(pass_context=True)
async def manual_favorite_backup(ctx, *args):
    if len(args) > 0:
        log(ctx, 'favorite_backup wrong arg count')
        return error.send_error_backup_favorite(ctx)

    await favorite_controller.send_favorites_file(ctx, str(ctx.author.id))


# 즐겨찾기 복원
@slash.slash(
    name="즐겨찾기_복원",
    description="단축어 목록을 복원합니다. 단축어 목록 텍스트 파일을 디스코드에 업로드하고, 해당 url을 넣어주세요.",
    options=[
        create_option(
            name="download_url",
            description="단축어 텍스트 파일을 다운로드 할 수 있는 url",
            option_type=3,
            required=True
        )
    ],
    connector={
        'download_url': 'download_url'
        }
)
async def slash_restore_favorites(ctx, download_url):
    await favorite_controller.resotre_favorites(ctx, download_url)

async def manual_restore_favorites(ctx, *args):
    if not len(args) == 2:
        log(ctx, 'restore_favorites wrong arg count')
        return await error.send_error_restore_favorite(ctx)

    download_url = args[1]
    await favorite_controller.resotre_favorites(ctx, download_url)


# 즐겨찾기 초기화
async def manual_reset_favorites(ctx):
    await favorite_controller.reset_favorites(ctx)

############################################################################################################

# 캐시정리
@bot.command(name='캐시정리')
async def controller_clear_cache(ctx, *args):    
    await cache_controller.clear_cache(ctx)

@bot.event
async def on_command_error(ctx, error):
    log(ctx, error)
    await ctx.send(error)

if __name__ == "__main__":
    bot.run(hassan_env.BOT_TOKEN)
