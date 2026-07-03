# forum/urls.py
# 论坛模块 URL 路由

from django.urls import path
from . import views

urlpatterns = [
    # 帖子列表
    path('', views.thread_list_view, name='thread_list'),

    # 创建新帖子
    path('new/', views.new_thread_view, name='new_thread'),

    # 帖子详情
    path('thread/<int:thread_id>/', views.thread_detail_view, name='thread_detail'),

    # 添加回复
    path('thread/<int:thread_id>/reply/', views.reply_thread_view, name='reply_thread'),

    # 管理员：锁定/解锁
    path('thread/<int:thread_id>/lock/', views.lock_thread_view, name='lock_thread'),

    # 管理员：置顶/取消置顶
    path('thread/<int:thread_id>/pin/', views.pin_thread_view, name='pin_thread'),

    # 管理员：删除帖子
    path('thread/<int:thread_id>/delete/', views.delete_thread_view, name='delete_thread'),

    # 举报帖子（参数名改为 content_id，匹配视图函数）
    path('report/thread/<int:content_id>/', views.report_content_view, {'content_type': 'thread'}, name='report_thread'),

    # 举报回复（参数名改为 content_id，匹配视图函数）
    path('report/reply/<int:content_id>/', views.report_content_view, {'content_type': 'reply'}, name='report_reply'),
]