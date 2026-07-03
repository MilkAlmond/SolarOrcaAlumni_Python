# solarorca/urls.py
# 项目主路由配置

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, render
from django.views.generic import RedirectView


def faq_view(request):
    """FAQ 页面"""
    context = {}
    # 如果用户已登录，传递用户信息用于导航
    if request.session.get('is_logged_in', False):
        context['user_name'] = request.session.get('user_name', '')
        context['user_role'] = request.session.get('user_role', '')
    return render(request, 'faq.html', context)


def settings_view(request):
    """设置页面（主题切换、语言切换、修改密码）"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')
    context = {
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'users/settings.html', context)


urlpatterns = [
    # Django 自带管理后台
    path('admin/', admin.site.urls),

    # 首页重定向到登录页
    path('', lambda request: redirect('/login/')),

    # 用户模块
    path('', include('users.urls')),

    # 班级模块
    path('classes/', include('classes.urls')),

    # 论坛模块
    path('forum/', include('forum.urls')),

    # 职位搜索模块
    path('jobs/', include('jobs.urls')),

    # 统计分析模块
    path('stats/', include('stats.urls')),

    # 管理后台
    path('admin-panel/', include('admin_panel.urls')),

    # 设置页面
    path('settings/', settings_view, name='settings'),

    # 重定向（兼容旧链接）
    path('edit-profile/', RedirectView.as_view(url='/profile/edit/', permanent=False), name='edit_profile_redirect'),

    # FAQ 页面（公开页面，未登录也可访问）
    path('faq/', faq_view, name='faq'),
]