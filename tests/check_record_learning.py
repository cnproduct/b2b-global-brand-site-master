#!/usr/bin/env python3
"""Tests for scripts/record_learning.py."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD_SCRIPT = ROOT / "scripts/record_learning.py"


def test_record_learning():
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "sub/candidates.jsonl"

        # 1. Successful record
        cmd = [
            sys.executable,
            str(RECORD_SCRIPT),
            "--category",
            "安全与防护",
            "--observation",
            "边缘防护脚本默认拦截高频异常抓取，但未对特定合规 AI 爬虫做 UA 与速率白名单区分。",
            "--outcome",
            "离线模拟测试中合规抓取请求被误判限流，补充受控 UA 白名单后验证通过。",
            "--suggestion",
            "在 Workers 防护层增加针对规范搜索引擎与 AI 爬虫的显式白名单与定向流控策略。",
            "--evidence",
            "代码验证",
            "--output-file",
            str(target),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0, f"Failed: {res.stderr}"
        assert "已保存本地候选" in res.stdout

        # Verify file exists and permission is 0600
        assert target.exists()
        assert target.stat().st_mode & 0o077 == 0

        # Verify entry schema
        data = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line]
        assert len(data) == 1
        assert data[0]["category"] == "安全与防护"
        assert "fingerprint" in data[0]

        # 2. Duplicate detection
        res_dup = subprocess.run(cmd, capture_output=True, text=True)
        assert res_dup.returncode == 0
        assert "已有同一候选，未重复保存" in res_dup.stdout
        data_after = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line]
        assert len(data_after) == 1

        # 3. Reject sensitive content (URL, API token, email)
        sensitive_cases = [
            ("包含网址", "请看 https://example.com/api"),
            ("包含路径", "检查 /Users/happy/project/file.txt"),
            ("包含Token", "使用 api_key_12345678 进行鉴权"),
            ("包含邮箱", "联系 contact@domain.com"),
            ("包含底价", "工厂内部底价为 15 元"),
        ]
        for name, bad_text in sensitive_cases:
            bad_cmd = [
                sys.executable,
                str(RECORD_SCRIPT),
                "--category",
                "行业与资料",
                "--observation",
                bad_text,
                "--outcome",
                "测试拦截",
                "--suggestion",
                "测试拦截",
                "--evidence",
                "待核实",
                "--output-file",
                str(target),
            ]
            res_bad = subprocess.run(bad_cmd, capture_output=True, text=True)
            assert res_bad.returncode != 0, f"Should reject {name}"
            assert "请使用不含身份" in res_bad.stderr

    print("PASS: record_learning tests passed.")


if __name__ == "__main__":
    test_record_learning()
