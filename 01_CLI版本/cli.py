#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""命令行参数模块 - 解析命令行参数"""

import argparse


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='SolarOrca 校友数据分析系统',
        epilog='示例: python analysis_cli.py --stats'
    )
    parser.add_argument('-f', '--file', default='data/alumni_data.csv',
                        help='数据文件路径 (默认: data/alumni_data.csv)')
    parser.add_argument('-o', '--output', default='output',
                        help='输出目录 (默认: output)')
    parser.add_argument('--stats', action='store_true',
                        help='显示基本统计信息')
    parser.add_argument('--gender', action='store_true',
                        help='显示性别比例')
    parser.add_argument('--industry', action='store_true',
                        help='显示行业分布')
    parser.add_argument('--salary', action='store_true',
                        help='显示薪资统计')
    parser.add_argument('--charts', action='store_true',
                        help='生成所有图表')
    parser.add_argument('--export', action='store_true',
                        help='导出统计结果 (CSV)')
    parser.add_argument('--json', action='store_true',
                        help='导出 JSON 报告')
    parser.add_argument('--pdf', action='store_true',
                        help='导出 PDF 报告')
    return parser.parse_args()