#!/usr/bin/env python3
"""온라인강의 출석을 HTTP 세션으로 채운다 — 학습창을 열어 둔 것과 같은 요청만 보낸다.

학습창(online_view_form.acl)은 열려 있는 동안 AttDaemon 이 주기마다 online_view_at.acl 을 보내고,
출석 시간은 그 요청으로 쌓인다(영상 재생 위치와 무관). 이 스크립트는 그 흐름을 그대로 따른다:
  2차 본인인증(메일) → 과목 입장 → 학습창 → online_view_navi → online_view_hisno → 주기마다 online_view_at
  → online_view_status 가 '부족'(1)이 아니면 종료.

  ./ec attend              수강 과목 전부(비교과 포함)의 미이수 차시(마감 빠른 순)
  ./ec attend --only 세미나  과목명에 '세미나'가 들어간 차시만
인증번호는 메일로 온다. 프롬프트에 입력하거나 --code-file 로 넘긴다.
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import api
import collect_api
import lectures

LIST_FORM = "/ilos/st/course/online_list_form.acl"
VIEW_FORM = "/ilos/st/course/online_view_form.acl"


def J(body: str) -> dict:
    body = body.strip()
    return json.loads(body) if body.startswith("{") else api.parse_jsonp(body)


def second_auth(c, code_file: Path = None):
    info = J(c.post("/ilos/secondauth/secondary_auth_way_info.acl",
                    {"AUTH_DIV": "1", "returnData": "json", "encoding": "utf-8"}))
    email = info["USER_EMAIL"]
    st = J(c.post("/ilos/secondauth/secondary_auth_start.acl",
                  {"AUTH_DIV": "1", "AUTH_WAY": "2", "AUTH_PARAM": email, "returnData": "json", "encoding": "utf-8"}))
    if st.get("isError"):
        sys.exit(f"본인인증 요청 실패: {st.get('message')}")
    print(f"본인인증 번호를 {email} 로 보냈습니다.", flush=True)
    if code_file:
        while not (code_file.exists() and code_file.read_text().strip()):
            time.sleep(1)
        code = code_file.read_text().strip()
    else:
        code = input("인증번호 4자리: ").strip()
    cf = J(c.post("/ilos/secondauth/secondary_auth_confirm.acl",
                  {"AUTH_SEQ": st.get("AUTH_SEQ", ""), "AUTH_DIV": "1", "AUTH_WAY": "2", "AUTH_CODE": code,
                   "AUTH_PARAM": email, "returnData": "json", "encoding": "utf-8"}))
    if cf.get("isError"):
        sys.exit(f"본인인증 실패: {cf.get('message')}")
    print("✓ 본인인증 완료", flush=True)


def viewer_items(html: str):
    """학습창의 cv.load(...) 인자와 차시 안 콘텐츠 목록(.item-title-lesson val='item^content^org^week^…')."""
    m = re.search(r'cv\.load\(\s*"(\w*)",\s*"(\w*)",\s*"(\w*)",\s*"(\w*)",\s*"(\w*)",\s*"(\w*)",\s*"(\w*)"', html)
    if not m:
        raise RuntimeError("학습창에서 cv.load 를 찾지 못했습니다(본인인증·출석기간 확인)")
    navi, item, content, org, weeks, ky, ud = m.groups()
    items = []
    for val in re.findall(r'class="item-title-lesson[^"]*"[^>]*\bval="([^"]+)"', html):
        p = val.split("^")
        if len(p) >= 3 and p[0] not in [i[0] for i in items]:
            items.append((p[0], p[1], p[2]))
    return {"weeks": weeks, "ky": ky, "ud": ud, "items": items or [(item, content, org)]}


def attend_item(c, v, item, content, org, need_sec, referer):
    d = J(c.post("/ilos/st/course/online_view_navi.acl",
                 {"content_id": content, "organization_id": org, "lecture_weeks": v["weeks"], "navi": "current",
                  "item_id": item, "ky": v["ky"], "ud": v["ud"], "returnData": "json", "encoding": "utf-8"},
                 referer=referer))
    if d.get("isError") or not d.get("isKjkey"):
        raise RuntimeError(f"navi 실패: {d.get('message') or d.get('chSubjtMessage')}")
    base = {"lecture_weeks": v["weeks"], "item_id": d["item_id"], "link_seq": d["link_seq"],
            "ky": v["ky"], "ud": v["ud"], "returnData": "json", "encoding": "utf-8"}
    h = J(c.post("/ilos/st/course/online_view_hisno.acl",
                 {**base, "kjkey": v["ky"], "_KJKEY": v["ky"], "interval_time": "240"}, referer=referer))
    if h.get("isError") or not h.get("isKjkey"):
        raise RuntimeError(f"hisno 실패: {h.get('message') or h.get('chSubjtMessage')}")
    his, iv = h["his_no"], int(h.get("attendIntervalTime") or 240)
    at = {**base, "his_no": his, "trigger_yn": "N", "interval_time": str(iv)}

    def beat():
        r = J(c.post("/ilos/st/course/online_view_at.acl", at, referer=referer))
        if r.get("isError") or not r.get("isKjkey"):
            raise RuntimeError(f"at 실패: {r.get('message') or r.get('chSubjtMessage')}")

    def short() -> bool:   # 출석(종료) 버튼이 묻는 것과 같은 확인 — '1' 이면 출석인정시간 미달
        r = J(c.post("/ilos/st/course/online_view_status.acl",
                     {**base, "his_no": his, "btn_dv": ""}, referer=referer))
        return str(r.get("attend_stat")) == "1"

    beat()
    start = time.time()
    print(f"     주기 {iv}초, 남은 {need_sec // 60}분 {need_sec % 60}초", flush=True)
    while True:
        time.sleep(iv)
        beat()
        spent = int(time.time() - start)
        if spent >= need_sec and not short():
            print(f"     ✓ 출석인정시간 채움 ({spent // 60}분)", flush=True)
            return
        print(f"     … {spent // 60}분 경과", flush=True)


def live_pending(c, only=""):
    """지금 서버의 온라인강의 목록에서 미이수 차시를 모은다. 투두 목록이나 수집본(output/)이 아니라
    수강 과목 전부(비교과 [..] 포함)의 모든 주차를 직접 받는다 — 투두에 안 뜨는 차시도 놓치지 않게."""
    now, rows = datetime.now(), []
    for course in c.courses():
        if only not in course["title"]:
            continue
        c.enter(course["kj"])
        try:
            frames, form = collect_api.menu_frames(c, LIST_FORM, api.ORIGIN + "/ilos/st/course/submain_form.acl")
        except Exception as e:
            print(f"  ✗ {course['title']}: 온라인강의 조회 실패 ({type(e).__name__}) — 직접 확인 필요", flush=True)
            continue
        lt = lectures.LECT_TYPE_RE.search(form)
        for _, frag in frames[1:]:
            for lec in lectures.parse_week(frag):
                lec.update(course=course["title"], kjkey=course["kj"], lect_type=lt.group(1) if lt else "0")
                if lectures.status(lec, now) == "미이수":
                    rows.append(lec)
        print(f"  · {course['title']}: 주차 {len(frames) - 1}개 확인", flush=True)
    rows.sort(key=lambda r: r["end"] or datetime.max)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="온라인강의 출석을 HTTP 로 채운다")
    ap.add_argument("--only", default="", help="과목명에 이 글자가 들어간 차시만")
    ap.add_argument("--code-file", type=Path, help="인증번호를 이 파일에서 읽는다(프롬프트 대신)")
    args = ap.parse_args(argv)

    c = api.Client.from_keychain()
    c.login()
    todo = live_pending(c, args.only)
    if not todo:
        print("채울 차시가 없습니다.")
        return
    second_auth(c, args.code_file)
    for r in todo:
        print(f"▶ {r['course']} {r['week']}주 {r['seq']}차시 {r['title']}", flush=True)
        key = r["kjkey"]
        c.enter(key)
        ref = api.ORIGIN + LIST_FORM
        c.get(LIST_FORM)
        html = c.post(VIEW_FORM, {"lecture_weeks": r["seq"], "WEEK_NO": r["week"], "_KJKEY": key,
                                  "kj_lect_type": r["lect_type"], "item_id": "", "force": "Y"}, referer=ref)
        v = viewer_items(html)
        left = {i["item_id"]: max(0, i["required"] - i["learned"]) for i in r["items"]}
        for item, content, org in v["items"]:
            need = left.get(item, 0)
            if item in left and need == 0:
                continue
            attend_item(c, v, item, content, org, need, api.ORIGIN + VIEW_FORM)
    print("완료. 진도율 확인: ./ec --auto --menus 온라인강의 && ./ec lectures --all")


if __name__ == "__main__":
    main()
