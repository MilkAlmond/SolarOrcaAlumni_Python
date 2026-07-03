#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""导出模块 - 导出统计结果为 CSV、JSON 和 PDF"""

import os
import json
import glob
import pandas as pd
from datetime import datetime

from stats import (
    get_basic_stats,
    get_gender_stats,
    get_industry_stats,
    get_salary_stats,
    get_location_stats,
    get_degree_stats
)


def clean_old_pdfs(output_dir='output'):
    """删除所有旧的 PDF 报告文件（report*.pdf）"""
    pdf_files = glob.glob(os.path.join(output_dir, 'report*.pdf'))
    if not pdf_files:
        return

    for f in pdf_files:
        try:
            os.remove(f)
            print(f"🗑️ 已删除旧文件: {os.path.basename(f)}")
        except Exception as e:
            print(f"⚠️ 无法删除 {f}: {e}")


def export_results(df, output_path='output/stats_summary.csv'):
    """导出统计结果到 CSV 文件"""
    os.makedirs('output', exist_ok=True)

    basic_stats = get_basic_stats(df)
    gender_stats = get_gender_stats(df)
    industry_stats = get_industry_stats(df)
    salary_stats = get_salary_stats(df)
    location_stats = get_location_stats(df)

    results = []

    results.append(['=== 基础统计 ===', '', ''])
    for key, value in basic_stats.items():
        results.append([key, value, ''])

    results.append(['', '', ''])
    results.append(['=== 性别比例（按学历）===', '', ''])
    for degree, row in gender_stats.iterrows():
        results.append([f'{degree}', f'男: {row["男"]}, 女: {row["女"]}',
                        f'总: {row["总人数"]}'])

    results.append(['', '', ''])
    results.append(['=== 行业分布 ===', '', ''])
    for industry, count in industry_stats.items():
        results.append([industry, count, ''])

    results.append(['', '', ''])
    results.append(['=== 平均薪资（按专业）===', '', ''])
    for major, row in salary_stats.iterrows():
        results.append([major, f"¥{row['平均薪资']:.0f}", f"人数: {row['人数']}"])

    results.append(['', '', ''])
    results.append(['=== 所在地分布 ===', '', ''])
    for location, count in location_stats.items():
        results.append([location, count, ''])

    df_results = pd.DataFrame(results, columns=['类别', '统计值', '备注'])
    df_results.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ 统计结果已导出: {output_path}")


def export_json_report(df, output_path='output/stats_summary.json'):
    """导出统计结果为 JSON 格式"""
    os.makedirs('output', exist_ok=True)

    try:
        result = {
            '导出时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '总记录数': len(df),
            '基本统计': get_basic_stats(df),
            '性别比例': get_gender_stats(df).to_dict(),
            '行业分布': get_industry_stats(df).to_dict(),
            '薪资统计': get_salary_stats(df).to_dict(),
            '所在地分布': get_location_stats(df).to_dict(),
            '学历分布': get_degree_stats(df).to_dict()
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ JSON 报告已导出: {output_path}")
    except Exception as e:
        print(f"❌ 导出 JSON 失败: {e}")


def export_pdf_report(df, output_path='output/report.pdf'):
    """导出 PDF 报告（支持中文，自动清理旧文件）"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch, cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        os.makedirs('output', exist_ok=True)

        # ========== 清理所有旧的 PDF 文件 ==========
        clean_old_pdfs('output')

        # ========== 注册中文字体 ==========
        font_registered = False
        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simsun.ttc',
            'C:/Windows/Fonts/simhei.ttf',
            '/System/Library/Fonts/PingFang.ttc',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    font_registered = True
                    print(f"✅ 找到中文字体: {font_path}")
                    break
                except Exception as e:
                    continue

        if not font_registered:
            print("⚠️ 未找到中文字体，PDF 中的中文可能显示为方块")

        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                leftMargin=1 * cm, rightMargin=1 * cm,
                                topMargin=1 * cm, bottomMargin=1 * cm)
        styles = getSampleStyleSheet()

        if font_registered:
            title_style = ParagraphStyle('Title', parent=styles['Title'],
                                         fontSize=20, alignment=1,
                                         fontName='ChineseFont')
            heading_style = ParagraphStyle('Heading2', parent=styles['Heading2'],
                                           fontSize=14, fontName='ChineseFont')
            normal_style = ParagraphStyle('Normal', parent=styles['Normal'],
                                          fontSize=10, fontName='ChineseFont')
            table_header_style = ParagraphStyle('TableHeader', parent=styles['Normal'],
                                                fontSize=11, fontName='ChineseFont',
                                                alignment=1, textColor=colors.whitesmoke)
            table_cell_style = ParagraphStyle('TableCell', parent=styles['Normal'],
                                              fontSize=10, fontName='ChineseFont',
                                              alignment=1)
        else:
            title_style = ParagraphStyle('Title', parent=styles['Title'],
                                         fontSize=20, alignment=1)
            heading_style = styles['Heading2']
            normal_style = styles['Normal']
            table_header_style = styles['Normal']
            table_cell_style = styles['Normal']

        story = []

        # 标题
        story.append(Paragraph("校友数据分析报告", title_style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Spacer(1, 0.3 * inch))

        # 基本统计
        stats = get_basic_stats(df)
        story.append(Paragraph("一、基本统计信息", heading_style))
        story.append(Spacer(1, 0.1 * inch))

        data = [['指标', '数值']]
        for k, v in stats.items():
            if isinstance(v, float) and v > 0:
                display_val = f"¥{v:.0f}" if '薪资' in k else f"{v:.1f}"
            else:
                display_val = str(v)
            data.append([k, display_val])

        table = Table(data, colWidths=[4 * cm, 4 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006994')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'ChineseFont' if font_registered else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'ChineseFont' if font_registered else 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3 * inch))

        # 性别比例
        gender_stats = get_gender_stats(df)
        story.append(Paragraph("二、性别比例（按学历）", heading_style))
        story.append(Spacer(1, 0.1 * inch))

        data = [['学历', '男', '女', '总人数', '男性占比%', '女性占比%']]
        for degree, row in gender_stats.iterrows():
            data.append([
                degree,
                str(int(row['男'])),
                str(int(row['女'])),
                str(int(row['总人数'])),
                f"{row['男性占比(%)']:.1f}",
                f"{row['女性占比(%)']:.1f}"
            ])

        table = Table(data, colWidths=[2.2 * cm, 1.5 * cm, 1.5 * cm, 2 * cm, 2.2 * cm, 2.2 * cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006994')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'ChineseFont' if font_registered else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'ChineseFont' if font_registered else 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3 * inch))

        # 行业分布
        industry_stats = get_industry_stats(df)
        if len(industry_stats) > 0:
            story.append(Paragraph("三、行业分布", heading_style))
            story.append(Spacer(1, 0.1 * inch))

            data = [['行业', '人数', '占比']]
            total = industry_stats.sum()
            for industry, count in industry_stats.items():
                pct = count / total * 100
                data.append([industry, str(count), f"{pct:.1f}%"])

            table = Table(data, colWidths=[4 * cm, 2 * cm, 2 * cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006994')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'ChineseFont' if font_registered else 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), 'ChineseFont' if font_registered else 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3 * inch))

        # 图表图片
        story.append(PageBreak())
        story.append(Paragraph("四、可视化图表", heading_style))
        story.append(Spacer(1, 0.2 * inch))

        chart_files = [
            ('gender_pie.png', '图1：性别比例饼图'),
            ('industry_bar.png', '图2：行业分布柱状图'),
            ('salary_bar.png', '图3：薪资对比柱状图'),
            ('salary_boxplot.png', '图4：薪资箱线图'),
            ('location_pie.png', '图5：所在地分布饼图')
        ]

        img_width = 16 * cm
        img_height = 10 * cm

        for i, (filename, caption) in enumerate(chart_files):
            img_path = f'output/{filename}'
            if os.path.exists(img_path):
                if i > 0 and i % 2 == 0:
                    story.append(PageBreak())

                story.append(Paragraph(caption, heading_style))
                try:
                    story.append(Image(img_path, width=img_width, height=img_height))
                except Exception as e:
                    story.append(Paragraph(f"⚠️ 图片 {filename} 无法加载", normal_style))
                story.append(Spacer(1, 0.15 * inch))

        doc.build(story)
        print(f"✅ PDF 报告已导出: {output_path}")
        return True

    except ImportError as e:
        print(f"⚠️ 请安装 reportlab: pip install reportlab")
        return False
    except PermissionError:
        # 如果文件被占用，生成带时间戳的文件名
        base, ext = os.path.splitext(output_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_path = f"{base}_{timestamp}{ext}"
        print(f"⚠️ 原文件被占用，使用新文件名: {new_path}")
        return export_pdf_report(df, new_path)
    except Exception as e:
        print(f"❌ 导出 PDF 失败: {e}")
        import traceback
        traceback.print_exc()
        return False