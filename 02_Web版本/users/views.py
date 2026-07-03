import random
import datetime
import uuid
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import connection

from .models import User, VerificationToken, Degree, PasswordResetToken
from classes.models import Class, UserClass
from jobs.models import WorkExperience, ResearchPosition


# -------------------- 登录 / 登出 / 首页 --------------------

def login_view(request):
    """用户登录"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'users/login.html')

        if user.password_hash == password:
            request.session['user_id'] = user.user_id
            request.session['user_email'] = user.email
            request.session['user_role'] = user.role
            request.session['user_name'] = user.full_name
            request.session['is_logged_in'] = True
            return redirect('/home/')
        else:
            messages.error(request, 'Invalid email or password')

    # GET 请求：获取演示账号列表（从数据库读取）
    demo_accounts = []
    demo_emails = [
        'alumni1@demo.com',
        'alumni2@demo.com',
        'alumni3@demo.com',
        'teacher1@demo.com',
        'admin1@demo.com',
        'undergrad1@demo.com'
    ]
    for email in demo_emails:
        try:
            user = User.objects.get(email=email)
            demo_accounts.append({
                'email': user.email,
                'password': user.password_hash,
                'name': user.full_name,
                'role': user.role
            })
        except User.DoesNotExist:
            pass

    context = {
        'demo_accounts': demo_accounts
    }
    return render(request, 'users/login.html', context)


def logout_view(request):
    """用户登出"""
    request.session.flush()
    return redirect('/login/')


def home_view(request):
    """首页"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')
    context = {
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'users/home.html', context)


# -------------------- 注册（三步流程） --------------------

def register_view(request):
    """注册主页，根据 step 参数显示不同步骤"""
    step = request.GET.get('step', '1')

    if step == '1':
        return render(request, 'users/register_step1.html')

    if step == '2':
        student_id = request.session.get('temp_student_id')
        email = request.session.get('temp_email')
        if not student_id or not email:
            return redirect('/register/?step=1')
        return render(request, 'users/register_step2.html', {'email': email})

    if step == '3':
        email_verified = request.session.get('email_verified', False)
        if not email_verified:
            return redirect('/register/?step=1')
        return render(request, 'users/register_step3.html')

    return redirect('/register/?step=1')


def register_step1_post(request):
    """注册步骤1：验证学号和毕业年份"""
    if request.method != 'POST':
        return redirect('/register/?step=1')

    student_id = request.POST.get('student_id')
    graduation_year = request.POST.get('graduation_year')

    if not student_id or not graduation_year:
        messages.error(request, 'Please fill in all fields.')
        return render(request, 'users/register_step1.html')

    try:
        graduation_year = int(graduation_year)
        if graduation_year < 1950 or graduation_year > 2030:
            messages.error(request, 'Please enter a valid graduation year (1950-2030).')
            return render(request, 'users/register_step1.html')
    except ValueError:
        messages.error(request, 'Please enter a valid graduation year.')
        return render(request, 'users/register_step1.html')

    try:
        user = User.objects.get(student_id=student_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid student ID. Please check your information or contact alumni office.')
        return render(request, 'users/register_step1.html')

    if user.password_hash:
        messages.error(request, 'An account already exists for this student ID. Please login instead.')
        return render(request, 'users/register_step1.html')

    if user.graduation_year and user.graduation_year != graduation_year:
        messages.error(request, 'The graduation year you entered does not match our records.')
        return render(request, 'users/register_step1.html')

    request.session['temp_student_id'] = student_id
    request.session['temp_email'] = user.email
    request.session['temp_name'] = user.full_name

    return redirect('/register/?step=2')


def register_step2_post(request):
    """注册步骤2：发送并验证邮箱验证码"""
    if request.method != 'POST':
        return redirect('/register/?step=2')

    action = request.POST.get('action')

    if action == 'send_code':
        email = request.session.get('temp_email')
        if not email:
            return redirect('/register/?step=1')

        code = f"{random.randint(0, 999999):06d}"
        expires_at = datetime.datetime.now() + datetime.timedelta(minutes=10)

        VerificationToken.objects.update_or_create(
            email=email,
            defaults={
                'code': code,
                'expires_at': expires_at,
                'is_used': False
            }
        )

        request.session['demo_otp'] = code
        messages.success(request, f'Demo mode: Your verification code is {code}')
        return redirect('/register/?step=2')

    elif action == 'verify':
        entered_otp = request.POST.get('otp')
        demo_otp = request.session.get('demo_otp')

        if demo_otp and demo_otp == entered_otp:
            request.session['email_verified'] = True
            messages.success(request, 'Email verified successfully!')
            return redirect('/register/?step=3')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')
            return redirect('/register/?step=2')

    return redirect('/register/?step=2')


def register_step3_post(request):
    """注册步骤3：设置密码，完成注册"""
    if request.method != 'POST':
        return redirect('/register/?step=3')

    if not request.session.get('email_verified', False):
        return redirect('/register/?step=1')

    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')

    if not password or not confirm_password:
        messages.error(request, 'Please fill in all fields.')
        return render(request, 'users/register_step3.html')

    if password != confirm_password:
        messages.error(request, 'Passwords do not match.')
        return render(request, 'users/register_step3.html')

    if len(password) < 6:
        messages.error(request, 'Password must be at least 6 characters.')
        return render(request, 'users/register_step3.html')

    student_id = request.session.get('temp_student_id')
    try:
        user = User.objects.get(student_id=student_id)
        user.password_hash = password
        user.is_verified = True
        user.save()

        request.session.flush()
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('/login/')
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please register again.')
        return redirect('/register/?step=1')


# -------------------- 个人资料 --------------------

def profile_view(request, user_id=None):
    """查看个人资料"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    if user_id is None:
        user_id = request.session.get('user_id')

    viewer_role = request.session.get('user_role', '')
    viewer_id = request.session.get('user_id')

    user = get_object_or_404(User, user_id=user_id)

    if viewer_role not in ['admin'] and viewer_id != user_id:
        messages.error(request, 'You do not have permission to view this profile.')
        return redirect('/home/')

    degrees = Degree.objects.filter(user_id=user_id).order_by('-start_year')
    work_list = WorkExperience.objects.filter(user_id=user_id).order_by('-start_year')
    research_list = ResearchPosition.objects.filter(user_id=user_id).order_by('-start_year')

    class_ids = UserClass.objects.filter(user_id=user_id).values_list('class_id', flat=True)
    classes = Class.objects.filter(class_id__in=class_ids)

    is_own_profile = (viewer_id == user_id)

    context = {
        'profile_user': user,
        'degrees': degrees,
        'work_list': work_list,
        'research_list': research_list,
        'classes': classes,
        'is_own_profile': is_own_profile,
        'user_name': request.session.get('user_name', ''),
        'user_role': viewer_role,
    }
    return render(request, 'users/profile.html', context)


def edit_profile_view(request):
    """编辑个人资料"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_id = request.session.get('user_id')
    user = get_object_or_404(User, user_id=user_id)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        location = request.POST.get('location')

        if not full_name or not email:
            messages.error(request, 'Full name and email are required.')
            return render(request, 'users/edit_profile.html', {'user': user})

        user.full_name = full_name
        user.email = email
        user.location = location
        user.save()

        request.session['user_name'] = full_name
        messages.success(request, 'Profile updated successfully!')
        return redirect('/profile/')

    context = {
        'user': user,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'users/edit_profile.html', context)


# -------------------- 修改密码 --------------------

def change_password_view(request):
    """修改密码"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_id = request.session.get('user_id')
    user = get_object_or_404(User, user_id=user_id)

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'users/change_password.html')

        if user.password_hash != current_password:
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'users/change_password.html')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/change_password.html')

        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'users/change_password.html')

        user.password_hash = new_password
        user.save()

        messages.success(request, 'Password changed successfully!')
        return render(request, 'users/change_password.html')

    context = {
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'users/change_password.html', context)


# -------------------- 忘记密码 / 重置密码 --------------------

def forgot_password_view(request):
    """忘记密码 - 发送重置链接"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'users/forgot_password.html')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.success(request, 'If your email is registered, you will receive a password reset link.')
            return render(request, 'users/forgot_password.html')

        token = uuid.uuid4().hex
        expires_at = timezone.now() + timedelta(hours=1)

        PasswordResetToken.objects.create(
            user_id=user.user_id,
            token=token,
            expires_at=expires_at,
            is_used=False
        )

        reset_link = f"http://localhost:8081/reset-password/?token={token}"
        messages.success(request, f'Demo mode: Reset link - {reset_link}')
        return render(request, 'users/forgot_password.html', {'reset_link': reset_link})

    return render(request, 'users/forgot_password.html')


def reset_password_view(request):
    """重置密码 - 验证令牌并更新密码"""
    token = request.GET.get('token') or request.POST.get('token')

    if not token:
        messages.error(request, 'Invalid reset link.')
        return redirect('/forgot-password/')

    try:
        reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('/forgot-password/')

    if reset_token.expires_at < timezone.now():
        messages.error(request, 'Reset link has expired. Please request a new one.')
        return redirect('/forgot-password/')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not password or not confirm_password:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'users/reset_password.html', {'token': token})

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/reset_password.html', {'token': token})

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'users/reset_password.html', {'token': token})

        try:
            user = User.objects.get(user_id=reset_token.user_id)
            user.password_hash = password
            user.save()

            reset_token.is_used = True
            reset_token.save()

            messages.success(request, 'Password reset successfully! Please login.')
            return redirect('/login/')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('/forgot-password/')

    context = {
        'token': token,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'users/reset_password.html', context)


# -------------------- 学位 CRUD --------------------

def add_degree_view(request):
    """添加学位"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_id = request.session.get('user_id')

    if request.method == 'POST':
        degree_type = request.POST.get('degree_type')
        major = request.POST.get('major')
        institution = request.POST.get('institution')
        start_year = request.POST.get('start_year')
        end_year = request.POST.get('end_year') or None
        minor = request.POST.get('minor') or ''
        certificate = request.POST.get('certificate') or ''
        original_major = request.POST.get('original_major') or ''
        transfer_year = request.POST.get('transfer_year') or None
        second_degree = request.POST.get('second_degree') or ''

        if not all([degree_type, major, institution, start_year]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'users/add_degree.html')

        try:
            start_year = int(start_year)
            if end_year:
                end_year = int(end_year)
            if transfer_year:
                transfer_year = int(transfer_year)
        except ValueError:
            messages.error(request, 'Invalid year format.')
            return render(request, 'users/add_degree.html')

        if end_year and start_year > end_year:
            messages.error(request, 'Start year must be less than or equal to end year.')
            return render(request, 'users/add_degree.html')

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Degrees (user_id, degree_type, major, institution, start_year, end_year, minor, certificate, original_major, transfer_year, second_degree)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [user_id, degree_type, major, institution, start_year, end_year, minor, certificate, original_major, transfer_year, second_degree]
            )

        messages.success(request, 'Degree added successfully!')
        return redirect('/profile/')

    context = {
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'users/add_degree.html', context)


def edit_degree_view(request, degree_id):
    """编辑学位"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_id = request.session.get('user_id')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Degrees WHERE degree_id = %s", [degree_id])
        row = cursor.fetchone()

    if not row:
        messages.error(request, 'Degree not found.')
        return redirect('/profile/')

    degree_data = row

    if degree_data[1] != user_id:
        messages.error(request, 'You do not have permission to edit this degree.')
        return redirect('/profile/')

    if request.method == 'POST':
        degree_type = request.POST.get('degree_type')
        major = request.POST.get('major')
        institution = request.POST.get('institution')
        start_year = request.POST.get('start_year')
        end_year = request.POST.get('end_year') or None
        minor = request.POST.get('minor') or ''
        certificate = request.POST.get('certificate') or ''
        original_major = request.POST.get('original_major') or ''
        transfer_year = request.POST.get('transfer_year') or None
        second_degree = request.POST.get('second_degree') or ''

        try:
            start_year = int(start_year)
            if end_year:
                end_year = int(end_year)
            if transfer_year:
                transfer_year = int(transfer_year)
        except ValueError:
            messages.error(request, 'Invalid year format.')
            return render(request, 'users/edit_degree.html', {'degree': degree_data})

        if end_year and start_year > end_year:
            messages.error(request, 'Start year must be less than or equal to end year.')
            return render(request, 'users/edit_degree.html', {'degree': degree_data})

        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE Degrees SET degree_type=%s, major=%s, institution=%s, start_year=%s, end_year=%s, minor=%s, certificate=%s, original_major=%s, transfer_year=%s, second_degree=%s
                WHERE degree_id=%s
                """,
                [degree_type, major, institution, start_year, end_year, minor, certificate, original_major, transfer_year, second_degree, degree_id]
            )

        messages.success(request, 'Degree updated successfully!')
        return redirect('/profile/')

    context = {
        'degree': degree_data,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'users/edit_degree.html', context)


def delete_degree_view(request, degree_id):
    """删除学位"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_id = request.session.get('user_id')

    with connection.cursor() as cursor:
        cursor.execute("SELECT user_id FROM Degrees WHERE degree_id = %s", [degree_id])
        row = cursor.fetchone()

    if not row:
        messages.error(request, 'Degree not found.')
        return redirect('/profile/')

    if row[0] != user_id:
        messages.error(request, 'You do not have permission to delete this degree.')
        return redirect('/profile/')

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM Degrees WHERE degree_id = %s", [degree_id])

    messages.success(request, 'Degree deleted successfully.')
    return redirect('/profile/')


# -------------------- 工作经历 CRUD --------------------

def add_work_view(request):
    """添加工作经历"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_id = request.session.get('user_id')

    if request.method == 'POST':
        job_title = request.POST.get('job_title')
        employer = request.POST.get('employer')
        start_year = request.POST.get('start_year')
        end_year = request.POST.get('end_year') or None
        is_current = request.POST.get('is_current') == 'on'
        industry = request.POST.get('industry') or ''

        if not all([job_title, employer, start_year]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'users/add_work.html')

        try:
            start_year = int(start_year)
            if end_year:
                end_year = int(end_year)
        except ValueError:
            messages.error(request, 'Invalid year format.')
            return render(request, 'users/add_work.html')

        if is_current:
            end_year = None

        if end_year and start_year > end_year:
            messages.error(request, 'Start year must be less than or equal to end year.')
            return render(request, 'users/add_work.html')

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO WorkExperience (user_id, job_title, employer, start_year, end_year, is_current, industry)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                [user_id, job_title, employer, start_year, end_year, is_current, industry]
            )

        messages.success(request, 'Work experience added successfully!')
        return redirect('/profile/')

    context = {
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'users/add_work.html', context)


def edit_work_view(request, work_id):
    """编辑工作经历"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_id = request.session.get('user_id')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM WorkExperience WHERE work_id = %s", [work_id])
        row = cursor.fetchone()

    if not row:
        messages.error(request, 'Work experience not found.')
        return redirect('/profile/')

    work_data = row

    if work_data[1] != user_id:
        messages.error(request, 'You do not have permission to edit this work experience.')
        return redirect('/profile/')

    if request.method == 'POST':
        job_title = request.POST.get('job_title')
        employer = request.POST.get('employer')
        start_year = request.POST.get('start_year')
        end_year = request.POST.get('end_year') or None
        is_current = request.POST.get('is_current') == 'on'
        industry = request.POST.get('industry') or ''

        try:
            start_year = int(start_year)
            if end_year:
                end_year = int(end_year)
        except ValueError:
            messages.error(request, 'Invalid year format.')
            return render(request, 'users/edit_work.html', {'work': work_data})

        if is_current:
            end_year = None

        if end_year and start_year > end_year:
            messages.error(request, 'Start year must be less than or equal to end year.')
            return render(request, 'users/edit_work.html', {'work': work_data})

        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE WorkExperience SET job_title=%s, employer=%s, start_year=%s, end_year=%s, is_current=%s, industry=%s
                WHERE work_id=%s
                """,
                [job_title, employer, start_year, end_year, is_current, industry, work_id]
            )

        messages.success(request, 'Work experience updated successfully!')
        return redirect('/profile/')

    context = {
        'work': work_data,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'users/edit_work.html', context)


def delete_work_view(request, work_id):
    """删除工作经历"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_id = request.session.get('user_id')

    with connection.cursor() as cursor:
        cursor.execute("SELECT user_id FROM WorkExperience WHERE work_id = %s", [work_id])
        row = cursor.fetchone()

    if not row:
        messages.error(request, 'Work experience not found.')
        return redirect('/profile/')

    if row[0] != user_id:
        messages.error(request, 'You do not have permission to delete this work experience.')
        return redirect('/profile/')

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM WorkExperience WHERE work_id = %s", [work_id])

    messages.success(request, 'Work experience deleted successfully.')
    return redirect('/profile/')


# -------------------- 科研经历 CRUD --------------------

def add_research_view(request):
    """添加科研经历"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_id = request.session.get('user_id')

    if request.method == 'POST':
        position_type = request.POST.get('position_type')
        institution = request.POST.get('institution')
        department = request.POST.get('department') or ''
        start_year = request.POST.get('start_year')
        end_year = request.POST.get('end_year') or None
        is_current = request.POST.get('is_current') == 'on'

        if not all([position_type, institution, start_year]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'users/add_research.html')

        try:
            start_year = int(start_year)
            if end_year:
                end_year = int(end_year)
        except ValueError:
            messages.error(request, 'Invalid year format.')
            return render(request, 'users/add_research.html')

        if is_current:
            end_year = None

        if end_year and start_year > end_year:
            messages.error(request, 'Start year must be less than or equal to end year.')
            return render(request, 'users/add_research.html')

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ResearchPositions (user_id, position_type, institution, department, start_year, end_year, is_current)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                [user_id, position_type, institution, department, start_year, end_year, is_current]
            )

        messages.success(request, 'Research position added successfully!')
        return redirect('/profile/')

    context = {
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'users/add_research.html', context)


def edit_research_view(request, position_id):
    """编辑科研经历"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_id = request.session.get('user_id')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM ResearchPositions WHERE position_id = %s", [position_id])
        row = cursor.fetchone()

    if not row:
        messages.error(request, 'Research position not found.')
        return redirect('/profile/')

    research_data = row

    if research_data[1] != user_id:
        messages.error(request, 'You do not have permission to edit this research position.')
        return redirect('/profile/')

    if request.method == 'POST':
        position_type = request.POST.get('position_type')
        institution = request.POST.get('institution')
        department = request.POST.get('department') or ''
        start_year = request.POST.get('start_year')
        end_year = request.POST.get('end_year') or None
        is_current = request.POST.get('is_current') == 'on'

        try:
            start_year = int(start_year)
            if end_year:
                end_year = int(end_year)
        except ValueError:
            messages.error(request, 'Invalid year format.')
            return render(request, 'users/edit_research.html', {'research': research_data})

        if is_current:
            end_year = None

        if end_year and start_year > end_year:
            messages.error(request, 'Start year must be less than or equal to end year.')
            return render(request, 'users/edit_research.html', {'research': research_data})

        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE ResearchPositions SET position_type=%s, institution=%s, department=%s, start_year=%s, end_year=%s, is_current=%s
                WHERE position_id=%s
                """,
                [position_type, institution, department, start_year, end_year, is_current, position_id]
            )

        messages.success(request, 'Research position updated successfully!')
        return redirect('/profile/')

    context = {
        'research': research_data,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'users/edit_research.html', context)


def delete_research_view(request, position_id):
    """删除科研经历"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_id = request.session.get('user_id')

    with connection.cursor() as cursor:
        cursor.execute("SELECT user_id FROM ResearchPositions WHERE position_id = %s", [position_id])
        row = cursor.fetchone()

    if not row:
        messages.error(request, 'Research position not found.')
        return redirect('/profile/')

    if row[0] != user_id:
        messages.error(request, 'You do not have permission to delete this research position.')
        return redirect('/profile/')

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM ResearchPositions WHERE position_id = %s", [position_id])

    messages.success(request, 'Research position deleted successfully.')
    return redirect('/profile/')


# -------------------- 自定义主题页面（新增） --------------------

def custom_theme_view(request):
    """自定义主题设计器页面"""
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')
    context = {
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'users/custom_theme.html', context)