#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""统计模块 - 所有数据统计函数"""

import pandas as pd


def get_basic_stats(df):
    """获取基本统计信息"""
    alumni_df = df[df['角色'] == 'alumni']
    stats = {
        '总人数': len(df),
        '校友人数': len(alumni_df),
        '男性人数': len(df[df['性别'] == '男']),
        '女性人数': len(df[df['性别'] == '女']),
        '平均薪资': alumni_df[alumni_df['薪资'].notna()]['薪资'].mean() if len(alumni_df[alumni_df['薪资'].notna()]) > 0 else 0,
        '最高薪资': alumni_df[alumni_df['薪资'].notna()]['薪资'].max() if len(alumni_df[alumni_df['薪资'].notna()]) > 0 else 0,
        '最低薪资': alumni_df[alumni_df['薪资'].notna()]['薪资'].min() if len(alumni_df[alumni_df['薪资'].notna()]) > 0 else 0,
    }
    return stats


def get_gender_stats(df):
    """按学历统计性别比例"""
    result = df.groupby(['学历', '性别']).size().unstack(fill_value=0)
    result['总人数'] = result.sum(axis=1)
    result['男性占比(%)'] = (result['男'] / result['总人数'] * 100).round(1)
    result['女性占比(%)'] = (result['女'] / result['总人数'] * 100).round(1)
    return result


def get_industry_stats(df):
    """统计各行业校友分布"""
    alumni_df = df[df['角色'] == 'alumni']
    alumni_df = alumni_df[alumni_df['行业'] != '']
    result = alumni_df['行业'].value_counts()
    return result


def get_salary_stats(df):
    """按专业统计平均薪资（仅校友）"""
    alumni_df = df[df['角色'] == 'alumni']
    alumni_df = alumni_df[alumni_df['薪资'].notna()]
    if len(alumni_df) == 0:
        return pd.DataFrame()
    salary_by_major = alumni_df.groupby('专业')['薪资'].agg(['mean', 'count', 'min', 'max']).round(0)
    salary_by_major = salary_by_major[salary_by_major['count'] >= 3]
    salary_by_major = salary_by_major.sort_values('mean', ascending=False)
    salary_by_major.columns = ['平均薪资', '人数', '最低薪资', '最高薪资']
    return salary_by_major


def get_location_stats(df):
    """统计校友所在地分布"""
    alumni_df = df[df['角色'] == 'alumni']
    result = alumni_df['所在地'].value_counts()
    return result


def get_degree_stats(df):
    """统计各学历分布"""
    result = df['学历'].value_counts()
    return result


def get_year_trend_stats(df):
    """按毕业年份统计校友数量"""
    alumni_df = df[df['角色'] == 'alumni']
    result = alumni_df.groupby('毕业年份').size()
    return result


def get_data_quality_report(df):
    """生成数据质量报告（缺失值统计）"""
    report = {
        '总记录数': len(df),
        '重复记录数': df.duplicated().sum(),
        '字段缺失值': {}
    }
    for col in df.columns:
        missing = df[col].isnull().sum()
        pct = missing / len(df) * 100
        report['字段缺失值'][col] = {'缺失数': missing, '占比(%)': round(pct, 1)}
    return report


def filter_data(df, field, value):
    """按字段筛选数据"""
    if field not in df.columns:
        return df, f"❌ 字段 '{field}' 不存在"
    if value == '':
        return df, "⚠️ 请输入筛选值"
    filtered = df[df[field] == value]
    return filtered, f"✅ 筛选完成，剩余 {len(filtered)} 条记录"