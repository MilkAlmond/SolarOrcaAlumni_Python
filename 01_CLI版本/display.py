#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""显示模块 - 简化表格输出（保证所有终端对齐）"""

from stats import (
    get_basic_stats,
    get_gender_stats,
    get_industry_stats,
    get_salary_stats,
    get_location_stats,
    get_degree_stats,
    get_year_trend_stats,
    get_data_quality_report,
    filter_data
)


def display_basic_stats(df):
    """显示基本统计信息"""
    stats = get_basic_stats(df)
    print("\n" + "=" * 50)
    print("                  📊 基本统计信息")
    print("=" * 50)
    print(f"  👥 总人数:           {stats['总人数']}")
    print(f"  🎓 校友人数:         {stats['校友人数']}")
    print(f"  👨 男性人数:         {stats['男性人数']}")
    print(f"  👩 女性人数:         {stats['女性人数']}")
    if stats['平均薪资'] > 0:
        print(f"  💰 平均薪资:         ¥{stats['平均薪资']:.0f}")
        print(f"  📈 最高薪资:         ¥{stats['最高薪资']:.0f}")
        print(f"  📉 最低薪资:         ¥{stats['最低薪资']:.0f}")
    print("=" * 50)


def display_gender_stats(df):
    """显示性别比例（简化表格）"""
    gender_stats = get_gender_stats(df)
    print("\n" + "=" * 70)
    print("                   📈 性别比例（按学历）")
    print("=" * 70)
    print(f"{'学历':<12} {'男':>6} {'女':>6} {'总人数':>8} {'男性占比%':>12} {'女性占比%':>12}")
    print("-" * 70)
    for degree, row in gender_stats.iterrows():
        print(f"{degree:<12} {int(row['男']):>6} {int(row['女']):>6} {int(row['总人数']):>8} {row['男性占比(%)']:>11.1f}% {row['女性占比(%)']:>11.1f}%")
    print("=" * 70)


def display_industry_stats(df):
    """显示行业分布（简化表格 + 进度条）"""
    industry_stats = get_industry_stats(df)
    if len(industry_stats) == 0:
        print("\n⚠️ 暂无行业数据")
        return

    print("\n" + "=" * 70)
    print("                      📊 行业分布")
    print("=" * 70)
    print(f"{'行业':<12} {'人数':>6} {'分布图'}")
    print("-" * 70)

    total = industry_stats.sum()
    for industry, count in industry_stats.items():
        pct = count / total * 100
        bar_len = int(pct / 2)
        bar = "█" * bar_len
        print(f"{industry:<12} {count:>6}  {bar}")
    print("-" * 70)
    print(f"  合计: {total} 人")
    print("=" * 70)


def display_salary_stats(df):
    """显示薪资统计（简化表格）"""
    salary_stats = get_salary_stats(df)
    print("\n" + "=" * 70)
    print("                      💰 薪资统计（按专业）")
    print("=" * 70)

    if len(salary_stats) == 0:
        print("  ⚠️ 暂无薪资数据")
        print("=" * 70)
        return

    print(f"{'专业':<14} {'平均薪资':>12} {'人数':>6} {'最低薪资':>12} {'最高薪资':>12}")
    print("-" * 70)
    for major, row in salary_stats.iterrows():
        print(f"{major:<14} {int(row['平均薪资']):>12,} {int(row['人数']):>6} {int(row['最低薪资']):>12,} {int(row['最高薪资']):>12,}")
    print("=" * 70)


def display_location_stats(df):
    """显示所在地分布（简化表格 + 进度条）"""
    location_stats = get_location_stats(df)
    if len(location_stats) == 0:
        print("\n⚠️ 暂无所在地数据")
        return

    print("\n" + "=" * 70)
    print("                      📍 所在地分布")
    print("=" * 70)
    print(f"{'所在地':<12} {'人数':>6} {'分布图'}")
    print("-" * 70)

    total = location_stats.sum()
    for location, count in location_stats.items():
        pct = count / total * 100
        bar_len = int(pct / 2)
        bar = "█" * bar_len
        print(f"{location:<12} {count:>6}  {bar}")
    print("-" * 70)
    print(f"  合计: {total} 人")
    print("=" * 70)


def display_degree_stats(df):
    """显示学历分布（简化表格 + 进度条）"""
    degree_stats = get_degree_stats(df)
    print("\n" + "=" * 70)
    print("                       🎓 学历分布")
    print("=" * 70)
    print(f"{'学历':<12} {'人数':>6} {'分布图'}")
    print("-" * 70)

    total = degree_stats.sum()
    for degree, count in degree_stats.items():
        pct = count / total * 100
        bar_len = int(pct / 2)
        bar = "█" * bar_len
        print(f"{degree:<12} {count:>6}  {bar}")
    print("-" * 70)
    print(f"  合计: {total} 人")
    print("=" * 70)


def display_year_trend(df):
    """显示毕业年份趋势"""
    trend = get_year_trend_stats(df)
    print("\n" + "=" * 70)
    print("                      📈 毕业年份趋势")
    print("=" * 70)

    if len(trend) == 0:
        print("  ⚠️ 暂无毕业年份数据")
        print("=" * 70)
        return

    max_count = trend.max()
    for year, count in trend.items():
        bar_len = int(count / max_count * 40) if max_count > 0 else 0
        bar = "█" * bar_len
        print(f"  {year}: {count:>3} 人  {bar}")
    print("=" * 70)


def display_quality_report(df):
    """显示数据质量报告"""
    report = get_data_quality_report(df)
    print("\n" + "=" * 50)
    print("              📋 数据质量报告")
    print("=" * 50)
    print(f"  📊 总记录数:        {report['总记录数']}")
    print(f"  🔄 重复记录数:      {report['重复记录数']}")
    print("")
    print("  各字段缺失值统计:")
    for col, info in report['字段缺失值'].items():
        missing = info['缺失数']
        pct = info['占比(%)']
        bar = "█" * int(pct / 5) if pct > 0 else ""
        status = "✅" if pct == 0 else "⚠️"
        print(f"    {status} {col}: {missing} ({pct:.1f}%) {bar}")
    print("=" * 50)


def display_data_preview(df):
    """显示数据预览"""
    print("\n" + "=" * 50)
    print("              📋 数据预览（前10行）")
    print("=" * 50)
    print(df.head(10).to_string())
    print(f"\n  总记录数: {len(df)} 条")
    print("=" * 50)


def interactive_filter(df):
    """交互式数据筛选"""
    print("\n" + "=" * 50)
    print("              🔍 数据筛选")
    print("=" * 50)
    print("可筛选字段: 角色, 学历, 专业, 性别, 所在地")

    filtered = df.copy()

    while True:
        print(f"\n当前数据量: {len(filtered)} 条")
        choice = input("请输入要筛选的字段 (角色/学历/专业/性别/所在地/重置/完成): ").strip()

        if choice == '完成':
            break
        elif choice == '重置':
            filtered = df.copy()
            print("✅ 已重置")
            continue
        elif choice in ['角色', '学历', '专业', '性别', '所在地']:
            values = filtered[choice].unique()
            print(f"可选值: {list(values)}")
            val = input(f"请输入 {choice} 的值: ").strip()
            if val:
                filtered = filtered[filtered[choice] == val]
                print(f"✅ 筛选完成，剩余 {len(filtered)} 条记录")
            else:
                print("⚠️ 请输入有效值")
        else:
            print("❌ 无效字段，可选: 角色/学历/专业/性别/所在地")

    return filtered