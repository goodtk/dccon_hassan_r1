# 디시콘 핫산
디시콘을 디스코드에서 쓸 수 있게 해주는 디스코드 봇입니다.
디코 개발자 페이지 가서
테스트용 봇 하나 만들고
봇 토큰을 .env 안에 넣으면 세팅 끝
개발용 디코 방 하나 파서
거기다 봇 초대하고 테스트

## Demo
[봇 초대 링크](https://discord.com/api/oauth2/authorize?client_id=629279090716966932&permissions=2147526656&scope=bot%20applications.commands)

Oracle Free Tier 서버에서 돌아가고 있는 봇입니다. 예고 없이 봇 작동이 중지될 수 있습니다. 

## [원본](https://github.com/Dogdriip/dccon_hassan) Demo
[원본 봇 초대 링크](https://discordapp.com/oauth2/authorize?&client_id=464437182887886850&scope=bot&permissions=101376)

Heroku 무료 Dyno에서 테스트용으로 돌아가고 있는 봇입니다. 사용자가 몰리면 봇 응답이 느려지거나 봇이 꺼질 수 있으며, 예고 없이 봇 작동이 중지될 수 있습니다. 

## 설치 및 실행
```
$ pip3 install -r requirements.txt
env_example.txt 참고하여 .env 파일 생성
$ python3 main.py
```

## 사용법
!콘 "디시콘 패키지 제목" "콘 이름"  
사용 예시 1 : !콘 멘헤라콘 15, !콘 "마히로콘 리메이크" 꿀잠, !콘 "좋은말콘 스페셜 에디션" 응원, ...  
사용 예시 2 : !콘 "나나히라 라인", !콘 카구야는인사받고싶어, ... (디시콘 패키지 이름만 입력 시 디시콘 목록 출력)  
다른 커맨드는 봇 초대해서 "!도움" 입력

## 즐겨찾기

!즐찾 [옵션1] [옵션2] [...]
!즐찾 "추가" "단축어" "디시콘 패키지 제목" "콘 이름"

등록 예시 : !즐찾 추가 멘헤라15 멘헤라콘 1  
목록 조회 : !즐찾 목록  
삭제 예시 : !즐찾 삭제 멘헤라15  
사용 예시 : !ㅋ 멘헤라15  
사용 예시2: !ㅋ 갈아 입어 오기 때문에 기다리고 있어요

(즐겨찾기 사용은 띄워쓰기를 따옴표로 안묶어도 됩니다.)

즐겨찾기 관련 다른 커맨드는 봇 초대해서 "!즐찾" 입력

## 콘 명령어 자동 삭제 채널
채널 ID를 입력하면 해당 채널에서는 콘, ㅋ 명령어는 자동 삭제됩니다.

.concmdAutodelChannel.example을 참고하여
.concmdAutodelChannel
을 만든 후 안에 채널 ID를 한줄씩 넣어주세요.

## TODO
* 라이센스 추가
* 이것저것
* 디시콘 다운받는 부분을 별도의 모듈로 분리

## CUSTOMED
* 디시콘 사용자 표시 기능 추가
* 검색에 성공했지만 검색결과가 없는 경우 만두콘 표시하지 않게 변경.
* 패키지만 입력했을 때 패키지 URL을 표시하도록 함.
* 패키지명이 완전히 동일한 패키지가 선택되도록 수정함.
* 즐겨찾기 기능 추가 (매크로) [BETA]
* 캐싱 (.env 파일의 CACHE_MAX를 0로 설정하면 사용하지 않음)
* 콘 명령어 자동삭제 채널 추가
