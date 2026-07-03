#!/usr/bin/env python
# utils/generate_demo_data.py
# 演示数据生成器（独立脚本）
# 使用方法：python utils/generate_demo_data.py

import os
import sys
import random

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solarorca.settings')
import django
django.setup()

from django.db import connection


# 姓名库
FIRST_NAMES = [
    'Wei', 'Ming', 'Jian', 'Qiang', 'Tao', 'Jun', 'Feng', 'Yong', 'Bin', 'Hao',
    'Li', 'Fang', 'Min', 'Yan', 'Jing', 'Yue', 'Lin', 'Na', 'Xin', 'Wei'
]
LAST_NAMES = ['Zhang', 'Li', 'Wang', 'Liu', 'Chen', 'Yang', 'Zhao', 'Zhou', 'Wu', 'Xu']

# 学术数据
MAJORS = [
    'Computer Science', 'Software Engineering', 'Economics', 'Finance',
    'Business Administration', 'Physics', 'Mathematics', 'English Literature',
    'Law', 'Mechanical Engineering'
]
UNIVERSITIES = ['Central South University', 'Wuhan University', 'Fudan University']

# 用户角色（权重）
ROLES = ['alumni', 'student', 'teacher', 'admin']
ROLE_WEIGHTS = [80, 15, 3, 2]

# 工作数据
INDUSTRIES = ['Technology', 'Finance', 'Education', 'Healthcare', 'Manufacturing', 'Other']
COMPANIES = ['Tencent', 'Alibaba', 'ByteDance', 'Huawei', 'Baidu', 'Meituan', 'JD.com', 'NetEase']
LOCATIONS = ['Beijing', 'Shanghai', 'Shenzhen', 'Guangzhou', 'Hangzhou', 'Chengdu', 'Other']

JOB_TITLES_BY_INDUSTRY = {
    'Technology': ['Software Engineer', 'Data Scientist', 'DevOps Engineer', 'Frontend Developer', 'Backend Developer', 'QA Engineer'],
    'Finance': ['Financial Analyst', 'Investment Banker', 'Accountant', 'Risk Manager', 'Auditor'],
    'Education': ['Teacher', 'Professor', 'Researcher', 'Administrator', 'Lecturer'],
    'Healthcare': ['Doctor', 'Nurse', 'Pharmacist', 'Researcher', 'Lab Technician'],
    'Manufacturing': ['Production Engineer', 'Quality Control', 'Supply Chain Manager', 'Plant Manager'],
    'Other': ['Consultant', 'Manager', 'Analyst', 'Coordinator', 'Specialist']
}

# 常量
TARGET_USER_COUNT = 500
CURRENT_YEAR = 2026
PASSWORD = 'demo123'


def get_weighted_role():
    """根据权重随机获取角色"""
    total = sum(ROLE_WEIGHTS)
    rand = random.randint(1, total)
    cumulative = 0
    for i, weight in enumerate(ROLE_WEIGHTS):
        cumulative += weight
        if rand <= cumulative:
            return ROLES[i]
    return 'alumni'


def get_weighted_university():
    """根据权重随机获取大学（中南大学 90%）"""
    rand = random.randint(1, 100)
    if rand <= 90:
        return UNIVERSITIES[0]
    elif rand <= 95:
        return UNIVERSITIES[1]
    else:
        return UNIVERSITIES[2]


def generate_email_domain():
    """生成随机邮箱域名"""
    domains = ['@gmail.com', '@outlook.com', '@163.com', '@qq.com', '@csu.edu.cn']
    return random.choice(domains)


def insert_user(sequence):
    """插入单个用户及其关联数据（学位、工作经历）"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    full_name = f'{first_name} {last_name}'

    email = f'demo{sequence}{generate_email_domain()}'
    student_id = f'SID{sequence:06d}'

    role = get_weighted_role()
    grad_year = random.randint(2000, 2026)
    birth_year = grad_year - 22
    age = CURRENT_YEAR - birth_year
    location = random.choice(LOCATIONS)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO Users (email, password_hash, full_name, student_id, role, location, is_verified, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, GETDATE())
            """,
            [email, PASSWORD, full_name, student_id, role, location]
        )
        cursor.execute("SELECT @@IDENTITY")
        user_id = cursor.fetchone()[0]

    major = random.choice(MAJORS)
    university = get_weighted_university()

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO Degrees (user_id, degree_type, major, institution, start_year, end_year)
            VALUES (?, 'Bachelor', ?, ?, ?, ?)
            """,
            [user_id, major, university, grad_year - 4, grad_year]
        )

        if random.randint(1, 100) <= 40 and role == 'alumni':
            cursor.execute(
                """
                INSERT INTO Degrees (user_id, degree_type, major, institution, start_year, end_year)
                VALUES (?, 'Master', ?, ?, ?, ?)
                """,
                [user_id, major, university, grad_year, grad_year + 2]
            )

        if random.randint(1, 100) <= 10 and role == 'alumni':
            phd_start = grad_year + random.choice([0, 2])
            cursor.execute(
                """
                INSERT INTO Degrees (user_id, degree_type, major, institution, start_year, end_year)
                VALUES (?, 'PhD', ?, ?, ?, ?)
                """,
                [user_id, major, university, phd_start, phd_start + 4]
            )

    if role == 'alumni' and age > 22 and random.randint(1, 100) <= 70:
        with connection.cursor() as cursor:
            industry_idx = random.randint(0, len(INDUSTRIES) - 1)
            industry = INDUSTRIES[industry_idx]
            job_title = random.choice(JOB_TITLES_BY_INDUSTRY[industry])
            company = random.choice(COMPANIES)
            work_start_year = grad_year + random.randint(0, 2)
            is_current = random.randint(1, 100) <= 30

            if is_current:
                cursor.execute(
                    """
                    INSERT INTO WorkExperience (user_id, job_title, employer, industry, start_year, end_year, is_current)
                    VALUES (?, ?, ?, ?, ?, NULL, ?)
                    """,
                    [user_id, job_title, company, industry, work_start_year, is_current]
                )
            else:
                work_end_year = grad_year + random.randint(0, age - 22)
                cursor.execute(
                    """
                    INSERT INTO WorkExperience (user_id, job_title, employer, industry, start_year, end_year, is_current)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [user_id, job_title, company, industry, work_start_year, work_end_year, is_current]
                )


def generate_demo_data():
    """生成演示数据的主方法"""
    print('Starting demo data generation...')

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM Users")
        current_count = cursor.fetchone()[0]

    if current_count >= TARGET_USER_COUNT:
        print(f'Already have {current_count} users. Skipping generation.')
        return

    needed = TARGET_USER_COUNT - current_count
    print(f'Generating {needed} demo records...')

    for i in range(1, needed + 1):
        insert_user(current_count + i)
        if (current_count + i) % 50 == 0:
            print(f'Generated {current_count + i} records...')

    print(f'Successfully generated {needed} demo records!')
    print(f'Total users now: {TARGET_USER_COUNT}')


if __name__ == '__main__':
    generate_demo_data()