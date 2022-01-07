from discord import File

# 요청자의 태그와 디시콘 전송
async def send_with_dccon(ctx, buffer, file_name):
    sender_tag = "<@" + str(ctx.author.id) + ">"                             # 디시콘 + 콘 사용자 표시
    try:
        await ctx.channel.send(file=File(buffer, file_name), content=sender_tag)
        return True
    except:
        await ctx.channel.send('dccon_send : 디시콘 업로드 중 오류 발생.')
        return False

async def send(ctx, msg):
    await ctx.channel.send(msg)