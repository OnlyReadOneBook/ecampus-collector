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

    def test_multiple_files_are_each_checked_before_login(self):
        # 두 번째 파일이 없으면 로그인 전에 그 파일 이름으로 멈춘다
        ok = HERE / "submit_report.py"
        r = run("--rt-seq", "1", "--file", str(ok), "/nonexistent2.cpp", "--dry-run")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("nonexistent2.cpp", r.stderr + r.stdout)


if __name__ == "__main__":
    unittest.main()
