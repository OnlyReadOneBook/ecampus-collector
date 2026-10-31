---
name: online-lecture-attend
description: 온라인강의 미이수 차시가 생기면 바로 출석을 채운다. 30분마다 도는 감시(attend-watch.ps1, LLM 없음)가 미이수를 찾았을 때만 이 루틴을 띄운다.
---

이 PC(윈도우)의 감시 작업 `Attend Watch` 가 `attend.py --check` 로 미이수 차시를 찾았을 때 띄우는 루틴이다. 이 본문이 지시서 전부다. 답은 한국어로 한다.

## 지켜야 할 것
- 작업 폴더는 C:\Users\rlfjr\ecampus-collector, 파이썬은 그 안의 .venv\Scripts\python.exe. 명령 앞에 `$env:PYTHONUTF8="1"; ` 를 붙인다.
- 창을 띄우지 않는다(-NoNewWindow). GTA5_Enhanced 가 돌고 있으면 어떤 창도 앞으로 가져오지 않는다.
- 비밀번호를 묻거나 타이핑하지 않는다. 로그인은 스크립트가 자격 증명 관리자 값으로 한다. 본인인증 메일은 Gmail 커넥터로 읽기만 한다.
- 출석 시간은 서버에 쌓인다. 중간에 끊겨도 다시 돌리면 남은 시간만 채운다.
- PushNotification 은 부르지 않는다.

## 절차
cs-seminar-week-material-watch.md 의 「6. 온라인강의 출석」 1~5단계를 그대로 한다(대상 확인 → attend.py 배경 실행 → Gmail 인증번호 → 대기 → 확인). 로그 경로는 같다(C:\Users\rlfjr\school\cs-seminar\runs\attend-last.log).

## 실행 기록
`& "C:\Users\rlfjr\ecampus-collector\.venv\Scripts\python.exe" "C:\Users\rlfjr\dotfiles\claude\scripts\routine-events.py" record --task "cs-seminar-week-material-watch" --line "YYYY-MM-DD HH:mm [PC] 온강 감시: <N차시 채움(과목·주차), 남은 미이수 M | 막힘 원인>" --publish`
기록은 세미나 루틴 기록에 함께 남긴다(같은 사람이 같은 곳에서 본다).
