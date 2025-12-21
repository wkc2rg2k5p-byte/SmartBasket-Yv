#!/usr/bin/env python3
# check_vscode_pyenv.py
"""
一键检查 VS Code Python 环境
"""

import sys, os, subprocess, traceback, json

def _log(msg, ok=None):
    flag = {True: "✅", False: "❌", None: "  "}[ok]
    print(f"{flag} {msg}")

def test_01_interpreter():
    """1. 解释器能否启动"""
    _log(f"Python 解释器版本：{sys.version}")
    assert sys.version_info >= (3, 8), "建议 Python≥3.8"
    return True

def test_02_stdlib():
    """2. 标准库/第三方库能否 import"""
    try:
        import pathlib, venv, datetime, math
        import requests          # 常见第三方
        import numpy as np       # 科学计算
        import pandas as pd      # 数据分析
        return True
    except ImportError as e:
        _log(f"第三方库缺失：{e}", False)
        return False

def test_03_pytest():
    """3. pytest 是否可用"""
    try:
        import pytest
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True, text=True, check=True
        )
        _log(f"pytest 版本：{result.stdout.strip()}")
        return True
    except Exception as e:
        _log(f"pytest 不可用：{e}", False)
        return False

def test_04_debugpy():
    """4. 调试器 debugpy 是否可 import（VS Code 依赖它）"""
    try:
        import debugpy
        _log(f"debugpy 已安装，版本：{debugpy.__version__}")
        return True
    except ImportError:
        _log("debugpy 未安装 → pip install debugpy", False)
        return False

def test_05_black():
    """5. Black 格式化器能否调用"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "black", "--version"],
            capture_output=True, text=True, check=True
        )
        _log(f"Black 版本：{result.stdout.strip()}")
        return True
    except Exception as e:
        _log(f"Black 不可用：{e}", False)
        return False

def test_06_encoding():
    """6. 终端中文编码"""
    try:
        print("中文测试：VS Code 终端编码正常")
        return True
    except UnicodeError:
        _log("终端编码异常，请设置 VS Code 终端为 UTF-8", False)
        return False

def main():
    print("========== VS Code Python 环境自检 ==========")
    tests = [
        test_01_interpreter,
        test_02_stdlib,
        test_03_pytest,
        test_04_debugpy,
        test_05_black,
        test_06_encoding,
    ]
    ok = 0
    for t in tests:
        try:
            ret = t()
            if ret:
                ok += 1
        except Exception as e:
            _log(f"{t.__name__} 异常：{e}", False)
    print("==========================================")
    _log(f"通过 {ok}/{len(tests)} 项", ok == len(tests))
    if ok == len(tests):
        print("🎉 你的 VS Code Python 环境已配置完成！")
    else:
        print("👉 请根据 ❌ 提示安装缺失组件或调整设置。")

if __name__ == "__main__":
    main()