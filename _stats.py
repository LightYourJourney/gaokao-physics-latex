#!/usr/bin/env python3
"""统计各年份湖南卷的考点分布。

方法：按题号把正文切块，每块只取到「答案/解析」出现之前的部分（即题干），
在题干里做关键词命中。这样避免解析中反复提及概念造成的虚高。

局限（务必知悉）：这是关键词命中，不是人工审题。
  - 一道题可能同时命中多个考点（综合题），会重复计入；
  - 题干未出现关键词但实质考查该点的（如受力分析题不写"牛顿定律"），会漏计。
输出仅供交叉参考，最终分级应以人工审题为准。
"""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent

# 考点 → 题干关键词（尽量选题干中会出现的具象词）
TOPICS = {
    "匀变速直线运动": ["匀变速", "初速度", "刹车", "自由落体", "v—t", "v-t", "速度—时间"],
    "受力分析与平衡": ["静止", "光滑斜面", "粗糙", "摩擦因数", "轻绳", "轻杆", "弹簧"],
    "牛顿运动定律": ["牛顿第二定律", "牛顿运动定律", "加速度大小为", "剪断"],
    "平抛与曲线运动": ["平抛", "斜抛", "抛出", "水平抛出"],
    "圆周运动": ["圆周运动", "向心", "角速度", "转动", "转速"],
    "万有引力与天体": ["万有引力", "宇宙速度", "同步", "卫星", "行星", "引力常量"],
    "功和能": ["动能定理", "机械能守恒", "重力势能", "做功", "功率"],
    "动量与碰撞": ["动量", "碰撞", "冲量", "反冲"],
    "静电场": ["电场强度", "电势", "等势", "库仑", "点电荷", "电容"],
    "恒定电流与电路": ["欧姆定律", "电动势", "内阻", "串联", "并联", "多用电表", "滑动变阻器"],
    "磁场": ["磁感应强度", "安培力", "洛伦兹力", "磁场中"],
    "电磁感应": ["感应电动势", "感应电流", "楞次", "磁通量", "切割磁感线"],
    "交变电流与变压器": ["变压器", "交变电流", "有效值", "原线圈", "副线圈"],
    "机械振动与波": ["简谐", "振幅", "波长", "波速", "机械波", "单摆"],
    "光学": ["折射率", "全反射", "干涉", "衍射", "单色光", "棱镜", "透明介质"],
    "热学与气体": ["玻意耳", "查理", "理想气体", "内能", "热力学", "空气柱", "分子"],
    "原子与近代物理": ["衰变", "半衰期", "光电效应", "结合能", "核反应", "光子", "普朗克"],
}

YEARS = ["2021", "2022", "2023", "2024", "2025", "2026"]


def stems(md: str) -> list[str]:
    """按题号切块，每块截断到「答案」之前，返回题干列表。"""
    parts = re.split(r"^\*\*(\d{1,2})\.\*\*", md, flags=re.M)
    out = []
    # parts = [前言, 号, 内容, 号, 内容, ...]
    for i in range(1, len(parts) - 1, 2):
        body = parts[i + 1]
        cut = re.search(r"【答案】|【解析】|^答案|^解析", body, re.M)
        out.append(body[: cut.start()] if cut else body)
    return out


def main():
    table = {t: {} for t in TOPICS}
    for y in YEARS:
        f = BASE / y / f"{y}_物理真题_含解析.md"
        if not f.exists():
            continue
        blocks = stems(f.read_text(encoding="utf-8"))
        for topic, kws in TOPICS.items():
            hit = sum(1 for b in blocks if any(k in b for k in kws))
            table[topic][y] = hit

    width = max(len(t) for t in TOPICS) + 2
    header = "考点".ljust(width) + "".join(y.rjust(6) for y in YEARS) + "   年份覆盖"
    print(header)
    print("-" * len(header))
    rows = []
    for topic, per in table.items():
        covered = sum(1 for y in YEARS if per.get(y, 0) > 0)
        rows.append((covered, topic, per))
    for covered, topic, per in sorted(rows, key=lambda r: -r[0]):
        line = topic.ljust(width) + "".join(str(per.get(y, 0)).rjust(6) for y in YEARS)
        print(f"{line}   {covered}/6 年")


if __name__ == "__main__":
    main()
