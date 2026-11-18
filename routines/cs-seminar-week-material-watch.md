---
name: cs-seminar-week-material-watch
description: "컴퓨터공학세미나 새 주차 강의가 올라오면 영상을 끝까지 보고 요약서를 써서 저장만 한다. 제출하지 않는다 (매주 월 09:00 KST, 1116 제출·온강 출석 제거, 1118 화 19:17→월 09:00)"
---

이 PC(윈도우)에서 도는 예약 작업 cs-seminar-week-material-watch 다(매주 월 09:00, 1118 화 19:17 에서 옮김: 강의자료 PDF 가 늦어도 일요일 밤에 올라온다). 2026-09-28 에 맥 예약 작업을 이 PC 로 옮겼다. 이 본문이 지시서 전부이고, 이 세션은 이전 대화를 기억하지 못하니 여기 적힌 것만 믿는다. 답은 한국어로 한다.

건국대 eCampus 「컴퓨터공학세미나」(교수 남원홍, 100% e-러닝)에서 새 주차 강의가 올라오면 강의 영상을 끝까지 보고 요약서를 써서 저장한다(1~5단계, 새 자료가 있을 때만). **eCampus 에 제출하지 않는다.** 제출은 사용자가 대화에서 그 주차를 제출하라고 명시적으로 말했을 때만, 이 루틴이 저장해 둔 파일로 한다(1116 사용자 지시). 온라인강의 출석 채우기(attend.py)도 하지 않는다(1116 사용자 지시).

## 보고
- 폰 푸시는 쓰지 않는다. PushNotification 을 부르지 않는다(0922 일혁 지시). 결과는 이 실행의 보고와 아래 실행 기록으로만 낸다.
- 보고에 값이 있는 것은 eCampus 앱이 알려 주지 않는 것 둘, 몇 주차 요약서를 써서 「제출 대기」로 저장했는지 또는 무엇이 막았는지뿐이다(강의 영상 문제는 첫 줄에 적는다). 새 자료 알림은 사용자가 앱 푸시로 이미 받는다.

## 지켜야 할 것
- 작업 폴더는 C:\Users\rlfjr\ecampus-collector, 파이썬은 그 안의 .venv\Scripts\python.exe 다. 명령은 PowerShell 도구에서 그 폴더로 cd 한 뒤 돌린다(스크립트가 .auth-notify·.auth-submit·output 을 상대 경로로 쓴다).
- 창을 띄우지 않는다. collect.py 는 반드시 --headless 로 돌린다(notify.py·submit_report.py 는 원래 headless 다). 이 PC 에서는 GTA AFK 매크로가 돌고, 창이 GTA 포커스를 가져가면 방치 킥이 난다. GTA5_Enhanced 가 돌고 있으면 어떤 창도 앞으로 가져오지 않는다.
- 파이썬 명령 앞에는 늘 `$env:PYTHONUTF8="1"; ` 를 붙인다. 스크립트가 ✓·✗ 를 찍는데 cp949 콘솔·리다이렉트 파일에서는 UnicodeEncodeError 로 죽는다.
- 비밀번호를 묻거나 UI 폼에 직접 타이핑하지 않는다. 로그인은 스크립트가 윈도우 자격 증명 관리자(keyring)의 값으로 한다.
- 결제·메시지 전송·과제 제출은 하지 않는다. submit_report.py 를 실행하지 않는다(사용자 승인 표시 없이는 스크립트가 거부한다). 학습창 본인인증 메일은 Gmail 커넥터로 읽기만 한다. attend.py 는 돌리지 않는다.

## 0. 준비
1. `git -C C:\Users\rlfjr\ecampus-collector checkout -- config.py` 뒤 `git -C C:\Users\rlfjr\ecampus-collector pull --ff-only` 로 도구를 최신으로 한다(config.py 의 AUTO_COURSE 는 2단계에서 다시 바꾼다).
2. 로그인 정보를 확인한다: `.venv\Scripts\python -c "import collect;print(collect.keychain_creds()[0] is not None)"`. False 면 여기서 끝낸다. 실행 기록에 「막힘: 자격 증명 관리자에 eCampus 로그인 정보 없음, C:\Users\rlfjr\dotfiles\claude\scripts\setup-routine-creds.py 필요」를 남긴다.

## 1. 감지 (트리거용)
`.venv\Scripts\python notify.py --course 컴퓨터공학세미나 --json --seen output\_notify_seen.json` 으로 ilos 알림함·할일 목록을 읽는다. 이 명령은 기준선 파일을 바꾸지 않고, 새 알림을 `new` 에 담아 준다.
- `first_run` 이 true 면 첫 실행이다. `--save-seen` 을 붙여 한 번 더 돌려 기준선만 만들고 제출하지 않고 끝낸다. 기록: 「기준선 만듦」.
- 아니면 `new` 에 kind 가 강의자료 또는 온라인강의인 알림이 있는지만 본다.
- 기준선 갱신(`--seen output\_notify_seen.json --save-seen`)은 새 게 없을 때, 또는 4단계에서 그 주차 요약서를 「제출 대기」로 저장했을 때만 한다. 2~4단계가 중간에 실패하면 갱신하지 않는다. 먼저 갱신하면 다음 실행이 그 주차를 새 자료로 못 보고 영영 건너뛴다(1027: 9주차 감지 후 collect.py 실패, 기준선만 갱신돼 1030 실행이 「새 자료 없음」).
- 알림함은 최근 약 1주만 보이므로 알림 비교와 별도로, 2단계 collect 결과의 최신 강의자료 주차 N 에 대해 C:\Users\rlfjr\school\cs-seminar\week<N>_summary.docx 파일과 실행 기록의 「N주차 요약서 제출 대기 저장」이 둘 다 없으면 새 자료로 본다. 이 확인을 위해 새 알림이 없어도 2단계 collect 는 매번 돌린다.
- 새 알림이 없으면 2단계 collect 만 돌려 위의 미제출 주차 확인을 하고, 미제출 주차도 없으면 3~5단계를 건너뛰고 끝낸다. 기록: 「새 자료 없음」.
- 로그인이 실패하면(「로그인 실패」로 끝남) 원인만 기록하고 끝낸다.

## 2. 자료 받기
1. config.py 의 AUTO_COURSE 줄을 python 으로 `AUTO_COURSE = "컴퓨터공학세미나"` 로 바꾼다(sed 는 없다). PowerShell 에서 따옴표가 깨지면 Bash 도구의 heredoc 으로 `.venv/Scripts/python - <<'EOF'` 를 쓴다.
2. `.venv\Scripts\python collect.py --auto --headless --menus 강의자료,공지,과제,온라인강의` 를 PowerShell 도구 timeout 600000 으로 돌린다. 시간이 모자라 끊기면 같은 명령을 한 번 더 돌린다(이미 받은 첨부는 건너뛴다).
3. 새 주차 N 의 `output\컴퓨터공학세미나\강의자료\posts\*<N>주차*\files\*.pdf` 가 실제로 있는지 본다. 없으면 여기서 멈춘다. 그다음 그 주차 강의 영상을 끝까지 본다: 학습창 본인인증 뒤 `online_view_navi.acl`·`online_view.acl` 로 HLS 주소를 얻어 ffmpeg 로 받고, 음성 전체를 받아쓰고 30초 간격 화면을 확인한다. PDF 와 지난 제출본만으로 요약서를 쓰지 않고, attend.py 의 출석 시간 채우기를 시청으로 치지 않는다. 영상이 없거나·안 열리거나·소리가 없거나·일부만 받아지거나·자료와 내용이 다르면 요약서를 쓰지 말고 멈춰 사용자에게 바로 알린다(1116 사용자 지시). 이 루틴은 1116 에 꺼져 있다.

## 3. 요약서 작성
기준 두 가지를 먼저 읽는다.
- 양식: `output\컴퓨터공학세미나\공지사항\posts\*Pass 조건*\files\컴퓨터공학세미나_요약서_2026.docx`
- 문체·분량·구성: `output\컴퓨터공학세미나\과제\posts\*\files\*.docx`(지난 주차 제출본). 없으면 C:\Users\rlfjr\school\cs-seminar\ 의 지난 weekN_summary.docx 를 본다.

PDF 는 Read 도구로 읽는다. 양식 docx 를 python-docx(.venv 에 설치돼 있다)로 열어 채운다. 표에 컴퓨터공학부 / 202111373 / 정일혁 을 넣고, 본문은 소제목 2개와 문단들, 끝에 Keyword 줄. A4 1~2장. PDF 에 실제로 있는 내용만 쓴다.

`C:\Users\rlfjr\school\cs-seminar\week<N>_summary.docx` 로 저장한다(폴더가 없으면 만든다). 파일명은 영문·숫자만 쓴다. 교내 방화벽이 한글 파일명 업로드를 막는다.

## 4. 저장 (제출하지 않는다)
- 요약서를 eCampus 에 내지 않는다. submit_report.py 를 부르지 않는다.
- `C:\Users\rlfjr\school\cs-seminar\pending.md` 에 「N주차 · week<N>_summary.docx · RT_SEQ <번호> · 마감 <날짜> · 강의 영상 <편수>편 <총 길이> 받아쓰기 확인」 한 줄을 덧붙인다. RT_SEQ 는 `output\컴퓨터공학세미나\과제\posts\<번호>_<N>주차 온라인...\meta.json` 의 top_url 에 있다.
- 사용자가 대화에서 「N주차 제출해」라고 명시하면, 그 세션이 이 파일을 `submit_report.py --user-approved ...` 로 낸다. 루틴은 이 플래그를 쓰지 않는다.

## 5. 마무리
- 보고 첫 줄: 「N주차 요약서 제출 대기 저장(마감 <날짜>)」. 강의 영상에 문제가 있었으면 그것이 첫 줄이다.
- 저장한 docx 는 SendUserFile 로 함께 보낸다.

## 실행 기록
실행마다 `C:\Users\rlfjr\school\cs-seminar\runs\cs-seminar-week-material-watch.md`에 결과를 기록한다. 요약서 결과를 한 줄로 적는다(예: 「12주차 요약서 제출 대기 저장, 영상 1편 51분 받아쓰기 확인」·「새 자료 없음」). 새 소식이 없거나 막힌 경우에도 원인을 한 줄 남긴다. 다음 명령의 `<결과 한 줄>`은 실제 결과로 바꾼다.

```powershell
& "C:\Users\rlfjr\ecampus-collector\.venv\Scripts\python.exe" "C:\Users\rlfjr\dotfiles\claude\scripts\routine-events.py" record --task "cs-seminar-week-material-watch" --line "YYYY-MM-DD HH:mm [PC] <결과 한 줄>" --publish
```

기존 알림 조건이 성립해 실제 알림을 보냈을 때만 같은 명령에 `--notification "실제로 보낸 동일 문구"`를 추가한다. 학교 작업은 기존 지시대로 알림을 보내지 않는다. 공통 절차의 후속 알림 전달 단계도 따른다. 종료 코드가 0이 아니면 게시 실패를 기록하고 성공으로 보고하지 않는다. 보고서와 보유 내역은 전달 저장소에 넣지 않는다. 원본 로그를 별도로 다시 기록하지 않는다.

공통 실행 절차는 `C:\Users\rlfjr\dotfiles\codex\skills\project-task-routing\references\pc-runtime.md`를 읽는다.
