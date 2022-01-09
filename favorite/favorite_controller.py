from .service import favorite_add_service, favorite_backup_service, favorite_read_service, favorite_delete_service, favorite_search_service
from send import sender
from logger.logger import log
from error.favorite_error import FavoriteError
from dccon import dccon_controller
from util import discord_util
from discord import File

async def add_favorite(ctx, keyword, package_name, dccon_name):
    log(ctx, 'add_favorite command')

    msg = favorite_add_service.add_favorite(ctx, keyword, package_name, dccon_name)
    await sender.send(ctx, msg)

async def send_favorite(ctx, keyword):
    log(ctx, 'send_favorite command')

    try:
        package_name, idx = favorite_read_service.find_favorite_one(ctx, keyword)
        await dccon_controller.send_dccon(ctx, package_name, idx)
    except FavoriteError as e:
        await sender.send(ctx, str(e))
    

async def show_favorites(ctx):
    await sender.reaction_by_slash(ctx)

    messages = favorite_read_service.show_favorites(ctx)
    for msg in messages:
        await sender.send_dm(ctx, msg)

    if discord_util.is_called_by_slash(ctx):
        await sender.send(ctx, 'DM으로 단축어 목록을 전송했습니다.')

async def delete_favorite(ctx, keyword):
    msg = favorite_delete_service.delete_favorite(ctx, keyword)
    await sender.send(ctx, msg)

async def serach_favorites(ctx, keyword):
    msg = favorite_search_service.search_favorite(ctx, keyword)
    await sender.send(ctx, msg)

async def send_favorites_file(ctx, user_id):
    try:
        results = favorite_backup_service.get_favorites_file(ctx, user_id)
        
        msg = results[0]
        file_path = results[1]
        file_name = results[2]

        await ctx.author.send(file=File(file_path, file_name), content=msg)

        if discord_util.is_called_by_slash(ctx):
            await sender.send('DM으로 즐겨찾기 목록을 전송했습니다.')

    except FavoriteError as e:
        await sender.send(str(e))

async def resotre_favorites(ctx, download_url):
    msg = favorite_backup_service.restore_favorites(ctx, download_url)
    await sender.send(ctx, msg)

async def reset_favorites(ctx):
    msg = favorite_delete_service.reset_favorites(ctx)
    await sender.send(ctx, msg)