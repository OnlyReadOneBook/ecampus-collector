from watch import key, new_items, wanted


def n(course, kind, title="t", date="2026.10.31 토요일"):
    return {"date": date, "course": course, "kind": kind, "title": title}


def test_wanted_kinds():
    assert wanted(n("알고리즘(002)", "온라인강의"))
    assert wanted(n("알고리즘(002)", "강의자료"))
    assert wanted(n("컴퓨터공학세미나(001)", "과제"))
    assert not wanted(n("알고리즘(002)", "과제"))
    assert not wanted(n("컴퓨터공학세미나(001)", "공지"))


def test_new_items_skips_seen():
    a, b = n("알고리즘", "온라인강의", "9주"), n("알고리즘", "온라인강의", "10주")
    assert new_items([a, b], {key(a)}) == [b]
