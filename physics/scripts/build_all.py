#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_all.py —— 遍历全部试卷项目，编译四个入口，汇总质量报告。

用法：python3 build_all.py [年份...]
不带参数则遍历所有含 exam.tex 的项目目录。

对每个项目：
  - 依次编译 exam / answer-key / solutions / complete（xelatex 两遍，第二遍解析交叉引用）；
  - 解析 .log：错误、未定义引用、Overfull、Missing character、PDF 页数；
  - 汇总输出 build-report.md 并打印摘要。
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ("exam", "answer-key", "solutions", "complete")


def compile_one(pdir: Path) -> dict:
    out = {"dir": pdir.relative_to(ROOT).as_posix(), "ok": {}, "errors": [], "warnings": {}}
    for entry in ENTRIES:
        tex = pdir / f"{entry}.tex"
        if not tex.exists():
            out["errors"].append(f"{entry}: 无源文件")
            continue
        for _ in range(2):  # 题号回链要两遍才能解析
            r = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error", entry],
                cwd=pdir, capture_output=True, text=True)
            if r.returncode != 0:
                break
        log = pdir / f"{entry}.log"
        errs = 0
        if not log.exists():
            out["ok"][entry] = False
            out["errors"].append(f"{entry}: 无日志")
            continue
        text = log.read_text(encoding="utf-8", errors="ignore")
        errs = len(re.findall(r"^!", text, re.M))
        undef = len(re.findall(r"Reference .* undefined|LaTeX Warning: Reference", text))
        overfull = len(re.findall(r"Overfull \\hbox", text))
        missing = len(re.findall(r"Missing character", text))
        pages = re.search(r"Output written on .*?\((\d+) pages?", text)
        out["ok"][entry] = r.returncode == 0 and errs == 0 and undef == 0
        out["warnings"][entry] = {
            "errors": errs, "undefined": undef, "overfull": overfull,
            "missing_char": missing,
            "pages": int(pages.group(1)) if pages else 0}
        if errs:
            first = re.search(r"^!.*$", text, re.M)
            out["errors"].append(f"{entry}: {errs} 错误 | 首个: {first.group(0)[:80]}")
    return out


def main() -> int:
    years = sys.argv[1:] or sorted(p.name for p in ROOT.iterdir()
                                   if p.is_dir() and re.fullmatch(r"\d{4}", p.name))
    results = []
    for y in years:
        for pdir in sorted((ROOT / y).iterdir()):
            if (pdir / "exam.tex").exists():
                results.append(compile_one(pdir))

    complete_n = sum(1 for r in results if all(r["ok"].values()))
    print(f"共 {len(results)} 个项目，{complete_n} 个四版本全部通过\n")
    for r in results:
        tag = "✅" if all(r["ok"].values()) else "❌"
        detail = " | ".join(
            f"{e}:{'OK' if r['ok'][e] else 'FAIL'}({r['warnings'][e]['pages']}页, "
            f"溢出{r['warnings'][e]['overfull']}, 未定义{r['warnings'][e]['undefined']})"
            for e in ENTRIES if e in r["ok"])
        print(f"{tag} {r['dir']}\n    {detail}")
        for e in r["errors"]:
            print(f"    ⚠️ {e}")

    # 写 build-report.md
    report = ROOT / "build-report.md"
    lines = ["# 构建报告", "", f"> 生成时间：本批次", f"> 项目数：{len(results)}，全通过：{complete_n}", ""]
    for r in results:
        lines.append(f"## {r['dir']}")
        lines.append("")
        for e in ENTRIES:
            if e in r["warnings"]:
                w = r["warnings"][e]
                lines.append(f"- {e}.pdf：{'✅' if r['ok'][e] else '❌'} "
                             f"{w['pages']} 页 | 错误 {w['errors']} | "
                             f"Overfull {w['overfull']} | 未定义引用 {w['undefined']} | "
                             f"缺失字符 {w['missing_char']}")
        if r["errors"]:
            lines.append("- 错误详情：")
            for e in r["errors"]:
                lines.append(f"  - {e}")
        lines.append("")
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n报告已写入 {report.relative_to(ROOT.parent)}")
    return 0 if complete_n == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
