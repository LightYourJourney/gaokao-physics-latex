#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_content.py —— 校验每套试卷三份共享内容的题号覆盖是否一致。

检查项：
  1. questions.tex 的 \\begin{question} 数与 \\gkti{...} 题号数一致；
  2. solutions.tex 的 \\begin{answer} 数与 \\gksolhead{...} 题号数一致；
  3. answers-short.tex 中每个 \\textbf{N.} 题号都能在试题中找到；
  4. 三份文件的题号集合完全相同（不缺、不多、不重复）。

用法：python3 check_content.py [年份...]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def nums(pattern: str, text: str) -> list[str]:
    return re.findall(pattern, text)


def check_project(pdir: Path) -> list[str]:
    problems = []
    qtex = pdir / "content" / "questions.tex"
    stex = pdir / "content" / "solutions.tex"
    atex = pdir / "content" / "answers-short.tex"
    for p in (qtex, stex, atex):
        if not p.exists():
            problems.append(f"缺文件: {p.relative_to(pdir)}")
            return problems

    qt = qtex.read_text(encoding="utf-8")
    st = stex.read_text(encoding="utf-8")
    at = atex.read_text(encoding="utf-8")

    qcount = len(re.findall(r"\\begin\{question\}", qt))
    qnums = nums(r"\\gkti\{([^{}]+)\}", qt)
    anscount = len(re.findall(r"\\begin\{answer\}", st))
    snums = nums(r"\\gksolhead\{([^{}]+)\}", st)
    bnums = nums(r"\\textbf\{([0-9]+)\.\}", at)
    # 选择题答案常以「题号 & 1 & 2 & ...」表格给出，补采每一行题号
    for m in re.findall(r"题号\s*&(.*?)\\\\", at, re.S):
        bnums += re.findall(r"\d+", m)
    # 「第 10 题：...」形式的单题答案
    bnums += re.findall(r"第\s*(\d+)\s*题", at)

    if qcount != len(qnums):
        problems.append(f"questions: {qcount} 个 question 环境，但 {len(qnums)} 个 \\gkti 题号")
    if anscount != len(snums):
        problems.append(f"solutions: {anscount} 个 answer 环境，但 {len(snums)} 个 \\gksolhead 题号")

    for name, seq in (("questions", qnums), ("solutions", snums), ("answers-short", bnums)):
        dup = sorted({n for n in seq if seq.count(n) > 1})
        if dup:
            problems.append(f"{name}: 题号重复 {dup}")

    qs, ss, bs = set(qnums), set(snums), set(bnums)
    if qs != ss:
        problems.append(f"试题/解析题号不一致: 仅试题 {sorted(qs - ss)}，仅解析 {sorted(ss - qs)}")
    if qs != bs:
        problems.append(f"试题/简答题号不一致: 仅试题 {sorted(qs - bs)}，仅简答 {sorted(bs - qs)}")

    return problems


def main() -> int:
    years = sys.argv[1:]
    if not years:
        years = sorted(p.name for p in ROOT.iterdir()
                       if p.is_dir() and re.fullmatch(r"\d{4}", p.name))
    problems = []
    total = 0
    for y in years:
        ydir = ROOT / y
        if not ydir.is_dir():
            continue
        for pdir in sorted(ydir.iterdir()):
            if not (pdir / "exam.tex").exists():
                continue
            total += 1
            for msg in check_project(pdir):
                problems.append(f"[{pdir.relative_to(ROOT)}] {msg}")

    print(f"检查 {total} 个项目")
    if problems:
        print(f"发现 {len(problems)} 个问题：")
        for p in problems:
            print("  ⚠️", p)
        return 1
    print("✅ 三份共享内容的题号覆盖一致")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
