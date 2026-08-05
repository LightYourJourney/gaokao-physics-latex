#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scaffold_exam.py —— 为新年份试卷创建独立 LaTeX 项目骨架。

用法：
    python3 scaffold_exam.py <年份目录名> <paper_id> <卷名> <版式标签>

例：
    python3 scaffold_exam.py 2021/hunan-physics 2021hn "2021 年·湖南卷" physics

会在目标目录生成：metadata.yaml 模板、四个入口壳（exam/answer-key/
solutions/complete）、latexmkrc、content/ 与 figures/ 空目录。
入口壳基于 physics/2026/hunan-physics 的定稿模板。
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATE = ROOT / "2026" / "hunan-physics"


def main() -> int:
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    rel_dir, pid, title = sys.argv[1], sys.argv[2], sys.argv[3]
    dst = ROOT / rel_dir
    if dst.exists():
        print(f"目标目录已存在：{dst}，中止（不覆盖已有成果）")
        return 1
    dst.mkdir(parents=True)

    # 复制壳与配置
    for name in ("exam.tex", "answer-key.tex", "solutions.tex", "complete.tex",
                 "latexmkrc", "metadata.yaml"):
        src = TEMPLATE / name
        text = src.read_text(encoding="utf-8")
        text = text.replace("2026 年·湖南卷", title)
        text = text.replace("2026hn", pid)
        text = text.replace("2026 年湖南卷", title)
        text = text.replace("2026 年·湖南卷 · 物理", f"{title} · 物理")
        (dst / name).write_text(text, encoding="utf-8")

    for sub in ("content", "figures", "photos", "build"):
        (dst / sub).mkdir()
    print(f"✅ 骨架已生成：{dst}")
    print("   下一步：转写 content/questions.tex 与 content/solutions.tex，"
          "绘制 figures/*.tex，再编译四入口。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
