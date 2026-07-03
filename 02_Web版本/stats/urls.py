# stats/urls.py
# 统计分析模块 URL 路由

from django.urls import path
from . import views

urlpatterns = [
    # 统计分析主页
    path('', views.stats_view, name='stats'),

    # 通用数据 API（图表数据）
    path('api/', views.stats_api, name='stats_api'),

    # 预设问题 API
    path('api/preset/', views.stats_preset_api, name='stats_preset'),

    # 自定义分析 API
    path('api/custom/', views.stats_custom_api, name='stats_custom'),
]