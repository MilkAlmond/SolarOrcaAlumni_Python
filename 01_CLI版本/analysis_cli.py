#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SolarOrca 校友数据分析系统 - 命令行版（模块化版本）

模块组成：
  - data_loader.py  : 数据加载 + 示例数据生成
  - stats.py        : 统计函数
  - display.py      : 数据显示（美化表格）
  - charts.py       : 图表生成（matplotlib）
  - export.py       : 导出功能（CSV + JSON + PDF）
  - cli.py          : 命令行参数解析
  - config.py       : 配置文件

作者: 你的名字
班级: 工商2301
学号: 20230001
日期: 2026-07-02
"""

import sys
import logging
import os
from datetime import datetime

from data_loader import load_data
from display import (
    display_basic_stats,
    display_gender_stats,
    display_industry_stats,
    display_salary_stats,
    display_location_stats,
    display_degree_stats,
    display_quality_report,
    display_data_preview,
    display_year_trend,
    interactive_filter
)
from charts import generate_all_charts
from export import export_results, export_json_report, export_pdf_report
from cli import parse_args
from config import load_config


def setup_logging():
    """设置日志记录（只保存到文件，不在终端显示）"""
    os.makedirs('logs', exist_ok=True)
    log_file = f"logs/analysis_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8')
            # 移除 StreamHandler，不再输出到终端
        ]
    )
    return logging.getLogger(__name__)


def display_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("         SolarOrca 校友数据分析系统")
    print("=" * 60)
    print("  1. 📊 显示基本统计信息")
    print("  2. 📈 查看性别比例（按学历）")
    print("  3. 📊 查看行业分布")
    print("  4. 💰 查看薪资统计（按专业）")
    print("  5. 📍 查看所在地分布")
    print("  6. 🎓 查看学历分布")
    print("  7. 📋 数据质量报告")
    print("  8. 📈 毕业年份趋势")
    print("  9. 📉 生成所有图表")
    print(" 10. 💾 导出统计结果 (CSV)")
    print(" 11. 📁 导出 JSON 报告")
    print(" 12. 📄 导出 PDF 报告")
    print(" 13. 🔍 数据筛选")
    print(" 14. 📋 显示所有数据预览")
    print(" 15. 🔄 重新加载数据")
    print("  0. 🚪 退出程序")
    print("-" * 60)


def get_user_choice():
    """获取用户输入（带验证）"""
    valid_choices = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                     '10', '11', '12', '13', '14', '15']
    while True:
        choice = input("\n请输入您的选择 (0-15): ").strip()
        if choice in valid_choices:
            return choice
        print("❌ 无效输入，请输入 0-15 之间的数字")


def main():
    """主程序入口"""
    # 加载配置
    config = load_config()

    # 设置日志
    logger = setup_logging()
    logger.info("程序启动")

    # 解析命令行参数
    args = parse_args()

    # 加载数据
    df = load_data(args.file if hasattr(args, 'file') else config.get('data_file', 'data/alumni_data.csv'))

    # 命令行模式
    if any([args.stats, args.gender, args.industry, args.salary,
            args.charts, args.export, args.json, args.pdf]):
        print("\n🔧 命令行模式运行中...\n")
        if args.stats:
            display_basic_stats(df)
        if args.gender:
            display_gender_stats(df)
        if args.industry:
            display_industry_stats(df)
        if args.salary:
            display_salary_stats(df)
        if args.charts:
            generate_all_charts(df)
        if args.export:
            export_results(df)
        if args.json:
            export_json_report(df)
        if args.pdf:
            export_pdf_report(df)
        logger.info("命令行模式执行完成")
        return

    # 交互式菜单模式
    print("\n" + "🐋" * 15 + " SolarOrca 校友数据分析系统 " + "🐋" * 15)

    while True:
        display_menu()
        choice = get_user_choice()

        try:
            if choice == '0':
                print("\n👋 感谢使用，再见！")
                logger.info("程序正常退出")
                sys.exit(0)

            elif choice == '1':
                display_basic_stats(df)

            elif choice == '2':
                display_gender_stats(df)

            elif choice == '3':
                display_industry_stats(df)

            elif choice == '4':
                display_salary_stats(df)

            elif choice == '5':
                display_location_stats(df)

            elif choice == '6':
                display_degree_stats(df)

            elif choice == '7':
                display_quality_report(df)

            elif choice == '8':
                display_year_trend(df)

            elif choice == '9':
                generate_all_charts(df)

            elif choice == '10':
                export_results(df)

            elif choice == '11':
                export_json_report(df)

            elif choice == '12':
                export_pdf_report(df)

            elif choice == '13':
                df = interactive_filter(df)
                print(f"✅ 当前数据: {len(df)} 条记录")

            elif choice == '14':
                display_data_preview(df)

            elif choice == '15':
                df = load_data(args.file if hasattr(args, 'file') else 'data/alumni_data.csv')
                print("✅ 数据已重新加载")

        except KeyboardInterrupt:
            print("\n\n👋 程序被中断，再见！")
            logger.info("程序被用户中断")
            sys.exit(0)
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            logger.error(f"错误: {e}")

        input("\n按 Enter 键继续...")


if __name__ == "__main__":
    main()