#!/usr/bin/env python3
"""notify.py 기준선 비교 단위 테스트 (네트워크 불필요).

실행:  .venv/bin/python -m unittest test_notify -v
"""

import json
import tempfile
import unittest
from pathlib import Path

import notify

W8 = {"date": "2026.10.20", "course": "컴퓨터공학세미나", "kind": "강의자료", "title": "8주차"}
W9 = {"date": "2026.10.27", "course": "컴퓨터공학세미나", "kind": "강의자료", "title": "9주차"}


class DiffSeenTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "seen.json"

    def tearDown(self):
        self.dir.cleanup()

    def test_first_run_reports_nothing_new(self):
        out = notify.diff_seen({"notifications": [W8], "todos": []}, self.path)
        self.assertTrue(out["first_run"])
        self.assertEqual(out["new"], [])

    def test_diff_does_not_touch_baseline(self):
        notify.save_seen({"notifications": [W8], "todos": []}, self.path)
        before = self.path.read_bytes()
        out = notify.diff_seen({"notifications": [W8, W9], "todos": []}, self.path)
        self.assertEqual(out["new"], [W9])
        self.assertEqual(self.path.read_bytes(), before)
        # 후속 처리가 실패해 갱신하지 않았으면 다음 실행도 9주차를 새 것으로 본다.
        again = notify.diff_seen({"notifications": [W8, W9], "todos": []}, self.path)
        self.assertEqual(again["new"], [W9])

    def test_reads_baseline_with_bom(self):
        self.path.write_text(json.dumps({"notifications": [W8]}, ensure_ascii=False), encoding="utf-8-sig")
        out = notify.diff_seen({"notifications": [W8], "todos": []}, self.path)
        self.assertEqual(out["new"], [])

    def test_save_seen_writes_without_bom(self):
        notify.save_seen({"notifications": [W9], "todos": [], "new": [W9]}, self.path)
        raw = self.path.read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn("new", json.loads(raw))


if __name__ == "__main__":
    unittest.main()
