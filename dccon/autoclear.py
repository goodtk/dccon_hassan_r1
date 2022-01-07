import os
import env.hassan_env as hassan_env
from log.logger import system_log

# 콘 명령어 자동 삭제 채널에 포함이 된다면 명령어 삭제
async def auto_delete_dccon(ctx):
    if os.path.exists(hassan_env.CMD_AUTODEL_CHANNEL_PATH): 
        file = open(hassan_env.CMD_AUTODEL_CHANNEL_PATH, mode='rt', encoding='utf-8')
        lines = file.readlines()
        file.close()

        for line in lines:
            system_log(str(ctx.channel.id) + ' vs ' + line.replace('\n',''))
            if str(ctx.channel.id) == line.replace('\n',''): 
                try:
                    await ctx.message.delete()      # 명령어 메시지 삭제
                    system_log('콘 명령어 자동 삭제 완료')
                except Exception as autodelException:
                    system_log(autodelException)
                break