# users/models.py
# 用户模块数据模型

from django.db import models


class User(models.Model):
    """用户实体，对应 Users 表"""
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255, unique=True)      # 登录账号
    password_hash = models.CharField(max_length=255)           # 密码哈希
    full_name = models.CharField(max_length=200)               # 真实姓名
    student_id = models.CharField(max_length=20, unique=True)  # 学号
    role = models.CharField(max_length=20, null=True, blank=True)  # student/alumni/teacher/admin
    is_verified = models.BooleanField(default=False)           # 邮箱是否已验证
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    salary = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'Users'
        managed = False

    def __str__(self):
        return self.full_name

    def get_full_name(self):
        return self.full_name


class Degree(models.Model):
    """学位实体，对应 Degrees 表"""
    degree_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    degree_type = models.CharField(max_length=30, null=True, blank=True)  # Bachelor/Master/PhD
    major = models.CharField(max_length=200, null=True, blank=True)
    institution = models.CharField(max_length=400, null=True, blank=True)
    start_year = models.IntegerField(null=True, blank=True)
    end_year = models.IntegerField(null=True, blank=True)        # 空表示在读
    minor = models.CharField(max_length=200, null=True, blank=True)       # 辅修学位
    certificate = models.CharField(max_length=200, null=True, blank=True) # 辅修专业
    original_major = models.CharField(max_length=200, null=True, blank=True)  # 转专业前原专业
    transfer_year = models.IntegerField(null=True, blank=True)
    second_degree = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'Degrees'
        managed = False

    def __str__(self):
        return f"{self.degree_type} - {self.major}"


class VerificationToken(models.Model):
    """邮箱验证令牌，对应 VerificationTokens 表"""
    token_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255)
    code = models.CharField(max_length=6)          # 6位验证码
    expires_at = models.DateTimeField()            # 过期时间（10分钟后）
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'VerificationTokens'
        managed = False

    def __str__(self):
        return f"{self.email} - {self.code}"


class PasswordResetToken(models.Model):
    """密码重置令牌，对应 PasswordResetTokens 表"""
    reset_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    token = models.CharField(max_length=255)       # UUID 令牌
    expires_at = models.DateTimeField()            # 过期时间（1小时后）
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'PasswordResetTokens'
        managed = False

    def __str__(self):
        return f"Token for user {self.user_id}"