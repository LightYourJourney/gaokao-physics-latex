#!/usr/bin/env python3
"""把下载的高考物理真题 docx 转为清理后的 Markdown。

来源 docx 由方正排版系统导出，pandoc 转换后有三类噪声需要清理：
  1. GFM 数学分隔符 $`...`$ → 标准 $...$（Obsidian/GitHub 通用）
  2. 标点被斜体包裹（0*.*010、*=*）→ 去掉标点上的斜体，保留物理量斜体
  3. <img> 标签携带方正内部 ID（alt="id:...;FounderCES"）→ 标准 Markdown 图片

用法：python3 _build.py [年份...]（不带参数则处理脚本内 META 登记的全部年份）
"""
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
RAW = BASE / "_raw"

# 年份 → (标题, 卷别说明)
META = {
    "2017": ("2017 年全国新课标 Ⅰ 卷 · 理综物理", "全国卷（湖南使用）"),
    "2018": ("2018 年全国新课标 Ⅰ 卷 · 理综物理", "全国卷（湖南使用）"),
    "2019": ("2019 年全国新课标 Ⅰ 卷 · 理综物理", "全国卷（湖南使用）"),
    "2020": ("2020 年全国新课标 Ⅰ 卷 · 理综物理", "全国卷（湖南使用）"),
    "2021": ("2021 年湖南卷 · 物理", "湖南自主命题"),
    "2022": ("2022 年湖南卷 · 物理", "湖南自主命题"),
    "2023": ("2023 年湖南卷 · 物理", "湖南自主命题"),
    "2024": ("2024 年湖南卷 · 物理", "湖南自主命题"),
    "2025": ("2025 年湖南卷 · 物理", "湖南自主命题"),
    "2026": ("2026 年湖南卷 · 物理", "湖南自主命题"),
}


def extract(zip_path: Path, dest_docx: Path) -> bool:
    """从下载的 zip 中取出唯一的 docx（文件名为 GBK 编码，直接按索引取）。"""
    try:
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
            if not names:
                return False
            dest_docx.write_bytes(z.read(names[0]))
            return True
    except zipfile.BadZipFile:
        return False


def clean_latex(m) -> str:
    """清理 LaTeX 公式内部的排版噪声（方正/MathType 导出遗留）。"""
    body = m.group(1)
    # \text{(} \text{)} \text{-} \text{.} 等标点不需要 \text 包裹
    body = re.sub(r"\\text\{([(),.\-+='·　])\}", r"\1", body)
    # \text{2} 这类纯数字上下标
    body = re.sub(r"\\text\{(\d+)\}", r"\1", body)
    # \text{π} → \pi（必须补尾空格，否则 \text{π}n 会粘连成未定义命令 \pin）
    body = body.replace(r"\text{π}", r"\pi ").replace(r"\text{°}", r"^\circ ")
    body = body.replace("·", r"\cdot ")
    # 合并相邻 \text{}：\text{m/s}\text{2} 情况已在上面处理
    body = re.sub(r"\s{2,}", " ", body)
    return f"${body}$"


def clean(md: str) -> str:
    """清理 pandoc GFM 输出中的排版噪声。"""
    # 1. GFM 数学分隔符 $`...`$ → $...$
    md = re.sub(r"\$`(.+?)`\$", r"$\1$", md, flags=re.S)

    # 1b. 公式内部清理
    md = re.sub(r"\$([^$\n]+)\$", clean_latex, md)

    # 2. <img src="x" style="..." alt="..." /> → ![图](x)
    def img_repl(m):
        src = m.group(1)
        return f"![图]({src})"

    md = re.sub(r'<img\s+src="([^"]+)"[^>]*?/>', img_repl, md, flags=re.S)

    # 3. 题号先降级为中性标记 @@N@@，避免被后续的斜体清理规则误伤
    #    （规则 5 会删掉"后跟空白的孤立 **"，正好命中 **11.** 的结尾）
    #    卷头「注意事项 1./2./3.」不是题目，切出来不做转换
    sec = re.search(r"^一[、．]", md, re.M)
    head, body = (md[: sec.start()], md[sec.start():]) if sec else ("", md)
    body = re.sub(r"\*\*(\d+)\*\*\*\.\*\s*", r"@@\1@@", body)
    body = re.sub(r"^(\d{1,2})[．.]\s*(?=[^\d\s])", r"@@\1@@", body, flags=re.M)
    # 卷头里 pandoc 残留的 **1***.* 也要还原成朴素文本
    head = re.sub(r"\*\*(\d+)\*\*\*\.\*\s*", r"\1. ", head)
    md = head + body

    # 4. 纯标点/空白被斜体包裹 → 去掉斜体
    #    覆盖 *.*  *=*  *-*  *,*  *　*  *(*  *)* 等
    md = re.sub(r"\*([\s.,=+\-×÷:;()　]+)\*", r"\1", md)

    # 5. 相邻斜体合并后可能出现的空斜体 ** 或 ****
    md = re.sub(r"(?<!\*)\*\*(?!\*)(?=\s|$)", "", md)
    md = re.sub(r"\*{4,}", "**", md)

    # 5b. 题号还原为 "**N.** "
    #     末尾必须留空格：GFM 中 `**1.**中文` 的右定界符紧跟标点会解析失败，不显示粗体
    md = re.sub(r"@@(\d+)@@\s*", r"**\1.** ", md)

    # 6. 方正软回车残留
    md = md.replace("　　", "　")

    # 6b. 孤立的 = / - 行会被 Markdown 当成 Setext 标题（把上一行整段放大成 <h1>）。
    #     这类行来自被 pandoc 跨行拆开的公式（如「将 r = nR 代入」），与上一行接回去。
    md = re.sub(r"(?<=\S)\n([=\-])\n(?=\S)", r"\1", md)

    # 7. 压缩 3 个以上连续空行
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def build_one(year: str) -> dict:
    zip_path = RAW / f"{year}.zip"
    result = {"year": year, "ok": False, "reason": "", "images": 0, "lines": 0}
    if not zip_path.exists():
        result["reason"] = "未下载到源文件"
        return result

    docx = RAW / f"{year}.docx"
    if not extract(zip_path, docx):
        result["reason"] = "压缩包损坏或非 docx"
        return result

    out_dir = BASE / year
    media_dir = out_dir / "images"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    tmp_md = out_dir / "_tmp.md"
    cmd = [
        "pandoc", "-f", "docx", "-t", "gfm+tex_math_dollars",
        f"--extract-media={out_dir}", str(docx), "-o", str(tmp_md),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        result["reason"] = f"pandoc 失败: {proc.stderr[:120]}"
        return result

    md = tmp_md.read_text(encoding="utf-8")
    tmp_md.unlink()

    # pandoc 把图片放在 <out_dir>/media/，改名为 images/ 并修正路径
    pandoc_media = out_dir / "media"
    if pandoc_media.exists():
        pandoc_media.rename(media_dir)
        md = md.replace(f"{out_dir}/media/", "images/")
        md = md.replace("./media/", "images/")
        md = md.replace("media/", "images/")

    md = clean(md)

    title, juanbie = META[year]
    header = (
        f"# {title}\n\n"
        f"> **卷别**：{juanbie}　|　**含解析**：是　|　"
        f"**来源**：物理备课大师（wl.eywedu.com）Word 版含解析\n"
        f"> **说明**：由来源站 Word 版转换，公式为 LaTeX，图片见同目录 `images/`。\n\n"
        f"---\n\n"
    )
    # 去掉 pandoc 生成的原标题行（通常是 ### 开头的试卷名）
    md = re.sub(r"^#{1,6}\s*\d{4}年[^\n]*\n+", "", md, count=1)

    final = header + md
    out_file = out_dir / f"{year}_物理真题_含解析.md"
    out_file.write_text(final, encoding="utf-8")

    result["ok"] = True
    result["images"] = len(list(media_dir.glob("*"))) if media_dir.exists() else 0
    result["lines"] = final.count("\n")
    result["path"] = str(out_file.relative_to(BASE))
    return result


def main():
    years = sys.argv[1:] or sorted(META)
    rows = []
    for y in years:
        r = build_one(y)
        rows.append(r)
        status = "✅" if r["ok"] else "❌"
        extra = f"{r['lines']} 行 / {r['images']} 图" if r["ok"] else r["reason"]
        print(f"{status} {y}  {extra}")
    ok = sum(1 for r in rows if r["ok"])
    print(f"\n完成 {ok}/{len(rows)}")


if __name__ == "__main__":
    main()
