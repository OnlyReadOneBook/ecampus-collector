"""submit_report.py — 사용자 승인 표시(--user-approved) 없이는 제출하지 않는다(1116 사용자 지시)."""
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(*args):
    return subprocess.run([sys.executable, str(HERE / "submit_report.py"), *args],
                          capture_output=True, text=True, encoding="utf-8")


class T(unittest.TestCase):
    def test_without_approval_refuses_before_login(self):
        r = run("--rt-seq", "1", "--file", "x.docx")
        self.assertEqual(r.returncode, 3)
        self.assertIn("--user-approved", r.stderr + r.stdout)

    def test_dry_run_also_needs_no_approval(self):
        # dry-run 은 제출하지 않으니 막지 않는다 — 파일이 없어 다른 이유로 끝나도 3 은 아니다
        r = run("--rt-seq", "1", "--file", "/nonexistent.docx", "--dry-run")
        self.assertNotEqual(r.returncode, 3)


if __name__ == "__main__":
    unittest.main()
