import env.hassan_env as hassan_env
from discord import Embed
from logger.logger import log, system_log

async def send_help(ctx):
    log(ctx, 'help command')
    embed = Embed(title='안녕하세요! 디시콘 핫산이에요!',
                  description='명령어들은 아래에서 전부 보실 수 있어요.',
                  color=hassan_env.EMBED_COLOR)
    embed.add_field(name='사용 방법', value='!콘 "디시콘 패키지 제목" "콘 이름"', inline=False)
    embed.add_field(name='사용 예시 1', value='!콘 멘헤라콘 15, !콘 "마히로콘 리메이크" 꿀잠, !콘 "좋은말콘 스페셜 에디션" 응원, ...', inline=False)
    embed.add_field(name='사용 예시 2', value='!콘 "나나히라 라인", !콘 카구야는인사받고싶어, ... (디시콘 패키지 이름만 입력 시 디시콘 목록 출력)', inline=False)
    embed.add_field(name='명령어', value='!콘, !도움, !대하여, !ㅋ, !즐찾', inline=False)

    embed.set_footer(text='그코좆망겜')
    await ctx.send(embed=embed)

async def send_about(ctx):
    log(ctx, 'about command')
    embed = Embed(title='디시콘 핫산',
                  description='디시콘을 디스코드에서 쓸 수 있게 해주는 디스코드 봇입니다.',
                  color=hassan_env.EMBED_COLOR)
    embed.add_field(name='Repository', value='https://github.com/dldhk97/dccon_hassan', inline=False)
    await ctx.send(embed=embed)

async def send_help_favorite(ctx):
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
    await ctx.send(embed=embed)
