SolarOrca 校友数据分析系统 - Python 期末大作业

=====项目概述=====

本项目是一个校友数据分析与管理系统，包含两个版本：

  - CLI 版本：命令行数据分析工具（核心评分部分）
  - Web 版本：Django 校友管理系统（加分展示）

=====项目结构=====

班级_学号_姓名_Python期末大作业/
│
├── 01_CLI版本/
│   ├── analysis_cli.py           # 主程序（所有代码集中在此）
│   ├── data/
│   │   └── alumni_data.csv       # 数据文件（自动生成）
│   ├── output/                   # 运行后自动生成
│   │   ├── stats_summary.csv
│   │   ├── gender_pie.png
│   │   ├── industry_bar.png
│   │   ├── salary_bar.png
│   │   └── location_pie.png
│   ├── requirements_cli.txt      # 依赖列表
│   └── README.md                 # CLI 版本说明
│
├── 02_Web版本/
│   ├── manage.py
│   ├── solarorca/                # Django 项目配置
│   ├── users/                    # 用户管理模块
│   ├── forum/                    # 论坛模块
│   ├── classes/                  # 班级模块
│   ├── jobs/                     # 职位搜索模块
│   ├── stats/                    # 统计分析模块
│   ├── admin_panel/              # 管理后台模块
│   ├── templates/                # HTML 模板
│   ├── static/                   # 静态文件
│   ├── utils/                    # 工具函数
│   ├── requirements_web.txt      # 依赖列表
│   └── 运行说明.txt
│
└── 项目报告.docx                 # 项目说明报告（含运行截图）

=====运行方法=====

CLI 版本
----------

  cd 01_CLI版本
  pip install -r requirements_cli.txt
  python analysis_cli.py

Web 版本
----------

  cd 02_Web版本
  pip install -r requirements_web.txt
  python manage.py runserver 8081

  访问 http://127.0.0.1:8081

=====CLI 版本功能列表=====

  编号  功能              说明
  ----  ----------------  --------------------------------------------
  1     基本统计信息       总人数、校友人数、性别比例、薪资统计
  2     性别比例（按学历） 各学历的男女比例
  3     行业分布           校友就业行业分布
  4     薪资统计（按专业） 各专业校友平均薪资
  5     所在地分布         校友城市分布
  6     生成所有图表       生成 PNG 格式的统计图表
  7     导出统计结果       导出 CSV 格式的统计报告
  8     数据预览           查看前 10 条数据
  9     重新加载数据       重新加载数据文件

=====Web 版本功能列表=====

  功能              说明
  ----------------  --------------------------------------------
  用户登录/注册     Session 认证
  个人资料管理      编辑个人资料、学历、工作经历
  论坛系统          发帖、回复、置顶、锁定
  班级管理          查看班级列表、班级详情
  职位搜索          模糊搜索校友职位
  统计分析          性别比例、行业分布、薪资统计
  管理后台          用户管理、举报管理

=====技术栈=====

CLI 版本
----------

  pandas 2.2.2     数据处理
  matplotlib 3.9.0 数据可视化
  numpy 1.26.4     数值计算

Web 版本
----------

  Django 5.0.6                 Web 框架
  mssql-django 1.3.1           SQL Server 驱动
  pyodbc 5.1.0                 ODBC 连接
  Chart.js                     前端图表

=====作者信息=====

  姓名：黄心朗
  班级：信管2501
  学号：1602250130
  课程：Python 程序设计基础
  日期：2026年7月

=====项目报告=====

详细说明请查看 项目报告.docx，包含：

  - 项目背景与目标
  - 功能设计
  - 数据说明
  - 程序设计思路
  - 运行结果展示（含截图）
  - 总结与反思