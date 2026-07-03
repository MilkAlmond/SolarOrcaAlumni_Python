# classes/views.py
# 班级模块视图

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.db.models import Q

from .models import Class, UserClass
from users.models import User
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


# -------------------- 班级列表 --------------------

def class_list_view(request):
    """
    班级列表页（支持搜索和分页）
    URL: /classes/
    """
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    search = request.GET.get('search', '').strip()
    mode = request.GET.get('mode', 'exact')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('pageSize', 10))

    classes = []
    total_results = 0

    if search:
        if mode == 'fuzzy':
            # 模糊搜索：Levenshtein 相似度（阈值 20%）
            all_classes = Class.objects.all()
            ranked = []
            for c in all_classes:
                faculty_score = get_similarity(search, c.faculty)
                major_score = get_similarity(search, c.major)
                class_number_score = get_similarity(search, c.class_number)
                max_score = max(faculty_score, major_score, class_number_score)
                if max_score > 20:
                    ranked.append({'class': c, 'score': max_score})
            ranked.sort(key=lambda x: x['score'], reverse=True)
            total_results = len(ranked)
            start = (page - 1) * page_size
            end = start + page_size
            classes = [item['class'] for item in ranked[start:end]]
        else:
            # 精确搜索：SQL LIKE
            classes = Class.objects.filter(
                Q(faculty__icontains=search) |
                Q(major__icontains=search) |
                Q(class_number__icontains=search)
            ).order_by('-graduation_year', 'faculty', 'major', 'class_number')
            total_results = classes.count()
            start = (page - 1) * page_size
            end = start + page_size
            classes = classes[start:end]
    else:
        classes = Class.objects.all().order_by('-graduation_year', 'faculty', 'major', 'class_number')
        total_results = classes.count()
        start = (page - 1) * page_size
        end = start + page_size
        classes = classes[start:end]

    total_pages = (total_results + page_size - 1) // page_size if total_results > 0 else 1

    context = {
        'classes': classes,
        'search': search,
        'mode': mode,
        'current_page': page,
        'total_pages': total_pages,
        'total_results': total_results,
        'page_size': page_size,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'classes/list.html', context)


# -------------------- 班级详情 --------------------

def class_detail_view(request, class_id):
    """
    班级详情页（显示班级信息 + 学生列表）
    URL: /classes/detail/<class_id>/
    """
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    try:
        class_obj = Class.objects.get(class_id=class_id)
    except Class.DoesNotExist:
        messages.error(request, 'Class not found.')
        return redirect('/classes/')

    user_ids = UserClass.objects.filter(class_id=class_id).values_list('user_id', flat=True)
    students = User.objects.filter(user_id__in=user_ids)

    context = {
        'class_obj': class_obj,
        'students': students,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'classes/detail.html', context)


# -------------------- 添加班级（管理员） --------------------

@admin_required
def add_class_view(request):
    """
    添加班级（管理员功能）
    URL: /classes/add/
    """
    if request.method == 'POST':
        faculty = request.POST.get('faculty', '').strip()
        major = request.POST.get('major', '').strip()
        class_number = request.POST.get('class_number', '').strip()
        graduation_year = request.POST.get('graduation_year', '').strip()

        if not all([faculty, major, class_number, graduation_year]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'classes/form.html', {'is_edit': False})

        try:
            graduation_year = int(graduation_year)
        except ValueError:
            messages.error(request, 'Invalid graduation year.')
            return render(request, 'classes/form.html', {'is_edit': False})

        Class.objects.create(
            faculty=faculty,
            major=major,
            class_number=class_number,
            graduation_year=graduation_year
        )

        messages.success(request, 'Class added successfully!')
        return redirect('/classes/')

    context = {
        'is_edit': False,
        'class_obj': None,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'classes/form.html', context)


# -------------------- 编辑班级（管理员） --------------------

@admin_required
def edit_class_view(request, class_id):
    """
    编辑班级（管理员功能）
    URL: /classes/edit/<class_id>/
    """
    try:
        class_obj = Class.objects.get(class_id=class_id)
    except Class.DoesNotExist:
        messages.error(request, 'Class not found.')
        return redirect('/classes/')

    if request.method == 'POST':
        faculty = request.POST.get('faculty', '').strip()
        major = request.POST.get('major', '').strip()
        class_number = request.POST.get('class_number', '').strip()
        graduation_year = request.POST.get('graduation_year', '').strip()

        if not all([faculty, major, class_number, graduation_year]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'classes/form.html', {'is_edit': True, 'class_obj': class_obj})

        try:
            graduation_year = int(graduation_year)
        except ValueError:
            messages.error(request, 'Invalid graduation year.')
            return render(request, 'classes/form.html', {'is_edit': True, 'class_obj': class_obj})

        class_obj.faculty = faculty
        class_obj.major = major
        class_obj.class_number = class_number
        class_obj.graduation_year = graduation_year
        class_obj.save()

        messages.success(request, 'Class updated successfully!')
        return redirect('/classes/')

    context = {
        'is_edit': True,
        'class_obj': class_obj,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'classes/form.html', context)


# -------------------- 删除班级（管理员） --------------------

@admin_required
def delete_class_view(request, class_id):
    """
    删除班级（管理员功能）
    URL: /classes/delete/<class_id>/
    先删除所有学生-班级关联，再删除班级本身
    """
    try:
        class_obj = Class.objects.get(class_id=class_id)
        class_name = f"{class_obj.faculty} - {class_obj.class_number}"

        UserClass.objects.filter(class_id=class_id).delete()
        class_obj.delete()

        messages.success(request, f'Class "{class_name}" has been deleted.')
    except Class.DoesNotExist:
        messages.error(request, 'Class not found.')

    return redirect('/classes/')


# -------------------- 移动学生（管理员） --------------------

@admin_required
def move_student_view(request):
    """
    移动学生到另一个班级（管理员功能）
    URL: /classes/move/
    """
    if request.method == 'POST':
        student_id = request.POST.get('student_id', '').strip()
        from_class_id = request.POST.get('from_class_id', '').strip()
        to_class_id = request.POST.get('to_class_id', '').strip()

        if not all([student_id, from_class_id, to_class_id]):
            messages.error(request, 'Missing required parameters.')
            return redirect('/classes/')

        try:
            student_id = int(student_id)
            from_class_id = int(from_class_id)
            to_class_id = int(to_class_id)
        except ValueError:
            messages.error(request, 'Invalid parameters.')
            return redirect('/classes/')

        if from_class_id == to_class_id:
            messages.error(request, 'Student is already in the target class.')
            return redirect(f'/classes/detail/{from_class_id}/')

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM UserClasses WHERE user_id = %s AND class_id = %s", [student_id, from_class_id])
            cursor.execute("INSERT INTO UserClasses (user_id, class_id) VALUES (%s, %s)", [student_id, to_class_id])

        messages.success(request, 'Student moved successfully!')
        return redirect(f'/classes/detail/{from_class_id}/')

    # GET 请求：显示移动表单
    student_id = request.GET.get('student_id', '').strip()
    from_class_id = request.GET.get('from_class_id', '').strip()

    if not student_id or not from_class_id:
        messages.error(request, 'Missing required parameters.')
        return redirect('/classes/')

    try:
        student_id = int(student_id)
        from_class_id = int(from_class_id)
    except ValueError:
        messages.error(request, 'Invalid parameters.')
        return redirect('/classes/')

    try:
        student = User.objects.get(user_id=student_id)
    except User.DoesNotExist:
        messages.error(request, 'Student not found.')
        return redirect('/classes/')

    try:
        from_class = Class.objects.get(class_id=from_class_id)
    except Class.DoesNotExist:
        messages.error(request, 'Source class not found.')
        return redirect('/classes/')

    all_classes = Class.objects.exclude(class_id=from_class_id).order_by('graduation_year', 'faculty', 'major')

    context = {
        'student': student,
        'from_class': from_class,
        'all_classes': all_classes,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'classes/move.html', context)


# -------------------- 移除学生（管理员） --------------------

@admin_required
def remove_student_view(request):
    """
    从班级中移除学生（管理员功能）
    URL: /classes/remove/
    仅删除 UserClasses 表中的关联记录，不删除 User 本身
    """
    if request.method != 'GET':
        return redirect('/classes/')

    user_id = request.GET.get('user_id')
    class_id = request.GET.get('class_id')

    if not user_id or not class_id:
        messages.error(request, 'Missing required parameters.')
        return redirect('/classes/')

    try:
        user_id = int(user_id)
        class_id = int(class_id)
    except ValueError:
        messages.error(request, 'Invalid parameters.')
        return redirect('/classes/')

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM UserClasses WHERE user_id = %s AND class_id = %s", [user_id, class_id])

    messages.success(request, 'Student removed from class successfully.')
    return redirect(f'/classes/detail/{class_id}/')