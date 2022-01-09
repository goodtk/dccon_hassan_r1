import os
import env.hassan_env as hassan_env
from logger.logger import system_log

# 콘 명령어 자동 삭제 채널에 포함이 되는지 검사
def is_command_autodelete_channel(ctx):
    if os.path.exists(hassan_env.CMD_AUTODEL_CHANNEL_PATH): 
        file = open(hassan_env.CMD_AUTODEL_CHANNEL_PATH, mode='rt', encoding='utf-8')
        lines = file.readlines()
        file.close()

        for line in lines:
            system_log(str(ctx.channel.id) + ' vs ' + line.replace('\n',''))
            if str(ctx.channel.id) == line.replace('\n',''): 
                return True
        
    return False