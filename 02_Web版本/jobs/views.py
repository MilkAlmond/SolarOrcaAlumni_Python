# jobs/views.py
# 职位搜索模块视图

from django.shortcuts import render, redirect
from django.db import connection
from django.db import DatabaseError

from .models import WorkExperience
from users.models import User
from utils.levenshtein import get_similarity


def get_highest_degree(user_id):
    """
    获取用户的最高学历（用于搜索结果展示）
    优先级：PhD > Master > Bachelor
    """
    degree_map = {
        'Bachelor': '本科',
        'Master': '硕士',
        'PhD': '博士'
    }

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT degree_type, major FROM Degrees
                WHERE user_id = %s AND degree_type IN ('Bachelor', 'Master', 'PhD')
                ORDER BY 
                    CASE degree_type
                        WHEN 'PhD' THEN 3
                        WHEN 'Master' THEN 2
                        WHEN 'Bachelor' THEN 1
                        ELSE 0
                    END DESC
                LIMIT 1
            """, [user_id])
            row = cursor.fetchone()
            if row:
                degree_type, major = row
                display = degree_map.get(degree_type, degree_type)
                return f"{display} in {major}"
    except DatabaseError:
        pass
    return 'N/A'


def job_search_view(request):
    """
    职位搜索主页
    URL: /jobs/
    支持模糊搜索（Levenshtein 相似度，阈值 20%），结果按相似度排序
    """
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_role = request.session.get('user_role', '')
    search = request.GET.get('search', '').strip()
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('pageSize', 20))

    results = []
    total_results = 0
    total_pages = 1

    if search:
        all_jobs = WorkExperience.objects.all()

        ranked = []
        for job in all_jobs:
            title_score = get_similarity(search, job.job_title)
            employer_score = get_similarity(search, job.employer)
            industry_score = get_similarity(search, job.industry) if job.industry else 0

            max_score = max(title_score, employer_score, industry_score)

            if max_score > 20:
                user = User.objects.filter(user_id=job.user_id).first()
                highest_degree = get_highest_degree(job.user_id)

                ranked.append({
                    'job': job,
                    'user': user,
                    'user_name': user.full_name if user else 'Unknown',
                    'score': max_score,
                    'highest_degree': highest_degree
                })

        ranked.sort(key=lambda x: x['score'], reverse=True)

        total_results = len(ranked)

        start = (page - 1) * page_size
        end = start + page_size
        page_results = ranked[start:end]

        for item in page_results:
            results.append({
                'user_id': item['job'].user_id,
                'user_name': item['user_name'],
                'job_title': item['job'].job_title,
                'employer': item['job'].employer,
                'industry': item['job'].industry or '-',
                'start_year': item['job'].start_year,
                'highest_degree': item['highest_degree'],
                'similarity': item['score']
            })

        total_pages = (total_results + page_size - 1) // page_size if total_results > 0 else 1

    context = {
        'results': results,
        'search_keyword': search,
        'total_results': total_results,
        'current_page': page,
        'total_pages': total_pages,
        'page_size': page_size,
        'user_name': request.session.get('user_name', ''),
        'user_role': user_role,
        'has_search': bool(search),
    }
    return render(request, 'jobs/search.html', context)