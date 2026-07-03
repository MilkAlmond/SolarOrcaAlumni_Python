# jobs/urls.py
# 职位搜索模块 URL 路由

from django.urls import path
from . import views

urlpatterns = [
    # 职位搜索主页（支持 search、page、pageSize 参数）
    path('', views.job_search_view, name='job_search'),
]