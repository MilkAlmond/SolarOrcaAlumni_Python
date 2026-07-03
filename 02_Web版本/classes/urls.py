# classes/urls.py
# 班级模块 URL 路由

from django.urls import path
from . import views

urlpatterns = [
    # 班级列表
    path('', views.class_list_view, name='class_list'),

    # 班级详情
    path('detail/<int:class_id>/', views.class_detail_view, name='class_detail'),

    # 管理员：添加班级
    path('add/', views.add_class_view, name='add_class'),

    # 管理员：编辑班级
    path('edit/<int:class_id>/', views.edit_class_view, name='edit_class'),

    # 管理员：删除班级
    path('delete/<int:class_id>/', views.delete_class_view, name='delete_class'),

    # 管理员：移动学生
    path('move/', views.move_student_view, name='move_student'),

    # 管理员：移除学生
    path('remove/', views.remove_student_view, name='remove_student'),
]