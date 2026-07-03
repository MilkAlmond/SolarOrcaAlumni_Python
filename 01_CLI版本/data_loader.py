#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""数据加载模块 - 负责读取CSV文件和生成示例数据"""

import os
import random
import pandas as pd


def load_data(file_path='data/alumni_data.csv'):
    """
    加载校友数据
    如果文件不存在或为空，生成示例数据
    """
    if os.path.exists(file_path):
        try:
            print(f"📂 正在加载数据文件: {file_path}")
            df = pd.read_csv(file_path, encoding='utf-8')
            if len(df) == 0:
                print("⚠️ 数据文件为空，正在生成示例数据...")
                df = generate_sample_data()
                return df
            print(f"✅ 成功加载 {len(df)} 条记录")
            return df
        except pd.errors.EmptyDataError:
            print("⚠️ 数据文件为空，正在生成示例数据...")
            df = generate_sample_data()
            return df
        except Exception as e:
            print(f"❌ 读取文件出错: {e}")
            print("📝 正在生成示例数据...")
            df = generate_sample_data()
            return df
    else:
        print(f"⚠️ 数据文件不存在: {file_path}")
        print("📝 正在生成示例数据...")
        df = generate_sample_data()
        return df


def generate_sample_data():
    """生成示例数据（用于演示）"""
    first_names = ['伟', '明', '建', '强', '涛', '军', '峰', '勇', '斌', '浩',
                   '丽', '芳', '敏', '燕', '静', '悦', '琳', '娜', '欣', '薇']
    last_names = ['张', '李', '王', '刘', '陈', '杨', '赵', '周', '吴', '徐']

    data = []
    genders = ['M', 'F']
    roles = ['alumni', 'alumni', 'alumni', 'alumni', 'alumni', 'student', 'teacher', 'admin']
    degrees = ['Bachelor', 'Bachelor', 'Bachelor', 'Bachelor', 'Master', 'Master', 'PhD']
    majors = ['计算机科学', '软件工程', '经济学', '金融学', '工商管理', '物理学', '数学', '英语', '法学', '机械工程']
    industries = ['科技', '金融', '教育', '医疗', '制造业', '其他']
    locations = ['北京', '上海', '深圳', '广州', '杭州', '成都', '海外', '其他']

    for i in range(500):
        name = random.choice(last_names) + random.choice(first_names)
        gender = '男' if random.choice(genders) == 'M' else '女'
        role = random.choice(roles)
        degree = random.choice(degrees)
        major = random.choice(majors)
        industry = random.choice(industries) if role == 'alumni' and random.random() > 0.2 else ''
        location = random.choice(locations)
        salary = random.randint(8000, 50000) if role == 'alumni' and random.random() > 0.3 else None
        grad_year = random.randint(2000, 2026)

        data.append({
            'user_id': i + 1,
            '姓名': name,
            '性别': gender,
            '角色': role,
            '学历': degree,
            '专业': major,
            '行业': industry,
            '所在地': location,
            '薪资': salary,
            '毕业年份': grad_year
        })

    df = pd.DataFrame(data)
    print(f"✅ 已生成 {len(df)} 条示例数据")

    os.makedirs('data', exist_ok=True)
    df.to_csv('data/alumni_data.csv', index=False, encoding='utf-8')
    print("💾 示例数据已保存到 data/alumni_data.csv")

    return df