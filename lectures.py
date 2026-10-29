#!/usr/bin/env python3
"""온라인강의 미이수 차시 목록 · 사파리로 열기.

수집된 output/<과목>/온라인강의/frames/*.html(주차별 조각)을 읽는다. 최신 상태가 필요하면
먼저 `./ec --auto --menus 온라인강의` 로 다시 받는다.

  ./ec lectures          출석인정기간 안인데 진도율 100% 미만인 차시 목록
  ./ec lectures --all    기간 지난 것·이수한 것까지 전부
  ./ec lectures open     위 목록의 차시를 사파리 새 창으로 하나씩 연다(재생·출석(종료)는 직접)
"""
import argparse
import html as htmllib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ORIGIN = "https://ecampus.konkuk.ac.kr"
VIEW_FORM = ORIGIN + "/ilos/st/course/online_view_form.acl"
ONLINE_DIR = "온라인강의"

PERIOD_RE = re.compile(r"출석인정기간\s*:\s*(\d{4}\.\d{2}\.\d{2})\s*(오전|오후)\s*(\d{1,2}):(\d{2})\s*~\s*"
                       r"(\d{4}\.\d{2}\.\d{2})\s*(오전|오후)\s*(\d{1,2}):(\d{2})")
ITEM_RE = re.compile(r"viewGo\('(\w+)',\s*'(\w+)',\s*'\d+',\s*'\d+',\s*'(\w+)'\);\">([^<]*)</span>"
                     r".*?pbar-ani\.gif\);\s*width:\s*(\d+)%.*?id=\"per_text\".*?>\s*([\d:]+)\s*/\s*([\d:]+)\s*/\s*([\d:]+)\s*<",
                     re.S)
TITLE_RE = re.compile(r"font-size:\s*16px;\">([^<]+)</div>")
KJKEY_RE = re.compile(r'id="_KJKEY"[^>]*value="(\w+)"')
LECT_TYPE_RE = re.compile(r'id="kj_lect_type"[^>]*value="(\w*)"')


def _ampm(date, ap, h, m):
    h = int(h) % 12 + (12 if ap == "오후" else 0)
    return datetime.strptime(date, "%Y.%m.%d").replace(hour=h, minute=int(m))


def _secs(t):
    s = 0
    for part in t.split(":"):
        s = s * 60 + int(part)
    return s


def parse_week(frag: str) -> list:
    """주차 조각 1개 → 차시 dict 목록. 차시(lecture-box) 안 영상 항목이 여럿이면 각각 담는다.
    진도율은 진행 막대 폭(pbar-ani width)에서 읽는다 — per_text 글자는 학습 0분이어도 100% 로 찍힌 사례가 있다."""
    out = []
    for box in re.split(r'<div id="lecture-\d+" class="lecture-box"', frag)[1:]:
        title = TITLE_RE.search(box)
        period = PERIOD_RE.search(box)
        items = [{"week": w, "seq": s, "item_id": i, "name": htmllib.unescape(n).strip(),
                  "percent": int(p), "learned": _secs(a), "required": _secs(r)}
                 for w, s, i, n, p, a, _, r in ITEM_RE.findall(box)]
        if not items:
            continue
        out.append({
            "title": htmllib.unescape(title.group(1)).strip() if title else "",
            "start": _ampm(*period.groups()[:4]) if period else None,
            "end": _ampm(*period.groups()[4:]) if period else None,
            "week": items[0]["week"], "seq": items[0]["seq"], "items": items,
        })
    return out


def load(output: Path) -> list:
    rows = []
    for menu in sorted(output.glob(f"*/{ONLINE_DIR}")):
        frames = sorted((menu / "frames").glob("frame_*.html"))
        if not frames:
            continue
        form = frames[0].read_text(encoding="utf-8", errors="replace")
        kj = KJKEY_RE.search(form)
        lt = LECT_TYPE_RE.search(form)
        for f in frames[1:]:
            for lec in parse_week(f.read_text(encoding="utf-8", errors="replace")):
                lec.update(course=menu.parent.name, kjkey=kj.group(1) if kj else "",
                           lect_type=lt.group(1) if lt else "0", fetched=f.stat().st_mtime)
                rows.append(lec)
    rows.sort(key=lambda r: (r["end"] or datetime.max, r["course"], int(r["week"]), int(r["seq"])))
    return rows


def done(lec) -> bool:
    return all(i["percent"] >= 100 for i in lec["items"])


def status(lec, now) -> str:
    if done(lec):
        return "이수"
    if lec["start"] and now < lec["start"]:
        return "예정"
    if lec["end"] and now > lec["end"]:
        return "기간지남"
    return "미이수"


def _hm(s):
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def open_in_safari(lec, out_dir: Path) -> Path:
    """online_view_form.acl 로 POST 하는 자동 제출 페이지를 만들어 사파리 새 창으로 연다.
    ilos 화면의 '학습하기' 버튼(viewGo)이 보내는 폼과 같은 값이다. 로그인은 사파리 세션을 쓴다."""
    out_dir.mkdir(parents=True, exist_ok=True)
    fields = {"lecture_weeks": lec["seq"], "WEEK_NO": lec["week"], "_KJKEY": lec["kjkey"],
              "kj_lect_type": lec["lect_type"], "item_id": "", "force": ""}
    inputs = "".join(f'<input type="hidden" name="{k}" value="{htmllib.escape(v)}">' for k, v in fields.items())
    page = out_dir.resolve() / f"{lec['course']}-{lec['week']}주{lec['seq']}차시.html"
    page.write_text(f'<!doctype html><meta charset="utf-8"><title>{htmllib.escape(lec["course"])}</title>'
                    f'<form method="post" action="{VIEW_FORM}">{inputs}</form>'
                    '<script>document.forms[0].submit()</script>', encoding="utf-8")
    subprocess.run(["osascript", "-e", 'tell application "Safari" to make new document',
                    "-e", f'tell application "Safari" to set URL of front document to "{page.as_uri()}"',
                    "-e", 'tell application "Safari" to activate'], check=True)
    return page


def main(argv=None):
    ap = argparse.ArgumentParser(description="온라인강의 미이수 차시 목록 · 사파리로 열기")
    ap.add_argument("action", nargs="?", default="list", choices=["list", "open"])
    ap.add_argument("--all", action="store_true", help="이수·기간지남·예정까지 전부 보여 준다")
    ap.add_argument("--output", default="output")
    args = ap.parse_args(argv)

    now = datetime.now()
    rows = load(Path(args.output))
    if not rows:
        sys.exit(f"{args.output}/*/{ONLINE_DIR} 가 없습니다 — 먼저 ./ec --auto --menus 온라인강의")
    oldest = datetime.fromtimestamp(min(r["fetched"] for r in rows))
    pick = rows if args.all and args.action == "list" else [r for r in rows if status(r, now) == "미이수"]

    print(f"수집 시각 {oldest:%m-%d %H:%M} 기준 (최신화: ./ec --auto --menus 온라인강의)")
    if not pick:
        print("출석인정기간 안의 미이수 차시가 없습니다.")
        return
    for r in pick:
        left = sum(max(0, i["required"] - i["learned"]) for i in r["items"])
        need = sum(i["required"] for i in r["items"])
        end = f"{r['end']:%m-%d %H:%M}" if r["end"] else "?"
        print(f"[{status(r, now)}] {r['course']} {r['week']}주 {r['seq']}차시  ~{end}  "
              f"영상 {_hm(need)} · 남은 {_hm(left)}  {r['title']}")
    if args.action == "open":
        for r in pick:
            open_in_safari(r, Path(args.output) / "_open")
        print(f"\n사파리 창 {len(pick)}개를 열었습니다. 학습창에서 '출석(종료)'을 눌러야 출석 시간이 반영됩니다.")


if __name__ == "__main__":
    main()
