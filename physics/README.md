# 高考物理真题 LaTeX 工程（收录范围 1952–2026）

将可核验的高考物理试题、参考答案与详细解析重排为高质量 LaTeX 项目。
**每套试卷独立成项目、可在自身目录单独编译**；统一 XeLaTeX + ctexart，中文字体由 ctex 按操作系统自动选择。

> 收录范围按 1952–2026 年规划；**当前已建 LaTeX 工程的年份见下方状态表**。
> 没有取得可核验来源的年份不建版式、不凭记忆补写，统一登记于 [missing-sources.md](missing-sources.md)。

## 收录状态（一句话）

- ✅ **已建 LaTeX 工程（9 套）**：2018、2019、2020 全国Ⅰ卷物理部分，2021–2026 湖南卷，
  来源可追溯；每套四入口编译通过。2021、2022 的选考 15/16 与 2018–2020 的 33/34 两题均收录
  （正式作答二选一）。
- ⚠️ **缺失来源**：1952–2017 其余年份全国卷及各省市自主命题卷无仓库素材、
  亦未获免登录含解析源 → 见 [missing-sources.md](missing-sources.md)，**不编造**。
  其中 2017 已核实：中国教育在线的 2017 页面不提供原卷 Word 下载，无可核验来源。
- 📋 全量清单与状态：[manifest.csv](manifest.csv)。

### 已建工程一览

| 年份 | 卷别 | 题量 | 试题/简答/解析/印刷 页数 |
|---|---|---|---|
| 2019 | 全国Ⅰ卷物理部分 | 14（含选考 33/34） | 8 / 9 / 17 / 18 |
| 2018 | 全国Ⅰ卷物理部分 | 14（含选考 33/34） | 8 / 9 / 17 / 18 |
| 2020 | 全国Ⅰ卷物理部分 | 14（含选考 33/34） | 7 / 8 / 18 / 19 |
| 2021 | 湖南卷 | 16（含选考 15/16） | 11 / 12 / 23 / 24 |
| 2022 | 湖南卷 | 16（含选考 15/16） | 10 / 11 / 23 / 24 |
| 2023 | 湖南卷 | 15 | 9 / 10 / 22 / 23 |
| 2024 | 湖南卷 | 15 | 8 / 9 / 20 / 21 |
| 2025 | 湖南卷 | 15 | 9 / 10 / 20 / 21 |
| 2026 | 湖南卷 | 15 | 7 / 8 / 15 / 16 |

> 页数为本机 2026-11-21 全量构建结果；字体/引擎差异可能导致 ±1 页。
> **2018 卷解析来自原卷官方解析（公式由 Word 的 WMF 公式对象逐条读出转写）；
> 2019 卷原卷的公式对象为空占位，缺失处按题干重建并在正文标注「待核」，详见该卷 metadata。**
> 每套卷的图策略、非矢量例外与解析修正逐条见该卷 `metadata.yaml`。

## 结构

```
physics/
├── README.md           本文件
├── WORKLOG.md          计划、批次进度与决策记录
├── manifest.csv        全部试卷及状态（paper_id/year/…/status/notes）
├── missing-sources.md  缺失来源登记
├── build-report.md     构建报告（build_all.py 生成）
├── common/             公共样式（preamble / macros / questions_env / sty）
├── scripts/            自动化脚本（scaffold / build_all / check_manifest / check_content / visual_check）
└── YYYY/<short>-physics/   每套试卷的独立 LaTeX 项目
```

## 每套试卷的四个入口

| 规格名称 | 入口 | 内容 | 用途 |
|---|---|---|---|
| 试题版 | `exam.tex` | 仅试题 | 学生限时练习 |
| 简答版 | `answer-key.tex` | 试题 + 简明答案 | 快速核对 |
| 解析版 | `solutions.tex` | 试题 + 答案 + 详细解析 | 逐题讲解 |
| 印刷版 | `complete.tex` | 先试题，后答案与解析集中 | 完整真题资料、整卷打印 |

四个入口即需求中的「试题版 / 简答版 / 解析版 / 印刷版」；入口文件名沿用仓库既有约定，
不另建中文文件名，避免跨平台编译与脚本路径问题。

四个入口共享 `content/` 下的统一内容（questions/answers-short/solutions），
**不重复维护四份题目文本**。

## 编译

```bash
# 单卷（在卷目录内）：
cd physics/2026/hunan-physics
latexmk -xelatex exam.tex        # 或任一入口
# 一键全量（在仓库根）：
python3 physics/scripts/build_all.py
```

质量门禁：`build_all.py`（编译成败/Overfull/未定义引用/页数；每卷最多编译 4 遍，
日志中不再出现未定义引用或 `Rerun to get` 时才停止——有的卷题目与解析同文档，需 3 遍才能解析完交叉引用）、
`check_manifest.py`（清单与磁盘一致、题量核对；会检查 complete 卷的 PDF，新 clone 须先跑 `build_all.py`）、
`check_content.py`（questions / solutions / answers-short 三处题号覆盖一致）、
`visual_check.py`（PDF 文本层 LaTeX 泄漏/未解析引用）。

## 排版与图形约定

- 物理量斜体、单位正体（siunitx）；矢量 `\bm`；选择题选项 tasks 自动分栏（4/2/1 列）。
- 坐标图/电路/受力/光路/装置线稿一律 **TikZ / circuitikz / pgfplots 矢量重绘**
  （`figures/*.tex`），禁止截图当线稿；照片类保留原图并明确标注「非矢量例外」。
- A4 黑白打印友好，颜色不作唯一信息通道。

## 数据纪律

- 题号保留官方编号；解析类型 `source_embedded`（转录自来源站 Word 版并复核）/
  `reconstructed`（官方只有答案时重写，须与官方答案一致）——见各卷 `metadata.yaml`。
- 来源冲突不静默取舍，登记到 missing-sources.md 待复核。
- 版权：高考真题为公开考试内容，转录的解析归原编写方；本仓库自有的 LaTeX 源、重绘图与脚本采用 CC BY 4.0（见仓库根 `LICENSE`）。
