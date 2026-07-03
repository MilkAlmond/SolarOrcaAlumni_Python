# classes/models.py
# 班级模块数据模型

from django.db import models

class Class(models.Model):
    """班级实体，对应 Classes 表"""
    class_id = models.AutoField(primary_key=True)
    faculty = models.CharField(max_length=200)          # 学院
    major = models.CharField(max_length=200)            # 专业
    class_number = models.CharField(max_length=20)      # 班级编号
    graduation_year = models.IntegerField()             # 毕业年份

    class Meta:
        db_table = 'Classes'
        managed = False  # 使用现有数据库表，不自动迁移

    def __str__(self):
        return f"{self.faculty} - {self.major} ({self.graduation_year})"

class UserClass(models.Model):
    """用户-班级关联表"""
    user_id = models.IntegerField()
    class_id = models.IntegerField()

    class Meta:
        db_table = 'UserClasses'
        managed = False
        unique_together = (('user_id', 'class_id'),)