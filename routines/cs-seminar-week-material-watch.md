---
name: cs-seminar-week-material-watch
description: "컴퓨터공학세미나 새 주차 강의가 올라오면 영상을 끝까지 보고 요약서를 써서 저장만 하고(제출하지 않는다), 수강 과목 전부의 온라인강의 미이수 차시를 HTTP 로 채운다 (매주 월 09:00 KST, 1116 제출 제거, 1118 화 19:17→월 09:00, 1125 온강 출석 복구)"
---

이 PC(윈도우)에서 도는 예약 작업 cs-seminar-week-material-watch 다(매주 월 09:00, 1118 화 19:17 에서 옮김: 강의자료 PDF 가 늦어도 일요일 밤에 올라온다). 2026-09-28 에 맥 예약 작업을 이 PC 로 옮겼다. 이 본문이 지시서 전부이고, 이 세션은 이전 대화를 기억하지 못하니 여기 적힌 것만 믿는다. 답은 한국어로 한다.

건국대 eCampus 「컴퓨터공학세미나」(교수 남원홍, 100% e-러닝)에서 새 주차 강의가 올라오면 강의 영상을 끝까지 보고 요약서를 써서 저장한다(1~5단계, 새 자료가 있을 때만). **eCampus 에 제출하지 않는다.** 제출은 사용자가 대화에서 그 주차를 제출하라고 명시적으로 말했을 때만, 이 루틴이 저장해 둔 파일로 한다(1116 사용자 지시). 그리고 수강 과목 전부(비교과 포함)의 온라인강의 미이수 차시를 attend.py 로 채운다(6단계, 매번). 1~5단계가 어디서 끝나든 6단계는 한다. 출석은 1116 에 제출과 함께 뺐다가 1125 에 되살렸다(사용자: 출석은 하지 말라고 한 적 없다). 막는 것은 과제 제출뿐이다.

## 보고
- 폰 푸시는 쓰지 않는다. PushNotification 을 부르지 않는다(0922 일혁 지시). 결과는 이 실행의 보고와 아래 실행 기록으로만 낸다.
- 보고에 값이 있는 것은 eCampus 앱이 알려 주지 않는 것 둘, 몇 주차 요약서를 써서 「제출 대기」로 저장했는지 또는 무엇이 막았는지, 그리고 온라인강의 출석이 채워졌는지 또는 막혔는지뿐이다(강의 영상 문제는 첫 줄에 적는다). 새 자료 알림은 사용자가 앱 푸시로 이미 받는다.

## 지켜야 할 것
- 작업 폴더는 C:\Users\rlfjr\ecampus-collector, 파이썬은 그 안의 .venv\Scripts\python.exe 다. 명령은 PowerShell 도구에서 그 폴더로 cd 한 뒤 돌린다(스크립트가 .auth-notify·.auth-submit·output 을 상대 경로로 쓴다).
- 창을 띄우지 않는다. collect.py 는 반드시 --headless 로 돌린다(notify.py·submit_report.py 는 원래 headless 다). 이 PC 에서는 GTA AFK 매크로가 돌고, 창이 GTA 포커스를 가져가면 방치 킥이 난다. GTA5_Enhanced 가 돌고 있으면 어떤 창도 앞으로 가져오지 않는다.
- 파이썬 명령 앞에는 늘 `$env:PYTHONUTF8="1"; ` 를 붙인다. 스크립트가 ✓·✗ 를 찍는데 cp949 콘솔·리다이렉트 파일에서는 UnicodeEncodeError 로 죽는다.
- 비밀번호를 묻거나 UI 폼에 직접 타이핑하지 않는다. 로그인은 스크립트가 윈도우 자격 증명 관리자(keyring)의 값으로 한다.
- 결제·메시지 전송·과제 제출은 하지 않는다. submit_report.py 를 실행하지 않는다(사용자 승인 표시 없이는 스크립트가 거부한다). 학습창 본인인증 메일은 Gmail 커넥터로 읽기만 한다.
- 출석 도중 notify.py 로그인은 attend.py 세션을 끊지 않았다(1031 실측). 그래도 다른 스크립트(collect)는 실측 전이라 겹쳐 돌리지 않는다. 6단계의 attend.py 는 1~5단계가 끝난 뒤에 띄운다. 출석 시간은 서버에 쌓여 attend.py 를 멈췄다 다시 돌려도 채운 시간은 남는다(1031 실측). 그러니 요약서(1~5단계)가 출석보다 먼저다.
- 영상 받기·받아쓰기 도구(1125 설치): ffmpeg 는 `C:\Users\rlfjr\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe`(PATH 에 안 잡히면 이 경로로 부른다), 받아쓰기는 저장소 `.venv` 의 faster-whisper(`from faster_whisper import WhisperModel`, 한국어 강의는 `language="ko"`)다. 둘 중 하나가 없으면 요약서를 쓰지 말고 멈춰 기록에 무엇이 없는지 적는다.

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
3. 새 주차 N 의 `output\컴퓨터공학세미나\강의자료\posts\*<N>주차*\files\*.pdf` 가 실제로 있는지 본다. 없으면 요약서는 여기서 멈추고 6단계로 간다. 그다음 그 주차 강의 영상을 끝까지 본다: 학습창 본인인증 뒤 `online_view_navi.acl`·`online_view.acl` 로 HLS 주소를 얻어 ffmpeg 로 받고, 음성 전체를 받아쓰고 30초 간격 화면을 확인한다. PDF 와 지난 제출본만으로 요약서를 쓰지 않고, attend.py 의 출석 시간 채우기를 시청으로 치지 않는다. 영상이 없거나·안 열리거나·소리가 없거나·일부만 받아지거나·자료와 내용이 다르면 요약서를 쓰지 말고 멈춰 사용자에게 바로 알린다(1116 사용자 지시).

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

## 6. 온라인강의 출석 (전 과목, 매번)
1~5단계가 어떻게 끝났든 한다(0단계에서 자격 증명이 없거나 1단계에서 로그인이 실패한 경우만 예외). 원리: 학습창을 열어 둔 것과 같은 HTTP 요청(online_view_hisno → 주기마다 online_view_at)을 보내 출석인정시간을 채운다. 영상 재생도 창도 없다. 상세는 attend.py 머리 주석.

1. 대상 확인(서버 기준, 투두·output 이 아니다). `.venv\Scripts\python -c "import api, attend; c=api.Client.from_keychain(); c.login(); [print(r['course'], r['week'], r['seq'], r['title']) for r in attend.live_pending(c)]"`. 한 줄도 없으면 기록에 「온강 미이수 없음」을 덧붙이고 마무리로 간다. 「✗ … 조회 실패」 줄은 그 과목을 못 본 것이니 기록에 그대로 옮긴다.
2. 실행. 인증번호 파일 `C:\Users\rlfjr\school\cs-seminar\runs\attend-code.txt` 를 지우고(있으면), 로그 `C:\Users\rlfjr\school\cs-seminar\runs\attend-last.log` 를 비운 뒤 배경으로 띄운다:
   ```powershell
   $env:PYTHONUTF8="1"; Set-Location -LiteralPath "C:\Users\rlfjr\ecampus-collector"; Start-Process -NoNewWindow -FilePath ".venv\Scripts\python.exe" -ArgumentList "-u","attend.py","--code-file","C:\Users\rlfjr\school\cs-seminar\runs\attend-code.txt" -RedirectStandardOutput "C:\Users\rlfjr\school\cs-seminar\runs\attend-last.log" -RedirectStandardError "C:\Users\rlfjr\school\cs-seminar\runs\attend-last.err" -PassThru | Select-Object -ExpandProperty Id
   ```
   창을 띄우지 않는다(-NoNewWindow). 돌려받은 Id 를 적어 둔다.
3. 본인인증. 로그에 「본인인증 번호를 … 로 보냈습니다」가 찍힐 때까지 10초 간격으로 본다(최대 2분). 찍히면 Gmail 커넥터 `search_threads` 로 `from:ecampusreturn07@konkuk.ac.kr newer_than:1h` 를 찾고, `get_thread`(PLAIN_TEXT)의 **가장 최근** 메시지에서 「인증번호 NNNN」을 읽는다. 같은 스레드에 옛 번호가 쌓이니 날짜·시각이 지금 실행 이후인 것만 쓴다. 메일이 아직 없으면 20초 뒤 다시 찾는다(최대 3분). 번호는 BOM·줄바꿈 없이 쓴다: `Set-Content -LiteralPath "C:\Users\rlfjr\school\cs-seminar\runs\attend-code.txt" -Value "NNNN" -NoNewline -Encoding ascii`. 로그에 「✓ 본인인증 완료」가 찍히는지 본다. 「본인인증 실패」면 번호를 잘못 읽은 것이니 가장 최근 메일을 다시 보고, 그래도 안 되면 기록에 그 메시지를 적고 마무리로 간다.
4. 대기. 차시당 남은 출석인정시간만큼 걸린다(수십 분). `Start-Sleep 240` 뒤 로그와 프로세스(`Get-Process -Id <Id> -ErrorAction SilentlyContinue`)를 보는 것을 프로세스가 끝날 때까지 반복한다. 전체 상한은 3시간이고, 넘으면 `Stop-Process -Id <Id>` 하고 「온강 시간 초과」로 기록한다. 기다리는 동안 다른 eCampus 스크립트를 겹쳐 돌리지 않는다(중복 로그인이 세션을 끊을 수 있다). 다른 일이 급하면 멈추고 하고 다시 띄운다. 채운 시간은 남는다.
5. 확인. 로그의 「✓ 출석인정시간 채움」 줄 수와 `navi·hisno·at 실패`·attend-last.err 의 Traceback 을 본다. 1번 명령을 한 번 더 돌려 서버 기준으로 미이수가 남았는지 본다. 기록 한 줄에 「온강 N차시 채움(과목·주차 나열), 남은 미이수 M」 꼴로 덧붙이고, 실패 줄이 있으면 그 메시지를 그대로 옮긴다.

## 실행 기록
실행마다 `C:\Users\rlfjr\school\cs-seminar\runs\cs-seminar-week-material-watch.md`에 결과를 기록한다. 요약서 결과와 온강 결과를 한 줄에 같이 적는다(예: 「12주차 요약서 제출 대기 저장, 영상 1편 51분 받아쓰기 확인 · 온강 미이수 없음」·「새 자료 없음 · 온강 2차시 채움(알고리즘 9주 1·2차시), 남은 미이수 0」). 새 소식이 없거나 막힌 경우에도 원인을 한 줄 남긴다. 다음 명령의 `<결과 한 줄>`은 실제 결과로 바꾼다.

```powershell
& "C:\Users\rlfjr\ecampus-collector\.venv\Scripts\python.exe" "C:\Users\rlfjr\dotfiles\claude\scripts\routine-events.py" record --task "cs-seminar-week-material-watch" --line "YYYY-MM-DD HH:mm [PC] <결과 한 줄>" --publish
```

기존 알림 조건이 성립해 실제 알림을 보냈을 때만 같은 명령에 `--notification "실제로 보낸 동일 문구"`를 추가한다. 학교 작업은 기존 지시대로 알림을 보내지 않는다. 공통 절차의 후속 알림 전달 단계도 따른다. 종료 코드가 0이 아니면 게시 실패를 기록하고 성공으로 보고하지 않는다. 보고서와 보유 내역은 전달 저장소에 넣지 않는다. 원본 로그를 별도로 다시 기록하지 않는다.

공통 실행 절차는 `C:\Users\rlfjr\dotfiles\codex\skills\project-task-routing\references\pc-runtime.md`를 읽는다.
