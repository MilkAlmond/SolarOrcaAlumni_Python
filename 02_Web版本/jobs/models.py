# jobs/models.py
# 职位搜索模块数据模型

from django.db import models


class WorkExperience(models.Model):
    """工作经历实体，对应 WorkExperience 表"""
    work_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()                 # 所属用户 ID
    job_title = models.CharField(max_length=200)    # 职位名称
    employer = models.CharField(max_length=200)     # 雇主名称
    start_year = models.IntegerField()              # 开始年份
    end_year = models.IntegerField(null=True, blank=True)   # 结束年份（空表示至今）
    is_current = models.BooleanField(default=False) # 是否为当前工作
    industry = models.CharField(max_length=100, null=True, blank=True)  # 所属行业

    class Meta:
        db_table = 'WorkExperience'
        managed = False

    def __str__(self):
        return f"{self.job_title} at {self.employer}"


class ResearchPosition(models.Model):
    """科研经历实体，对应 ResearchPositions 表"""
    position_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()                 # 所属用户 ID
    position_type = models.CharField(max_length=50) # 岗位类型
    institution = models.CharField(max_length=400)  # 机构名称
    department = models.CharField(max_length=200, null=True, blank=True)  # 院系
    start_year = models.IntegerField()              # 开始年份
    end_year = models.IntegerField(null=True, blank=True)   # 结束年份（空表示至今）
    is_current = models.BooleanField(default=False) # 是否为当前岗位

    class Meta:
        db_table = 'ResearchPositions'
        managed = False