# 高考物理真题 LaTeX 工程（2007–2026）

将可核验的高考物理试题、参考答案与详细解析重排为高质量 LaTeX 项目。
**每套试卷独立成项目、可在自身目录单独编译**；统一 XeLaTeX + ctexart + Fandol 字体。

## 收录状态（一句话）

- ✅ **有来源、已收录**：2021–2026 湖南卷（6 套）+ 2020 全国Ⅰ卷物理部分（1 套），
  全部转录自仓库内的官方 Word 版（含解析），来源可追溯。
- ⚠️ **缺失来源**：2007–2019 其余各年全国卷及各省市自主命题卷无仓库素材、
  亦未获免登录含解析源 → 见 [missing-sources.md](missing-sources.md)，**不编造**。
- 📋 全量清单与状态：[manifest.csv](manifest.csv)。

## 结构

```
physics/
├── README.md           本文件
├── WORKLOG.md          计划、批次进度与决策记录
├── manifest.csv        全部试卷及状态（paper_id/year/…/status/notes）
├── missing-sources.md  缺失来源登记
├── build-report.md     构建报告（build_all.py 生成）
├── common/             公共样式（preamble / macros / questions_env / sty）
├── scripts/            自动化脚本（scaffold / build_all / check_manifest / visual_check）
└── YYYY/<short>-physics/   每套试卷的独立 LaTeX 项目
```

## 每套试卷的四个入口

| 入口 | 内容 | 用途 |
|---|---|---|
| `exam.tex` | 仅试题 | 学生限时练习 |
| `answer-key.tex` | 试题 + 简明答案 | 快速核对 |
| `solutions.tex` | 试题 + 答案 + 详细解析 | 逐题讲解 |
| `complete.tex` | 先试题，后答案与解析集中 | 完整真题资料 |

四个入口共享 `content/` 下的统一内容（questions/answers-short/solutions），
**不重复维护四份题目文本**。

## 编译

```bash
cd physics/2026/hunan-physics
latexmk -xelatex exam.tex        # 或任一入口
# 一键全量：
python3 physics/scripts/build_all.py
```

质量门禁：`build_all.py`（编译成败/Overfull/未定义引用/页数）、
`check_manifest.py`（清单与磁盘一致、题量核对）、`visual_check.py`（PDF 文本层
LaTeX 泄漏/未解析引用）。

## 排版与图形约定

- 物理量斜体、单位正体（siunitx）；矢量 `\bm`；选择题选项 tasks 自动分栏（4/2/1 列）。
- 坐标图/电路/受力/光路/装置线稿一律 **TikZ / circuitikz / pgfplots 矢量重绘**
  （`figures/*.tex`），禁止截图当线稿；照片类保留原图并明确标注「非矢量例外」。
- A4 黑白打印友好，颜色不作唯一信息通道。

## 数据纪律

- 题号保留官方编号；解析类型 `source_embedded`（转录自官方 Word 版并复核）/
  `reconstructed`（官方只有答案时重写，须与官方答案一致）——见各卷 `metadata.yaml`。
- 来源冲突不静默取舍，登记到 missing-sources.md 待复核。
- 版权：高考真题为公开考试内容，解析归原编写方；本库仅供个人教学备课，勿再分发。
