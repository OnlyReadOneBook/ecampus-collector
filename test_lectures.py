#!/usr/bin/env python3
"""온라인강의 주차 조각 파싱 단위 테스트 (네트워크 불필요).

실행:  .venv/bin/python -m unittest test_lectures -v
"""
import unittest
from datetime import datetime

import lectures


def box(n, title, period, name, bar, per, times, item="ITEM1", week="9", seq="2"):
    return (f'<div id="lecture-{n}" class="lecture-box" style=""><div style="font-weight: bold;font-size: 16px;">'
            f'{title}</div><div> 출석인정기간 : {period} </div>'
            f'<span onclick="viewGo(\'{week}\', \'{seq}\', \'202610261030\', \'202610261742\',\'{item}\');">{name}</span>'
            f'<div style="background-image: url(/ilos/images/common/pbar-ani.gif); width: {bar}%; height: 100%;"></div>'
            f'<div id="per_text" style="color:#fff">{per}%</div><div style="float: left;">{times}</div>')


FRAG = (box(1, "1차시 네트워크", "2026.10.19 오전 12:00 ~  2026.10.26 오전 10:30",
            "네트워크 10.26", 0, 100, "0:00 / 0:00 / 1:17:54")
        + box(2, "2차시 정렬", "2026.09.10 오전 12:00 ~  2026.09.27 오후 11:59",
              "Lecture_3", 313, 100, "1:32:22 / 0:00 / 29:30", seq="3"))


class TestParseWeek(unittest.TestCase):
    def setUp(self):
        self.rows = lectures.parse_week(FRAG)

    def test_fields(self):
        r = self.rows[0]
        self.assertEqual((r["week"], r["seq"], r["title"]), ("9", "2", "1차시 네트워크"))
        self.assertEqual(r["end"], datetime(2026, 10, 26, 10, 30))
        self.assertEqual(self.rows[1]["end"], datetime(2026, 9, 27, 23, 59))
        self.assertEqual(r["items"][0]["required"], 77 * 60 + 54)

    def test_progress_from_bar_not_per_text(self):
        # per_text 는 100% 인데 막대 폭 0% · 학습 0분 → 미이수로 봐야 한다
        self.assertFalse(lectures.done(self.rows[0]))
        self.assertTrue(lectures.done(self.rows[1]))

    def test_status(self):
        self.assertEqual(lectures.status(self.rows[0], datetime(2026, 10, 20)), "미이수")
        self.assertEqual(lectures.status(self.rows[0], datetime(2026, 10, 27)), "기간지남")
        self.assertEqual(lectures.status(self.rows[0], datetime(2026, 10, 1)), "예정")


if __name__ == "__main__":
    unittest.main()
