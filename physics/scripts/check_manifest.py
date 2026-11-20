#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_manifest.py —— 校验 manifest.csv 与磁盘结构的机械一致性。

检查项：
  1. manifest 中的每个 paper 目录是否存在；
  2. 每个标记 complete 的试卷四入口 PDF 是否都存在且非零字节；
  3. 题量字段与 content/questions.tex 中 \begin{question} 计数是否一致；
  4. 试卷目录是否都有 metadata.yaml。
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def count_questions(content_tex: Path) -> int:
    text = content_tex.read_text(encoding="utf-8")
    return len(re.findall(r"\\begin\{question\}", text))


def main() -> int:
    manifest = ROOT / "manifest.csv"
    if not manifest.exists():
        print("❌ manifest.csv 不存在")
        return 1
    rows = list(csv.DictReader(manifest.open(encoding="utf-8")))
    print(f"manifest 共 {len(rows)} 行\n")
    problems = []
    for r in rows:
        # paper_id 形如 2026-hunan / 2020-national-i → 目录 年份/短名-physics
        year = r["year"]
        # 目录名约定：去掉「年份-」前缀后整体作为短名（短名自身可含连字符）
        short = r["paper_id"][len(year) + 1:]
        pdir = ROOT / year / f"{short}-physics"
        status = r["status"]
        if status in ("missing-source", "pending", "needs-review"):
            continue  # 无来源/待发布/暂停批次，本就无目录
        if not pdir.exists():
            problems.append(f"[{r['paper_id']}] 目录缺失: {pdir.relative_to(ROOT)}")
            continue
        if not (pdir / "metadata.yaml").exists():
            problems.append(f"[{r['paper_id']}] 缺 metadata.yaml")
        if status == "complete":
            for entry in ("exam", "answer-key", "solutions", "complete"):
                pdf = pdir / f"{entry}.pdf"
                if not pdf.exists() or pdf.stat().st_size == 0:
                    problems.append(f"[{r['paper_id']}] 缺 {entry}.pdf")
        qtex = pdir / "content" / "questions.tex"
        if qtex.exists() and r.get("question_count"):
            n = count_questions(qtex)
            if n != int(r["question_count"]):
                problems.append(
                    f"[{r['paper_id']}] 题量不符: manifest={r['question_count']} "
                    f"questions.tex={n}")

    if problems:
        print("发现 " + str(len(problems)) + " 个问题：")
        for p in problems:
            print("  ⚠️", p)
        return 1
    print("✅ manifest 与磁盘结构一致")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
