# stats/views.py
# 统计分析模块视图

from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse


def stats_view(request):
    """
    统计分析主页
    URL: /stats/
    """
    if not request.session.get('is_logged_in', False):
        return redirect('/login/')

    user_role = request.session.get('user_role', '')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT major FROM Degrees
            WHERE degree_type = 'Bachelor' AND major IS NOT NULL
            ORDER BY major
        """)
        majors = [row[0] for row in cursor.fetchall()]

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT industry FROM WorkExperience
            WHERE industry IS NOT NULL AND industry != ''
            ORDER BY industry
        """)
        industries = [row[0] for row in cursor.fetchall()]

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT location FROM Users
            WHERE location IS NOT NULL AND location != ''
            ORDER BY location
        """)
        locations = [row[0] for row in cursor.fetchall()]

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT graduation_year FROM Users
            WHERE graduation_year IS NOT NULL
            ORDER BY graduation_year DESC
        """)
        years = [row[0] for row in cursor.fetchall()]

    context = {
        'user_name': request.session.get('user_name', ''),
        'user_role': user_role,
        'majors': majors,
        'industries': industries,
        'locations': locations,
        'years': years,
    }
    return render(request, 'stats/stats.html', context)


def stats_api(request):
    """
    统计数据 API（供 Chart.js 渲染图表）
    URL: /stats/api/?type=<type>
    支持：gender_ratio, industry_distribution, location_distribution, degree_distribution
    """
    data_type = request.GET.get('type', '')

    if data_type == 'gender_ratio':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT u.gender, COUNT(*) as count
                FROM Users u
                INNER JOIN Degrees d ON u.user_id = d.user_id
                WHERE u.gender IS NOT NULL
                GROUP BY u.gender
            """)
            rows = cursor.fetchall()
        return JsonResponse([{'gender': row[0], 'count': row[1]} for row in rows], safe=False)

    elif data_type == 'industry_distribution':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT industry, COUNT(*) as count
                FROM WorkExperience
                WHERE industry IS NOT NULL
                GROUP BY industry
                ORDER BY count DESC
            """)
            rows = cursor.fetchall()
        return JsonResponse([{'industry': row[0], 'count': row[1]} for row in rows], safe=False)

    elif data_type == 'location_distribution':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT location, COUNT(*) as count
                FROM Users
                WHERE location IS NOT NULL
                GROUP BY location
                ORDER BY count DESC
            """)
            rows = cursor.fetchall()
        return JsonResponse([{'location': row[0], 'count': row[1]} for row in rows], safe=False)

    elif data_type == 'degree_distribution':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT degree_type, COUNT(*) as count
                FROM Degrees
                GROUP BY degree_type
            """)
            rows = cursor.fetchall()
        return JsonResponse([{'degree': row[0], 'count': row[1]} for row in rows], safe=False)

    return JsonResponse([], safe=False)


def stats_preset_api(request):
    """
    预设问题 API
    URL: /stats/api/preset/?q=<question_id>&[params]
    """
    question = request.GET.get('q', '')

    # 问题1：性别比例
    if question == 'gender_ratio':
        degree_type = request.GET.get('degree_type', 'All')
        industry = request.GET.get('industry', 'All')

        sql = """
            SELECT u.gender, COUNT(*) as count
            FROM Users u
            INNER JOIN Degrees d ON u.user_id = d.user_id
            LEFT JOIN WorkExperience w ON u.user_id = w.user_id AND w.is_current = 1
            WHERE u.gender IS NOT NULL AND u.gender IN ('M', 'F')
        """
        params = []
        if degree_type != 'All':
            sql += " AND d.degree_type = %s"
            params.append(degree_type)
        if industry != 'All':
            sql += " AND w.industry = %s"
            params.append(industry)
        sql += " GROUP BY u.gender"

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        male = 0
        female = 0
        for row in rows:
            if row[0] == 'M':
                male = row[1]
            elif row[0] == 'F':
                female = row[1]
        total = male + female

        if total > 0:
            degree_display = degree_type if degree_type != 'All' else 'All'
            industry_display = industry if industry != 'All' else 'All'
            return JsonResponse({
                'result': f'{degree_display} graduates in {industry_display}: Male: {male} ({male*100/total:.1f}%), Female: {female} ({female*100/total:.1f}%)',
                'male': male,
                'female': female,
                'total': total
            })
        return JsonResponse({'result': 'No data available.'})

    # 问题2：海外工作比例
    elif question == 'abroad_percentage':
        degree_type = request.GET.get('degree_type', 'All')

        sql = """
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN u.location = 'Overseas' THEN 1 ELSE 0 END) as abroad
            FROM Users u
            INNER JOIN Degrees d ON u.user_id = d.user_id
            WHERE 1=1
        """
        params = []
        if degree_type != 'All':
            sql += " AND d.degree_type = %s"
            params.append(degree_type)

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()

        total = row[0] if row else 0
        abroad = row[1] if row else 0
        pct = abroad * 100 / total if total > 0 else 0
        degree_display = degree_type if degree_type != 'All' else 'All'

        return JsonResponse({'result': f'{degree_display} graduates working abroad: {abroad} ({pct:.1f}%)' if total > 0 else 'No data available.'})

    # 问题3：职业转型方向
    elif question == 'career_switch':
        major = request.GET.get('major', 'All')

        sql = """
            SELECT w.industry, COUNT(*) as count
            FROM WorkExperience w
            INNER JOIN Degrees d ON w.user_id = d.user_id
            WHERE d.degree_type = 'Bachelor' AND w.industry IS NOT NULL AND w.industry != ''
        """
        params = []
        if major != 'All':
            sql += " AND d.major = %s"
            params.append(major)
        sql += " GROUP BY w.industry ORDER BY count DESC LIMIT 1"

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()

        major_display = major if major != 'All' else 'All'
        if row:
            return JsonResponse({'result': f'Most common career switch for {major_display} graduates: {row[0]} ({row[1]} people)'})
        return JsonResponse({'result': f'No career switch data available for {major_display} graduates.'})

    # 问题4：近年毕业生行业流入
    elif question == 'recent_graduates':
        degree_type = request.GET.get('degree_type', 'All')
        industry = request.GET.get('industry', 'All')
        current_year = 2026
        recent_start = current_year - 3
        older_start = current_year - 6
        older_end = current_year - 4

        sql = """
            SELECT
                SUM(CASE WHEN d.end_year BETWEEN %s AND %s THEN 1 ELSE 0 END) as recent_total,
                SUM(CASE WHEN d.end_year BETWEEN %s AND %s AND w.work_id IS NOT NULL THEN 1 ELSE 0 END) as recent_employed,
                SUM(CASE WHEN d.end_year BETWEEN %s AND %s THEN 1 ELSE 0 END) as older_total,
                SUM(CASE WHEN d.end_year BETWEEN %s AND %s AND w.work_id IS NOT NULL THEN 1 ELSE 0 END) as older_employed
            FROM Degrees d
            LEFT JOIN WorkExperience w ON d.user_id = w.user_id AND w.is_current = 1
            WHERE d.degree_type = 'Bachelor'
        """
        params = [recent_start, current_year, recent_start, current_year, older_start, older_end, older_start, older_end]

        if degree_type != 'All':
            sql += " AND d.degree_type = %s"
            params.append(degree_type)
        if industry != 'All':
            sql += " AND w.industry = %s"
            params.append(industry)

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()

        if row:
            recent_total, recent_employed, older_total, older_employed = row
            recent_pct = recent_employed * 100 / recent_total if recent_total > 0 else 0
            older_pct = older_employed * 100 / older_total if older_total > 0 else 0

            degree_display = degree_type if degree_type != 'All' else 'Bachelor'
            industry_display = industry if industry != 'All' else 'All'
            increase_text = 'Yes, more recent graduates are entering this industry.' if recent_pct > older_pct else 'No significant increase.'

            return JsonResponse({
                'result': f'{degree_display} graduates ({recent_start}-{current_year}): {recent_pct:.1f}% in {industry_display} | {degree_display} graduates ({older_start}-{older_end}): {older_pct:.1f}% | {increase_text}',
                'recent_percent': recent_pct,
                'older_percent': older_pct
            })
        return JsonResponse({'result': 'No data available.'})

    # 问题5：学历薪资对比
    elif question == 'salary_comparison':
        degree1 = request.GET.get('degree1', 'Bachelor')
        degree2 = request.GET.get('degree2', 'Master')
        industry = request.GET.get('industry', 'All')

        sql = """
            SELECT
                AVG(CASE WHEN d.degree_type = %s THEN u.salary ELSE NULL END) as salary1,
                AVG(CASE WHEN d.degree_type = %s THEN u.salary ELSE NULL END) as salary2
            FROM Users u
            INNER JOIN Degrees d ON u.user_id = d.user_id
            LEFT JOIN WorkExperience w ON u.user_id = w.user_id AND w.is_current = 1
            WHERE u.salary IS NOT NULL AND u.salary > 0
        """
        params = [degree1, degree2]
        if industry != 'All':
            sql += " AND w.industry = %s"
            params.append(industry)

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()

        s1 = row[0] or 0
        s2 = row[1] or 0
        industry_display = industry if industry != 'All' else 'All'

        if s1 > 0 and s2 > 0:
            compare_text = f'{degree1} graduates earn more' if s1 > s2 else f'{degree2} graduates earn more'
            return JsonResponse({'result': f'{degree1}: ¥{s1:.0f} | {degree2}: ¥{s2:.0f} | {compare_text} in {industry_display}'})
        elif s1 > 0:
            return JsonResponse({'result': f'{degree1}: ¥{s1:.0f} | {degree2}: No data available'})
        elif s2 > 0:
            return JsonResponse({'result': f'{degree1}: No data available | {degree2}: ¥{s2:.0f}'})
        return JsonResponse({'result': 'Insufficient data for comparison.'})

    # 问题6：毕业生所在地分布
    elif question == 'location_by_degree':
        degree_type = request.GET.get('degree_type', 'All')

        sql = """
            SELECT u.location, COUNT(*) as count
            FROM Users u
            INNER JOIN Degrees d ON u.user_id = d.user_id
            WHERE u.location IS NOT NULL
        """
        params = []
        if degree_type != 'All':
            sql += " AND d.degree_type = %s"
            params.append(degree_type)
        sql += " GROUP BY u.location ORDER BY count DESC"

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        if rows:
            locations = ', '.join([f'{row[0]}: {row[1]}' for row in rows])
            degree_display = degree_type if degree_type != 'All' else 'All'
            return JsonResponse({'result': f'{degree_display} graduates locations: {locations}'})
        return JsonResponse({'result': 'No location data available.'})

    # 问题7：专业平均薪资
    elif question == 'salary_by_major':
        major = request.GET.get('major', 'All')

        sql = """
            SELECT AVG(u.salary) as avg_salary, COUNT(*) as count
            FROM Users u
            INNER JOIN Degrees d ON u.user_id = d.user_id
            WHERE d.degree_type = 'Bachelor' AND u.salary IS NOT NULL AND u.salary > 0
        """
        params = []
        if major != 'All':
            sql += " AND d.major = %s"
            params.append(major)

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()

        major_display = major if major != 'All' else 'All'
        if row and row[0]:
            return JsonResponse({'result': f'{major_display} graduates average salary: ¥{row[0]:.0f} (based on {row[1]} responses)'})
        return JsonResponse({'result': f'No salary data available for {major_display} graduates.'})

    # 问题8：最集中行业
    elif question == 'top_industry_by_degree':
        degree_type = request.GET.get('degree_type', 'All')

        sql = """
            SELECT w.industry, COUNT(*) as count
            FROM WorkExperience w
            INNER JOIN Degrees d ON w.user_id = d.user_id
            WHERE w.industry IS NOT NULL AND w.industry != '' AND w.is_current = 1
        """
        params = []
        if degree_type != 'All':
            sql += " AND d.degree_type = %s"
            params.append(degree_type)
        sql += " GROUP BY w.industry ORDER BY count DESC LIMIT 1"

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()

        degree_display = degree_type if degree_type != 'All' else 'All'
        if row:
            return JsonResponse({'result': f'{degree_display} graduates are most concentrated in {row[0]} ({row[1]} people)'})
        return JsonResponse({'result': f'No industry data available for {degree_display} graduates.'})

    # 问题9：辅修学位/证书统计
    elif question == 'minor_certificate_count':
        degree_type = request.GET.get('degree_type', 'All')

        sql = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN minor IS NOT NULL AND minor != '' THEN 1 ELSE 0 END) as with_minor,
                SUM(CASE WHEN certificate IS NOT NULL AND certificate != '' THEN 1 ELSE 0 END) as with_certificate
            FROM Degrees
            WHERE 1=1
        """
        params = []
        if degree_type != 'All':
            sql += " AND degree_type = %s"
            params.append(degree_type)

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()

        degree_display = degree_type if degree_type != 'All' else 'All'
        if row and row[0] > 0:
            total, with_minor, with_certificate = row
            minor_pct = with_minor * 100 / total
            cert_pct = with_certificate * 100 / total
            return JsonResponse({
                'result': f'{degree_display} graduates: Total: {total} | With Minor: {with_minor} ({minor_pct:.1f}%) | With Certificate: {with_certificate} ({cert_pct:.1f}%)'
            })
        return JsonResponse({'result': f'No data available for {degree_display} graduates.'})

    # 问题10：最常见职位
    elif question == 'top_job_title_by_major':
        major = request.GET.get('major', 'All')

        sql = """
            SELECT w.job_title, COUNT(*) as count
            FROM WorkExperience w
            INNER JOIN Degrees d ON w.user_id = d.user_id
            WHERE d.degree_type = 'Bachelor' AND w.job_title IS NOT NULL AND w.job_title != ''
        """
        params = []
        if major != 'All':
            sql += " AND d.major = %s"
            params.append(major)
        sql += " GROUP BY w.job_title ORDER BY count DESC LIMIT 1"

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            row = cursor.fetchone()

        major_display = major if major != 'All' else 'All'
        if row:
            return JsonResponse({'result': f'Most common job title for {major_display} graduates: "{row[0]}" ({row[1]} people)'})
        return JsonResponse({'result': f'No job title data available for {major_display} graduates.'})

    return JsonResponse({'result': 'Unknown question.'})


def stats_custom_api(request):
    """
    自定义多维度分析 API
    URL: /stats/api/custom/?[filters]
    支持：industry, location, gender, start_year, end_year, minor, certificate, employment
    """
    industry = request.GET.get('industry', '')
    location = request.GET.get('location', '')
    gender = request.GET.get('gender', '')
    start_year = request.GET.get('start_year', '')
    end_year = request.GET.get('end_year', '')
    has_minor = request.GET.get('minor', '')
    has_certificate = request.GET.get('certificate', '')
    employment_status = request.GET.get('employment', '')

    sql = """
        SELECT u.user_id, u.full_name, u.gender, u.location,
               d.degree_type, d.major, d.end_year as grad_year,
               w.job_title, w.employer, w.industry,
               CASE WHEN d.minor IS NOT NULL AND d.minor != '' THEN 1 ELSE 0 END as has_minor,
               CASE WHEN d.certificate IS NOT NULL AND d.certificate != '' THEN 1 ELSE 0 END as has_certificate
        FROM Users u
        LEFT JOIN Degrees d ON u.user_id = d.user_id AND d.degree_type = 'Bachelor'
        LEFT JOIN WorkExperience w ON u.user_id = w.user_id AND w.is_current = 1
        WHERE u.role = 'alumni'
    """
    params = []

    if industry:
        sql += " AND w.industry = %s"
        params.append(industry)
    if location:
        sql += " AND u.location = %s"
        params.append(location)
    if gender:
        sql += " AND u.gender = %s"
        params.append(gender)
    if start_year:
        sql += " AND d.end_year >= %s"
        params.append(int(start_year))
    if end_year:
        sql += " AND d.end_year <= %s"
        params.append(int(end_year))
    if has_minor == 'yes':
        sql += " AND d.minor IS NOT NULL AND d.minor != ''"
    elif has_minor == 'no':
        sql += " AND (d.minor IS NULL OR d.minor = '')"
    if has_certificate == 'yes':
        sql += " AND d.certificate IS NOT NULL AND d.certificate != ''"
    elif has_certificate == 'no':
        sql += " AND (d.certificate IS NULL OR d.certificate = '')"
    if employment_status == 'employed':
        sql += " AND w.work_id IS NOT NULL"
    elif employment_status == 'unemployed':
        sql += " AND w.work_id IS NULL"

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()

    total = len(rows)
    industry_count = {}
    location_count = {}
    year_count = {}
    minor_count = 0
    cert_count = 0

    for row in rows:
        ind = row[10] if len(row) > 10 else None
        if ind:
            industry_count[ind] = industry_count.get(ind, 0) + 1
        loc = row[3] if len(row) > 3 else None
        if loc:
            location_count[loc] = location_count.get(loc, 0) + 1
        year = row[6] if len(row) > 6 else None
        if year:
            year_count[year] = year_count.get(year, 0) + 1
        if len(row) > 11 and row[11]:
            minor_count += 1
        if len(row) > 12 and row[12]:
            cert_count += 1

    return JsonResponse({
        'total': total,
        'industry_count': industry_count,
        'location_count': location_count,
        'year_count': year_count,
        'minor_count': minor_count,
        'cert_count': cert_count,
    })