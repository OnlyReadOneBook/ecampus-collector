#!/usr/bin/env python
"""알림 감시 — 새 강의자료·온라인강의·과제 알림이 뜨면 처리 작업(Claude)을 띄운다.

윈도우 작업 스케줄러가 짧은 주기로 부른다. 매번 하는 일은 notify.fetch() 한 번(HTTP)뿐이고,
Claude 는 새 알림이 있을 때만 띄운다. ilos 는 학생에게 푸시를 주지 않으므로 알림함을
들여다보는 폴링 자체는 피할 수 없다.

- 기준선: 상태 파일이 없으면 이번 알림을 저장만 하고 끝낸다(지난 알림으로 띄우지 않게).
- 겹침 방지: 띄운 Claude 가 살아 있으면 조회도 하지 않는다. ilos 는 중복 로그인 시
  기존 세션을 끊어서, 처리 중인 attend.py 세션을 이 조회가 끊을 수 있다.

    python watch.py --cmd "claude.exe -p ..."      # 새 알림이면 --cmd 를 띄운다
    python watch.py --dry-run                       # 띄우지 않고 판정만 찍는다
"""
import argparse, json, os, shlex, subprocess, sys
from pathlib import Path

import notify

STATE = Path("output/_watch_seen.json")
LOCK = Path("output/_watch_running.json")
# (과목 부분일치, 알림 종류). 과목이 "" 이면 전 과목.
TRIGGERS = [("", "강의자료"), ("", "온라인강의"), ("컴퓨터공학세미나", "과제")]


def key(n: dict) -> str:
    return "|".join(n.get(k, "") for k in ("date", "course", "kind", "title"))


def wanted(n: dict) -> bool:
    return any(c in n.get("course", "") and n.get("kind") == k for c, k in TRIGGERS)


def alive(pid: int) -> bool:
    if os.name == "nt":
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                             capture_output=True, text=True).stdout
        return str(pid) in out
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def new_items(notis: list, seen: set) -> list:
    return [n for n in notis if wanted(n) and key(n) not in seen]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmd", default="", help="새 알림이 있을 때 띄울 명령")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if LOCK.exists():
        pid = json.loads(LOCK.read_text(encoding="utf-8")).get("pid", 0)
        if pid and alive(pid):
            print(f"처리 작업(pid {pid}) 진행 중 — 건너뜀")
            return
        LOCK.unlink()

    notis = notify.fetch()["notifications"]
    first = not STATE.exists()
    seen = set() if first else set(json.loads(STATE.read_text(encoding="utf-8")))
    fresh = [] if first else new_items(notis, seen)

    for n in fresh:
        print(f"새 알림: {n['course']} [{n['kind']}] {n['title']}")
    if a.dry_run:
        print("기준선 없음(첫 실행)" if first else f"새 알림 {len(fresh)}건")
        return

    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(sorted(seen | {key(n) for n in notis}), ensure_ascii=False),
                     encoding="utf-8")
    if first:
        print("기준선 만듦")
        return
    if not fresh or not a.cmd:
        return
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    p = subprocess.Popen(a.cmd if os.name == "nt" else shlex.split(a.cmd), creationflags=flags)
    LOCK.write_text(json.dumps({"pid": p.pid, "items": [key(n) for n in fresh]},
                               ensure_ascii=False), encoding="utf-8")
    print(f"처리 작업 띄움(pid {p.pid})")


if __name__ == "__main__":
    sys.exit(main())
