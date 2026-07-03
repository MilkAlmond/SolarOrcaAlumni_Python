# admin_panel/urls.py
# 管理后台 URL 路由

from django.urls import path
from . import views

urlpatterns = [
    # 用户管理
    path('users/', views.user_management_view, name='admin_users'),
    path('users/update-role/', views.update_user_role, name='update_user_role'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('users/edit/<int:user_id>/', views.edit_user_view, name='edit_user'),

    # 举报管理
    path('reports/', views.report_management_view, name='admin_reports'),
    path('reports/update/<int:report_id>/', views.update_report_status, name='update_report'),
    path('reports/delete/<int:report_id>/', views.delete_report, name='delete_report'),
]