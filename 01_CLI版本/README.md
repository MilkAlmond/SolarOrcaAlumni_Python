SolarOrca 校友数据分析系统 - CLI 版本

=====功能列表=====

  1. 📊 显示基本统计信息      - 总人数、校友人数、性别比例、薪资统计
  2. 📈 查看性别比例（按学历） - 各学历的男女比例
  3. 📊 查看行业分布          - 校友就业行业分布
  4. 💰 查看薪资统计（按专业） - 各专业校友平均薪资
  5. 📍 查看所在地分布        - 校友城市分布
  6. 🎓 查看学历分布          - 各学历人数分布
  7. 📋 数据质量报告          - 缺失值检测、重复记录统计
  8. 📈 毕业年份趋势          - 各年份校友数量趋势
  9. 📉 生成所有图表          - 生成 PNG 格式的统计图表
 10. 💾 导出统计结果 (CSV)    - 导出 CSV 格式统计报告
 11. 📁 导出 JSON 报告        - 导出 JSON 格式统计报告
 12. 📄 导出 PDF 报告         - 导出 PDF 格式完整报告
 13. 🔍 数据筛选              - 交互式数据筛选
 14. 📋 显示所有数据预览      - 查看前 10 条数据
 15. 🔄 重新加载数据          - 重新加载数据文件

=====运行方法=====

  cd 01_CLI版本
  pip install -r requirements_cli.txt
  python analysis_cli.py

命令行模式：

  python analysis_cli.py --stats
  python analysis_cli.py --charts
  python analysis_cli.py --pdf

=====输出文件=====

所有输出文件保存在 output/ 目录：

  stats_summary.csv      - CSV 统计结果
  stats_summary.json     - JSON 统计报告
  report.pdf             - PDF 完整报告
  gender_pie.png         - 性别比例饼图
  industry_bar.png       - 行业分布柱状图
  salary_bar.png         - 薪资对比柱状图
  salary_boxplot.png     - 薪资箱线图
  location_pie.png       - 所在地分布饼图

=====技术栈=====

  pandas                 - 数据处理
  matplotlib             - 数据可视化
  numpy                  - 数值计算
  reportlab              - PDF 报告生成