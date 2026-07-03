# forum/views.py
# 论坛模块视图

from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Thread, Reply, Report
from users.models import User


def thread_list_view(request):
    """
    帖子列表页
    URL: /forum/
    """
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_role = request.session.get('user_role', '')

    # 根据角色决定可见范围
    if user_role in ['alumni', 'admin']:
        threads = Thread.objects.all()
    else:
        threads = Thread.objects.filter(is_alumni_only=False)

    threads = threads.order_by('-is_pinned', '-created_at')

    for thread in threads:
        thread.reply_count = Reply.objects.filter(thread_id=thread.thread_id).count()
        try:
            author = User.objects.get(user_id=thread.user_id)
            thread.author_name = author.full_name
        except User.DoesNotExist:
            thread.author_name = 'Unknown'

    context = {
        'threads': threads,
        'user_name': request.session.get('user_name', ''),
        'user_role': user_role,
    }
    return render(request, 'forum/thread_list.html', context)


def new_thread_view(request):
    """
    创建新帖子
    URL: /forum/new/
    权限：仅校友和管理员
    """
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_role = request.session.get('user_role', '')

    if user_role not in ['alumni', 'admin']:
        messages.error(request, 'You do not have permission to create new threads.')
        return redirect('/forum/')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        is_alumni_only = request.POST.get('is_alumni_only') == 'true'

        if not title or not content:
            messages.error(request, 'Title and content are required.')
            return render(request, 'forum/new_thread.html')

        thread = Thread.objects.create(
            user_id=request.session.get('user_id'),
            title=title,
            content=content,
            is_alumni_only=is_alumni_only,
            is_pinned=False,
            is_locked=False,
            view_count=0
        )

        messages.success(request, 'Thread posted successfully!')
        return redirect(f'/forum/thread/{thread.thread_id}/')

    context = {
        'user_name': request.session.get('user_name', ''),
        'user_role': user_role,
    }
    return render(request, 'forum/new_thread.html', context)


def thread_detail_view(request, thread_id):
    """
    帖子详情页（含回复列表）
    URL: /forum/thread/<thread_id>/
    """
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_role = request.session.get('user_role', '')

    try:
        thread = Thread.objects.get(thread_id=thread_id)
    except Thread.DoesNotExist:
        messages.error(request, 'Thread not found.')
        return redirect('/forum/')

    # 校友专属帖子权限检查
    if thread.is_alumni_only and user_role not in ['alumni', 'admin']:
        messages.error(request, 'This thread is only visible to alumni.')
        return redirect('/forum/')

    # 增加浏览次数
    thread.view_count = (thread.view_count or 0) + 1
    thread.save(update_fields=['view_count'])

    try:
        author = User.objects.get(user_id=thread.user_id)
        thread.author_name = author.full_name
    except User.DoesNotExist:
        thread.author_name = 'Unknown'

    replies = Reply.objects.filter(thread_id=thread_id).order_by('created_at')

    for reply in replies:
        try:
            author = User.objects.get(user_id=reply.user_id)
            reply.author_name = author.full_name
            reply.author_role = author.role
        except User.DoesNotExist:
            reply.author_name = 'Unknown'
            reply.author_role = ''

    can_reply = (not thread.is_locked) and (user_role in ['alumni', 'admin'])

    context = {
        'thread': thread,
        'replies': replies,
        'can_reply': can_reply,
        'user_name': request.session.get('user_name', ''),
        'user_role': user_role,
    }
    return render(request, 'forum/thread_detail.html', context)


def reply_thread_view(request, thread_id):
    """
    添加回复
    URL: /forum/thread/<thread_id>/reply/ (POST)
    权限：仅校友和管理员
    """
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_role = request.session.get('user_role', '')

    if user_role not in ['alumni', 'admin']:
        messages.error(request, 'You do not have permission to reply.')
        return redirect('/forum/')

    if request.method != 'POST':
        return redirect(f'/forum/thread/{thread_id}/')

    content = request.POST.get('content', '').strip()

    if not content:
        messages.error(request, 'Reply content is required.')
        return redirect(f'/forum/thread/{thread_id}/')

    try:
        thread = Thread.objects.get(thread_id=thread_id)
    except Thread.DoesNotExist:
        messages.error(request, 'Thread not found.')
        return redirect('/forum/')

    if thread.is_locked:
        messages.error(request, 'This thread is locked. No new replies allowed.')
        return redirect(f'/forum/thread/{thread_id}/')

    Reply.objects.create(
        thread_id=thread_id,
        user_id=request.session.get('user_id'),
        content=content
    )

    messages.success(request, 'Reply posted successfully!')
    return redirect(f'/forum/thread/{thread_id}/')


def lock_thread_view(request, thread_id):
    """
    锁定/解锁帖子（管理员）
    URL: /forum/thread/<thread_id>/lock/
    """
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_role = request.session.get('user_role', '')
    if user_role != 'admin':
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('/forum/')

    try:
        thread = Thread.objects.get(thread_id=thread_id)
        thread.is_locked = not thread.is_locked
        thread.save()
        status = 'locked' if thread.is_locked else 'unlocked'
        messages.success(request, f'Thread has been {status}.')
    except Thread.DoesNotExist:
        messages.error(request, 'Thread not found.')

    return redirect(f'/forum/thread/{thread_id}/')


def pin_thread_view(request, thread_id):
    """
    置顶/取消置顶帖子（管理员）
    URL: /forum/thread/<thread_id>/pin/
    """
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_role = request.session.get('user_role', '')
    if user_role != 'admin':
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('/forum/')

    try:
        thread = Thread.objects.get(thread_id=thread_id)

        # 置顶时先取消所有其他帖子的置顶
        if not thread.is_pinned:
            Thread.objects.all().update(is_pinned=False)

        thread.is_pinned = not thread.is_pinned
        thread.save()
        status = 'pinned' if thread.is_pinned else 'unpinned'
        messages.success(request, f'Thread has been {status}.')
    except Thread.DoesNotExist:
        messages.error(request, 'Thread not found.')

    return redirect(f'/forum/thread/{thread_id}/')


def delete_thread_view(request, thread_id):
    """
    删除帖子（管理员）
    URL: /forum/thread/<thread_id>/delete/
    """
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_role = request.session.get('user_role', '')
    if user_role != 'admin':
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('/forum/')

    try:
        thread = Thread.objects.get(thread_id=thread_id)
        thread_title = thread.title
        thread.delete()
        messages.success(request, f'Thread "{thread_title}" has been deleted.')
    except Thread.DoesNotExist:
        messages.error(request, 'Thread not found.')

    return redirect('/forum/')


def report_content_view(request, content_type, content_id):
    """
    举报帖子或回复
    URL: /forum/report/thread/<thread_id>/ 或 /forum/report/reply/<reply_id>/
    """
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    # 获取被举报的内容信息
    if content_type == 'thread':
        try:
            target = Thread.objects.get(thread_id=content_id)
            target_title = target.title
            thread_id = content_id
            reply_id = None
        except Thread.DoesNotExist:
            messages.error(request, 'Thread not found.')
            return redirect('/forum/')
    elif content_type == 'reply':
        try:
            target = Reply.objects.get(reply_id=content_id)
            target_title = f'Reply to thread {target.thread_id}'
            thread_id = target.thread_id
            reply_id = content_id
        except Reply.DoesNotExist:
            messages.error(request, 'Reply not found.')
            return redirect('/forum/')
    else:
        messages.error(request, 'Invalid content type.')
        return redirect('/forum/')

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        details = request.POST.get('details', '').strip()

        if not reason:
            messages.error(request, 'Please select a reason for reporting.')
            return render(request, 'forum/report.html', {
                'content_type': content_type,
                'content_id': content_id,
                'target_title': target_title,
            })

        Report.objects.create(
            reporter_user_id=request.session.get('user_id'),
            thread_id=thread_id if content_type == 'thread' else None,
            reply_id=reply_id if content_type == 'reply' else None,
            reason=reason,
            details=details or '',
            status='pending'
        )

        messages.success(request, 'Report submitted successfully. An admin will review it.')
        return redirect(f'/forum/thread/{thread_id}/')

    context = {
        'content_type': content_type,
        'content_id': content_id,
        'target_title': target_title,
        'user_name': request.session.get('user_name', ''),
        'user_role': request.session.get('user_role', ''),
    }
    return render(request, 'forum/report.html', context)