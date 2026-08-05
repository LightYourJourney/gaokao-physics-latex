#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""visual_check.py —— PDF 版面机械检查（不依赖人眼）。

对每个 complete 项目的四个 PDF 运行：
  - 页数（非空、非异常跳变）；
  - pdftotext 抽文本：检查是否有 LaTeX 命令泄漏（\gkti、\begin 等原文残留）；
  - 检查是否有「??」未解析引用残留在文本层。
依赖：pdftotext（poppler）。
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ("exam", "answer-key", "solutions", "complete")


def check_pdf(pdf: Path) -> dict:
    r = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True)
    text = r.stdout
    leaks = []
    for pat in (r"\\gkti", r"\\gkanswer", r"\\begin\{", r"\\input", r"\\gkfig",
                r"\\gksolhead", r"\\gkpart"):
        if re.search(pat, text):
            leaks.append(pat)
    qmarks = len(re.findall(r"\?\?", text))
    return {"leaks": leaks, "qmarks": qmarks, "chars": len(text)}


def main() -> int:
    problems = []
    total = 0
    for ydir in sorted(ROOT.iterdir()):
        if not ydir.is_dir() or not re.fullmatch(r"\d{4}", ydir.name):
            continue
        for pdir in sorted(ydir.iterdir()):
            if not (pdir / "exam.tex").exists():
                continue
            for e in ENTRIES:
                pdf = pdir / f"{e}.pdf"
                if not pdf.exists():
                    problems.append(f"{pdir.name}/{e}.pdf 缺失")
                    continue
                total += 1
                st = pdf.stat()
                if st.st_size == 0:
                    problems.append(f"{pdir.name}/{e}.pdf 为空")
                    continue
                c = check_pdf(pdf)
                if c["leaks"]:
                    problems.append(f"{pdir.name}/{e}.pdf 文本层含 LaTeX 泄漏: {c['leaks']}")
                if c["qmarks"]:
                    problems.append(f"{pdir.name}/{e}.pdf 文本层含 {c['qmarks']} 处未解析引用 '??'")
                if c["chars"] < 200:
                    problems.append(f"{pdir.name}/{e}.pdf 文本量异常少 ({c['chars']} 字符)")

    print(f"检查 {total} 个 PDF")
    if problems:
        print(f"发现 {len(problems)} 个问题：")
        for p in problems:
            print("  ⚠️", p)
        return 1
    print("✅ 全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
