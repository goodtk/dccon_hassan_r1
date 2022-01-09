from discord import File
from util import discord_util

# 요청자의 태그와 디시콘 전송
async def send_with_dccon(ctx, buffer, file_name):
    sender_tag = "<@" + str(ctx.author.id) + ">"                             # 디시콘 + 콘 사용자 표시
    try:
        await ctx.send(file=File(buffer, file_name), content=sender_tag)
        return True
    except:
        await ctx.send('dccon_send : 디시콘 업로드 중 오류 발생.')
        return False

async def send(ctx, msg):
    await ctx.send(msg)

async def send_dm(ctx, msg):
    await ctx.author.send(msg)

async def reaction_by_slash(ctx):
    if discord_util.is_called_by_slash(ctx):
        await ctx.defer()
    else:
        await ctx.channel.trigger_typing()