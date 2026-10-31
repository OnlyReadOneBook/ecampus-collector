#!/usr/bin/env python
"""ilos 알림/할일 폴링 — 전체 수집(./ec) 없이 '새 게시물이 떴는지'만 싸게 확인한다.

ilos 는 좌측 상단 배지로 알림(notification)과 할일(todo)을 준다:
  - /ilos/mp/notification_list.acl  새 과제·공지·강의자료·온라인강의 알림 목록(HTML)
  - /ilos/mp/todo_list.acl          미제출/미학습 할일 목록(POST, HTML 조각)
폴더를 diff 하는 것보다 정확하고(교수가 올린 시각이 찍힌다) 훨씬 싸다.

브라우저 없이 HTTP(api.Client)로 돈다 — 자동으로 주기 실행되는 용도라 창이 필요 없다.

주의: ilos 는 중복 로그인 시 기존 세션을 끊는다. 사람이 eCampus 를 보고 있는
동안 이걸 돌리면 그 사람이 로그아웃된다. 자주 돌리지 말 것.

    python notify.py            # 사람이 읽는 형태
    python notify.py --json     # JSON (자동화용)
    python notify.py --course 컴퓨터공학세미나
    python notify.py --json --seen output/_notify_seen.json        # 새 알림만 "new" 로 표시, 파일은 안 바꾼다
    python notify.py --json --seen output/_notify_seen.json --save-seen   # 비교 뒤 이번 결과로 기준선 갱신

기준선 갱신(--save-seen)은 새 알림이 없을 때나 그 알림의 후속 처리(자료 받기·제출)가 끝난 뒤에만 한다.
비교와 동시에 갱신하면 후속 처리가 실패해도 다음 실행이 그 알림을 새 것으로 못 본다
(2026-10-27: 9주차 알림 감지 뒤 collect 실패, 기준선만 갱신돼 9주차가 영영 빠졌다).
"""
import argparse, json, re, sys
from pathlib import Path

from bs4 import BeautifulSoup

import api

NOTI_URL = "/ilos/mp/notification_list.acl"
TODO_URL = "/ilos/mp/todo_list.acl"


def _text(el) -> str:
    return re.sub(r"\s+", " ", el or "").strip()


def parse_notifications(body: str) -> list:
    """알림 목록 본문 텍스트를 [{date, course, kind, title, when}] 로 자른다.

    화면은 '날짜 헤더 → (과목 / 내용 / 상대시각) 3줄' 반복 구조다.
    """
    out, cur_date = [], ""
    lines = [l.strip() for l in body.splitlines() if l.strip()]
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.fullmatch(r"\d{4}\.\d{2}\.\d{2} \S요일", line):
            cur_date = line
            i += 1
            continue
        m = re.match(r"\[(.+?)\]\s*(.+)", line)          # [서울] 컴퓨터공학세미나(001)
        if m and i + 1 < len(lines) and lines[i + 1].startswith("["):
            course = m.group(2).strip()
            m2 = re.match(r"\[(.+?)\]\s*(.*)", lines[i + 1])   # [과제] 새로운 과제가...
            kind, title = (m2.group(1), m2.group(2).strip()) if m2 else ("", lines[i + 1])
            when = lines[i + 2] if i + 2 < len(lines) and not lines[i + 2].startswith("[") \
                                 and not re.fullmatch(r"\d{4}\.\d{2}\.\d{2} \S요일", lines[i + 2]) else ""
            out.append({"date": cur_date, "course": course, "kind": kind,
                        "title": title, "when": when})
            i += 3 if when else 2
            continue
        i += 1
    return out



TODO_KIND = {"report": "과제", "lecture_weeks": "온라인강의", "project": "팀프로젝트",
             "discuss": "토론", "test": "시험", "survey": "설문", "clicker": "투표"}


def parse_todos(html: str) -> list:
    """todo_list.acl 응답에서 [{kind, title, course, dday, due}] 를 뽑는다.

    항목은 <div class="todo_wrap ..."> 블록이고 그 안에
    todo_title / todo_subjt / todo_d_day / todo_date 로 나뉜다.
    """
    out = []
    for blk in re.findall(r'<div class="todo_wrap[^"]*"(.*?)(?=<div class="todo_wrap|\Z)', html, re.S):
        def pick(cls):
            # 클래스가 'todo_d_day site-color' 처럼 붙어 오므로 뒤에 더 와도 매치시킨다
            m = re.search(r'class="%s(?:\s[^"]*)?"[^>]*>(.*?)</' % cls, blk, re.S)
            return _text(re.sub(r"<[^>]+>", " ", m.group(1))) if m else ""
        title = pick("todo_title")
        if not title:
            continue
        m = re.match(r"\[(.+?)\]\s*(.*)", title)
        kind, name = (m.group(1), m.group(2).strip()) if m else ("", title)
        dates = re.findall(r"(\d{4}\.\d{2}\.\d{2}[^<]*)", blk)
        out.append({
            "kind": kind or TODO_KIND.get(pick("gubun"), ""),
            "title": name,
            "course": pick("todo_subjt"),
            "dday": pick("todo_d_day"),
            "due": _text(dates[-1]) if dates else "",
        })
    return out


def html_to_lines(html: str) -> str:
    """알림 목록 HTML → parse_notifications 가 먹는 줄 단위 텍스트.
    날짜 헤더(notification_title) · 과목(notification_subject) · 내용(notification_text) ·
    상대시각(notification_day) 이 문서 순서대로 한 줄씩이 되게 잇는다(브라우저 innerText 와 같은 모양)."""
    soup = BeautifulSoup(html or "", "lxml")
    sel = ".notification_title, .notification_subject, .notification_text, .notification_day"
    lines = (_text(el.get_text(" ")) for el in soup.select(sel))
    return "\n".join(l for l in lines if l)


def fetch(course_filter: str = "") -> dict:
    """브라우저 없이 HTTP 로 알림·할일을 받는다(api.Client, 키체인 자격)."""
    try:
        client = api.Client.from_keychain()
        client.login()
    except api.LoginError as e:
        sys.exit(f"로그인 실패: {e}")
    notis = parse_notifications(html_to_lines(client.get(NOTI_URL)))
    # 할일 목록은 todo_list_form.acl 화면이 아니라 ajax 엔드포인트를 직접 부른다.
    todo_html = client.post(TODO_URL, {"todoKjList": "", "chk_cate": "ALL"})
    todos = parse_todos(todo_html)

    if course_filter:
        notis = [n for n in notis if course_filter in n["course"]]
        todos = [t for t in todos if course_filter in t["course"]]
    return {"notifications": notis, "todos": todos}


def _noti_key(n: dict) -> tuple:
    return (n.get("date"), n.get("course"), n.get("kind"), n.get("title"))


def diff_seen(data: dict, seen_path) -> dict:
    """기준선 파일과 비교해 새 알림을 data["new"] 에 담는다. 파일은 건드리지 않는다.
    기준선이 없으면 first_run=True 이고 new 는 비운다(이미 나온 알림을 새 것으로 오인하지 않게)."""
    path = Path(seen_path)
    if not path.exists():
        return {**data, "first_run": True, "new": []}
    # 손으로 고친 파일에 BOM 이 붙어 있어도 읽는다.
    old = json.loads(path.read_text(encoding="utf-8-sig"))
    seen = {_noti_key(n) for n in old.get("notifications", [])}
    new = [n for n in data["notifications"] if _noti_key(n) not in seen]
    return {**data, "first_run": False, "new": new}


def save_seen(data: dict, seen_path) -> None:
    keep = {"notifications": data["notifications"], "todos": data["todos"]}
    Path(seen_path).write_text(json.dumps(keep, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--course", default="", help="과목명 부분일치 필터")
    ap.add_argument("--seen", help="기준선 JSON 경로. 주면 새 알림을 new 로 표시한다(파일은 안 바꾼다)")
    ap.add_argument("--save-seen", action="store_true", help="비교 뒤 이번 결과로 --seen 파일을 덮어쓴다")
    a = ap.parse_args()
    if a.save_seen and not a.seen:
        ap.error("--save-seen 은 --seen 과 함께 쓴다")
    data = fetch(a.course)
    if a.seen:
        data = diff_seen(data, a.seen)
        if a.save_seen:
            save_seen(data, a.seen)
    if a.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    print("── 알림 ──")
    for n in data["notifications"]:
        print(f"  {n['date']:<18} {n['course']:<26} [{n['kind']}] {n['title']}  ({n['when']})")
    print("\n── 할일 ──")
    for t in data["todos"]:
        print(f"  {t['dday']:>6}  {t['course']:<18} [{t['kind']}] {t['title']}  (마감 {t['due']})")


if __name__ == "__main__":
    main()
