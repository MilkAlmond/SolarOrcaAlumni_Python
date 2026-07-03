#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""图表模块 - 使用matplotlib生成统计图表"""

import os
import logging
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from stats import (
    get_gender_stats,
    get_industry_stats,
    get_salary_stats,
    get_location_stats
)

# ==================== 抑制字体警告 ====================
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
logging.getLogger('matplotlib').setLevel(logging.ERROR)

# ==================== 解决中文字体问题 ====================
FONT_CANDIDATES = [
    'SimHei',
    'Microsoft YaHei',
    'PingFang SC',
    'Heiti SC',
    'WenQuanYi Zen Hei',
    'Noto Sans CJK SC',
    'Arial Unicode MS',
]

for font in FONT_CANDIDATES:
    try:
        matplotlib.rcParams['font.sans-serif'] = [font, 'DejaVu Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False
        import matplotlib.font_manager as fm

        fm.FontProperties(family=font)
        print(f"✅ 使用字体: {font}")
        break
    except:
        continue


# ==================== 图表生成函数 ====================

def create_gender_pie(df, output_path='output/gender_pie.png'):
    """创建性别比例饼图（按学历分组，保持圆形）"""
    os.makedirs('output', exist_ok=True)

    gender_stats = get_gender_stats(df)
    n = len(gender_stats)

    # 根据子图数量动态调整尺寸
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
    if n == 1:
        axes = [axes]

    colors = ['#FF6B6B', '#006994']

    for idx, (degree, row) in enumerate(gender_stats.iterrows()):
        ax = axes[idx]
        data = [row['男'], row['女']]
        labels = ['男', '女']
        ax.pie(data, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title(f'{degree} 学历性别比例', fontsize=14, fontweight='bold')
        # 强制设置为等比例，保持圆形
        ax.set_aspect('equal')

    plt.suptitle('各学历性别比例分布', fontsize=16, fontweight='bold', y=1.05)
    # 使用 subplots_adjust 而不是 tight_layout，避免覆盖 aspect
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.85, wspace=0.3)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ 性别比例图已保存: {output_path}")
    plt.close()


def create_industry_bar(df, output_path='output/industry_bar.png'):
    """创建行业分布柱状图"""
    os.makedirs('output', exist_ok=True)

    industry_stats = get_industry_stats(df)

    if len(industry_stats) == 0:
        print("⚠️ 行业数据不足，跳过行业分布图生成")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#006994', '#48CAE4', '#F39C12', '#2E8B57', '#E74C3C', '#9B59B6']

    bars = ax.bar(industry_stats.index, industry_stats.values, color=colors[:len(industry_stats)])

    ax.set_xlabel('行业', fontsize=12, fontweight='bold')
    ax.set_ylabel('人数', fontsize=12, fontweight='bold')
    ax.set_title('校友行业分布', fontsize=16, fontweight='bold')

    for bar, val in zip(bars, industry_stats.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                str(val), ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ 行业分布图已保存: {output_path}")
    plt.close()


def create_salary_bar(df, output_path='output/salary_bar.png'):
    """创建各专业平均薪资柱状图"""
    os.makedirs('output', exist_ok=True)

    salary_stats = get_salary_stats(df)

    if len(salary_stats) == 0:
        print("⚠️ 薪资数据不足，跳过薪资图表生成")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(salary_stats)))

    bars = ax.bar(salary_stats.index, salary_stats['平均薪资'], color=colors)

    ax.set_xlabel('专业', fontsize=12, fontweight='bold')
    ax.set_ylabel('平均薪资 (元/月)', fontsize=12, fontweight='bold')
    ax.set_title('各专业校友平均薪资对比', fontsize=16, fontweight='bold')
    ax.tick_params(axis='x', rotation=30, labelsize=10)

    for bar, val in zip(bars, salary_stats['平均薪资']):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
                f'{val:.0f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ 薪资对比图已保存: {output_path}")
    plt.close()


def create_salary_boxplot(df, output_path='output/salary_boxplot.png'):
    """创建薪资分布箱线图"""
    os.makedirs('output', exist_ok=True)

    alumni_df = df[df['角色'] == 'alumni']
    alumni_df = alumni_df[alumni_df['薪资'].notna()]

    if len(alumni_df) < 5:
        print("⚠️ 薪资数据不足，跳过箱线图生成")
        return

    groups = []
    labels = []
    for name, group in alumni_df.groupby('专业'):
        if len(group) >= 3:
            groups.append(group['薪资'].values)
            labels.append(name)

    if len(groups) == 0:
        print("⚠️ 数据不足，跳过箱线图生成")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    box = ax.boxplot(groups, patch_artist=True)
    ax.set_xticklabels(labels, rotation=30, ha='right', fontsize=10)

    for patch in box['boxes']:
        patch.set_facecolor('#48CAE4')
        patch.set_alpha(0.7)

    ax.set_xlabel('专业', fontsize=12, fontweight='bold')
    ax.set_ylabel('薪资 (元/月)', fontsize=12, fontweight='bold')
    ax.set_title('各专业薪资分布箱线图', fontsize=16, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ 薪资箱线图已保存: {output_path}")
    plt.close()


def create_location_pie(df, output_path='output/location_pie.png'):
    """创建所在地分布饼图（保持圆形）"""
    os.makedirs('output', exist_ok=True)

    location_stats = get_location_stats(df)

    if len(location_stats) == 0:
        print("⚠️ 所在地数据不足，跳过所在地分布图生成")
        return

    # 使用正方形画布，确保饼图是圆的
    fig, ax = plt.subplots(figsize=(10, 10))
    colors = plt.cm.Set3(np.linspace(0, 1, len(location_stats)))

    ax.pie(location_stats.values, labels=location_stats.index,
           autopct='%1.1f%%', colors=colors, startangle=90)
    ax.set_title('校友所在地分布', fontsize=16, fontweight='bold')
    # 强制设置为等比例，保持圆形
    ax.set_aspect('equal')

    # 使用 subplots_adjust 而不是 tight_layout，避免覆盖 aspect
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.92)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ 所在地分布图已保存: {output_path}")
    plt.close()


def generate_all_charts(df):
    """生成所有图表"""
    print("\n" + "=" * 50)
    print("              📉 正在生成所有图表...")
    print("=" * 50)

    try:
        create_gender_pie(df)
        create_industry_bar(df)
        create_salary_bar(df)
        create_salary_boxplot(df)
        create_location_pie(df)
        print("\n✅ 所有图表生成完成！")
        print("📁 图表保存在 output/ 目录下")
        print("   - gender_pie.png (性别比例饼图)")
        print("   - industry_bar.png (行业分布柱状图)")
        print("   - salary_bar.png (薪资对比柱状图)")
        print("   - salary_boxplot.png (薪资箱线图)")
        print("   - location_pie.png (所在地分布饼图)")
    except Exception as e:
        print(f"❌ 生成图表时出错: {e}")

    print("=" * 50)