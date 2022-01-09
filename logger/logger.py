from datetime import datetime

def system_log(text):
    print(f'{"SYSTEM"} | {str(datetime.now())} | {text}')  # TODO: 시간대 조정

def log(ctx, text):
    print(f'{_ctx_format(ctx)} | {str(datetime.now())} | {text}')  # TODO: 시간대 조정

def _ctx_format(ctx):
    # msg_fr = msg.server.name + ' > ' + msg.channel.name + ' > ' + msg.author.name
    # msg.server --> msg.guild
    # https://discordpy.readthedocs.io/en/latest/migrating.html#server-is-now-guild
    
    if ctx.channel:
        channel_type = ctx.channel.type.value
        if channel_type != 1:
            return f'{ctx.guild.name} > {ctx.channel.name} > {ctx.author.name}'            
    
    return f'DM > {ctx.author.name}'