# admin_panel/views.py
# 管理后台视图

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.db.models import Q
from django.db import DatabaseError

from users.models import User
from forum.models import Report
from utils.levenshtein import get_similarity


def admin_required(view_func):
    """检查当前用户是否为管理员"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_logged_in', False):
            return redirect('/login/')
        if request.session.get('user_role', '') != 'admin':
            messages.error(request, 'You do not have admin privileges.')
            return redirect('/home/')
        return view_func(request, *args, **kwargs)
    return wrapper


# -------------------- 用户管理 --------------------

@admin_required
def user_management_view(request):
    """
    用户管理主页 - 列表、搜索、分页
    URL: /admin-panel/users/
    """
    search = request.GET.get('search', '').strip()
    mode = request.GET.get('mode', 'exact')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('pageSize', 10))

    if search:
        if mode == 'fuzzy':
            # 模糊搜索：Levenshtein 相似度（阈值 20%）
            all_users = User.objects.all()
            ranked = []
            for user in all_users:
                id_score = get_similarity(search, str(user.user_id))
                name_score = get_similarity(search, user.full_name)
                email_score = get_similarity(search, user.email)
                student_id_score = get_similarity(search, user.student_id)
                max_score = max(id_score, name_score, email_score, student_id_score)
                if max_score > 20:
                    ranked.append({'user': user, 'score': max_score})
            ranked.sort(key=lambda x: x['score'], reverse=True)
            total_results = len(ranked)
            start = (page - 1) * page_size
            end = start + page_size
            users = [item['user'] for item in ranked[start:end]]
        else:
            # 精确搜索：SQL LIKE
            users = User.objects.filter(
                Q(full_name__icontains=search) |
                Q(email__icontains=search) |
                Q(student_id__icontains=search)
            ).order_by('user_id')
            total_results = users.count()
            start = (page - 1) * page_size
            end = start + page_size
            users = users[start:end]
    else:
        # 获取全部用户（分页）
        users = User.objects.all().order_by('user_id')
        total_results = users.count()
        start = (page - 1) * page_size
        end = start + page_size
        users = users[start:end]

    total_pages = (total_results + page_size - 1) // page_size if total_results > 0 else 1

    context = {
        'users': users,
        'search': search,
        'mode': mode,
        'current_page': page,
        'total_pages': total_pages,
        'total_results': total_results,
        'page_size': page_size,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
        'user_id': request.session.get('user_id'),
    }
    return render(request, 'admin_panel/users.html', context)


@admin_required
def update_user_role(request):
    """更新用户角色（不能修改自己的角色）"""
    if request.method != 'POST':
        return redirect('/admin-panel/users/')

    user_id = request.POST.get('user_id')
    role = request.POST.get('role')

    if not user_id or not role:
        messages.error(request, 'Missing parameters.')
        return redirect('/admin-panel/users/')

    if int(user_id) == request.session.get('user_id'):
        messages.error(request, 'You cannot change your own role.')
        return redirect('/admin-panel/users/')

    try:
        user = User.objects.get(user_id=user_id)
        user.role = role
        user.save()
        messages.success(request, f'User {user.full_name}\'s role has been updated to {role}.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')

    return redirect('/admin-panel/users/')


@admin_required
def delete_user(request, user_id):
    """删除用户及所有关联数据（级联删除）"""
    if user_id == request.session.get('user_id'):
        messages.error(request, 'You cannot delete your own account.')
        return redirect('/admin-panel/users/')

    try:
        user = User.objects.get(user_id=user_id)
        user_name = user.full_name

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Reports WHERE reporter_user_id = %s", [user_id])
            cursor.execute("DELETE FROM UserNotifications WHERE user_id = %s", [user_id])
            cursor.execute("DELETE FROM Replies WHERE user_id = %s", [user_id])
            cursor.execute("DELETE FROM Threads WHERE user_id = %s", [user_id])
            cursor.execute("DELETE FROM ResearchPositions WHERE user_id = %s", [user_id])
            cursor.execute("DELETE FROM WorkExperience WHERE user_id = %s", [user_id])
            cursor.execute("DELETE FROM Degrees WHERE user_id = %s", [user_id])
            cursor.execute("DELETE FROM UserClasses WHERE user_id = %s", [user_id])
            cursor.execute("DELETE FROM Users WHERE user_id = %s", [user_id])

        messages.success(request, f'User {user_name} has been deleted successfully.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')

    return redirect('/admin-panel/users/')


@admin_required
def edit_user_view(request, user_id):
    """
    编辑用户信息
    URL: /admin-panel/users/edit/<user_id>/
    """
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('/admin-panel/users/')

    # 获取当前班级
    with connection.cursor() as cursor:
        cursor.execute("SELECT class_id FROM UserClasses WHERE user_id = %s", [user_id])
        row = cursor.fetchone()
        current_class_id = row[0] if row else None

    # 获取所有班级列表（用于下拉菜单）
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT class_id, faculty, major, class_number, graduation_year
            FROM Classes
            ORDER BY graduation_year DESC, faculty, major
        """)
        all_classes = cursor.fetchall()

    classes = []
    for row in all_classes:
        classes.append({
            'class_id': row[0],
            'faculty': row[1],
            'major': row[2],
            'class_number': row[3],
            'graduation_year': row[4],
        })

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        location = request.POST.get('location')
        role = request.POST.get('role')
        class_id = request.POST.get('class_id')

        user.full_name = full_name
        user.email = email
        user.location = location
        user.role = role
        user.save()

        # 更新班级分配
        if class_id:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM UserClasses WHERE user_id = %s", [user_id])
                cursor.execute("INSERT INTO UserClasses (user_id, class_id) VALUES (%s, %s)", [user_id, class_id])
        else:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM UserClasses WHERE user_id = %s", [user_id])

        messages.success(request, f'User {user.full_name} has been updated successfully.')
        return redirect('/admin-panel/users/')

    context = {
        'edit_user': user,
        'current_class_id': current_class_id,
        'classes': classes,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
        'user_id': request.session.get('user_id'),
    }
    return render(request, 'admin_panel/edit_user.html', context)


# -------------------- 举报管理 --------------------

@admin_required
def report_management_view(request):
    """举报管理主页"""
    reports = Report.objects.all().order_by('-created_at')

    for report in reports:
        # 举报人姓名
        try:
            reporter = User.objects.get(user_id=report.reporter_user_id)
            report.reporter_name = reporter.full_name
        except User.DoesNotExist:
            report.reporter_name = 'Unknown'

        # 被举报内容描述
        if report.thread_id:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT title FROM Threads WHERE thread_id = %s", [report.thread_id])
                    row = cursor.fetchone()
                    report.content_desc = f'Thread: {row[0] if row else "Deleted"}'
            except DatabaseError:
                report.content_desc = 'Thread (Deleted)'
        elif report.reply_id:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT content FROM Replies WHERE reply_id = %s", [report.reply_id])
                    row = cursor.fetchone()
                    content = row[0][:50] + '...' if row and len(row[0]) > 50 else row[0] if row else 'Deleted'
                    report.content_desc = f'Reply: {content}'
            except DatabaseError:
                report.content_desc = 'Reply (Deleted)'
        else:
            report.content_desc = 'Unknown Content'

    context = {
        'reports': reports,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'admin_panel/reports.html', context)


@admin_required
def update_report_status(request, report_id):
    """
    更新举报状态
    status: pending / resolved / dismissed
    """
    if request.method != 'POST':
        return redirect('/admin-panel/reports/')

    status = request.POST.get('status')

    if status not in ['pending', 'resolved', 'dismissed']:
        messages.error(request, 'Invalid status.')
        return redirect('/admin-panel/reports/')

    try:
        report = Report.objects.get(report_id=report_id)
        report.status = status
        report.save()
        messages.success(request, f'Report status updated to: {status}')
    except Report.DoesNotExist:
        messages.error(request, 'Report not found.')

    return redirect('/admin-panel/reports/')


@admin_required
def delete_report(request, report_id):
    """删除举报记录"""
    try:
        report = Report.objects.get(report_id=report_id)
        report.delete()
        messages.success(request, 'Report deleted successfully.')
    except Report.DoesNotExist:
        messages.error(request, 'Report not found.')

    return redirect('/admin-panel/reports/')