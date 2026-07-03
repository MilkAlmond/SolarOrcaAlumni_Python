# forum/models.py
# 论坛模块数据模型

from django.db import models


class Thread(models.Model):
    """帖子实体，对应 Threads 表"""
    thread_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()                 # 发帖用户 ID
    title = models.CharField(max_length=400)        # 帖子标题
    content = models.TextField()                    # 正文内容
    is_pinned = models.BooleanField(default=False)  # 是否置顶
    is_locked = models.BooleanField(default=False)  # 是否锁定
    is_alumni_only = models.BooleanField(default=False)  # 仅校友可见
    view_count = models.IntegerField(default=0)     # 浏览次数
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'Threads'
        managed = False

    def __str__(self):
        return self.title


class Reply(models.Model):
    """回复实体，对应 Replies 表"""
    reply_id = models.AutoField(primary_key=True)
    thread_id = models.IntegerField()               # 所属帖子 ID
    user_id = models.IntegerField()                 # 回复用户 ID
    content = models.TextField()                    # 回复内容
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Replies'
        managed = False

    def __str__(self):
        return f"Reply to thread {self.thread_id}"


class Report(models.Model):
    """举报实体，对应 Reports 表"""
    report_id = models.AutoField(primary_key=True)
    reporter_user_id = models.IntegerField()        # 举报人 ID
    thread_id = models.IntegerField(null=True, blank=True)   # 被举报帖子 ID
    reply_id = models.IntegerField(null=True, blank=True)    # 被举报回复 ID
    reason = models.CharField(max_length=200)       # 举报原因
    details = models.CharField(max_length=1000, null=True, blank=True)  # 详情
    status = models.CharField(max_length=20, default='pending')  # pending/resolved/dismissed
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Reports'
        managed = False

    def __str__(self):
        return f"Report {self.report_id} - {self.status}"