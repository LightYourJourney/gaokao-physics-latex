# 工作日志

> 任务：2007–2026 高考物理真题 LaTeX 重排工程。原则：不凭记忆编造，卷卷有来源。

## 2026-08-05 批次 0：环境检查与样板建立

- **环境**：TeX Live 2026 全量就绪（xelatex + latexmk + Fandol 字体 + 全部宏包），无需安装。
- **仓库盘点**：
  - 素材：仓库内有 2020 全国Ⅰ卷物理 + 2021–2026 湖南卷物理（共 7 套，
    官方 Word 版转 Markdown，含解析与插图）。
  - 版式约定：tasks 选项对齐、emergencystretch、语义环境、四版本壳。
- **脚手架**：`physics/` 建成——`common/`（preamble/macros/
  questions_env/gaokao-physics.sty）、`scripts/`（scaffold_exam/build_all/
  check_manifest/visual_check）、`manifest.csv`（20 行：7 套有源 + 13 套 missing-source）、
  `missing-sources.md`、`WORKLOG.md`。
- **样板：2026 湖南卷**（`2026/hunan-physics/`）
  - 内容：15 题全转录（单选 6 + 多选 4 + 实验 2 + 计算 3），官方题号保留。
  - 图形：16 张 TikZ/circuitikz/pgfplots 重绘（v-t 图、波坐标图、电路、金属板、
    均热板、气球受力、磁悬浮、霍尔装置、数据网格、光路、储能电路、杆球、分裂）；
    3 张非矢量例外保留原图（心形气球、单摆装置照片、表盘照片），已在 metadata 标注。
  - **四个入口全部编译通过**：exam 7 页 / answer-key 8 页 / solutions 15 页 /
    complete 16 页；零 error、零 Overfull、零未定义引用、零缺失字符。
  - 排障记录：circuitikz 标签内 \SI 解析失败（改纯 $R$）；pic angle 不能用裸坐标
    （改预定义 \coordinate）；standalone 测试文档需显式 ctex；\uline 需 ulem（改用
    既有 \gkblank 宏）；15 题答案行过长（拆两行 gkanswer）。

## 批次 1（进行中）：2021–2025 湖南卷 + 2020 全国Ⅰ卷

每套一卷并行转录，逐卷以 diff 审校后合入。

| paper_id | 状态 | 备注 |
|---|---|---|
| 2025-hunan | 待转录 | 25 图 |
| 2024-hunan | 待转录 | 23 图，解析含考点标注 |
| 2023-hunan | 待转录 | 31 图 |
| 2022-hunan | 待转录 | 28 图 |
| 2021-hunan | 待转录 | 37 图（最多），首年 |
| 2020-national-i | 待转录 | 21 图，理综物理部分（题号 14–25+33–34） |

## 决策记录

- **范围裁定**：原计划的收录范围（全国各卷种+各省自主命题）远超仓库素材。
  按「能够核验的」口径，本期只做仓库有素材的 7 套（湖南相关）；其余列
  `missing-source`，不编造。
- **图策略**：坐标图/电路/受力/光路/装置线稿一律 TikZ/circuitikz/pgfplots 重绘；
  照片类（气球、实验装置、表盘）保留原图并标注「非矢量例外」，不冒充矢量。
- **解析类型**：7 套的解析转录自官方 Word 版内嵌解析（`source_embedded`），
  转录时独立复核量纲与符号；无官方解析的年份才用 `reconstructed` 并另行标注。
