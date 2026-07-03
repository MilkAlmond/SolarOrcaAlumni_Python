from django.urls import path
from . import views

urlpatterns = [
    # 登录/登出/首页
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),

    # 注册（三步流程）
    path('register/', views.register_view, name='register'),
    path('register/step1/', views.register_step1_post, name='register_step1'),
    path('register/step2/', views.register_step2_post, name='register_step2'),
    path('register/step3/', views.register_step3_post, name='register_step3'),

    # 个人资料
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.profile_view, name='profile_detail'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # 修改密码
    path('change-password/', views.change_password_view, name='change_password'),

    # 忘记密码 / 重置密码
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/', views.reset_password_view, name='reset_password'),

    # 学位 CRUD
    path('degree/add/', views.add_degree_view, name='add_degree'),
    path('degree/edit/<int:degree_id>/', views.edit_degree_view, name='edit_degree'),
    path('degree/delete/<int:degree_id>/', views.delete_degree_view, name='delete_degree'),

    # 工作经历 CRUD
    path('work/add/', views.add_work_view, name='add_work'),
    path('work/edit/<int:work_id>/', views.edit_work_view, name='edit_work'),
    path('work/delete/<int:work_id>/', views.delete_work_view, name='delete_work'),

    # 科研经历 CRUD
    path('research/add/', views.add_research_view, name='add_research'),
    path('research/edit/<int:position_id>/', views.edit_research_view, name='edit_research'),
    path('research/delete/<int:position_id>/', views.delete_research_view, name='delete_research'),

    # 自定义主题
    path('custom-theme/', views.custom_theme_view, name='custom_theme'),
]