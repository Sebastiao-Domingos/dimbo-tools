from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from apps.analytics.models import ConversionLog

@login_required
def index(request):
    user = request.user
    today = timezone.now().date()
    
    # Conversões dos últimos 7 dias (para o gráfico)
    seven_days_ago = today - timedelta(days=7)
    daily_stats = []
    for i in range(7):
        day = today - timedelta(days=i)
        count = user.conversions.filter(created_at__date=day).count()
        daily_stats.append({'day': day, 'count': count})
    daily_stats.reverse()  # ordem cronológica
    
    recent_conversions = user.conversions.all()[:10]
    total_conversions = user.conversions.count()
    today_conversions = user.conversions.filter(created_at__date=today).count()
    
    plan = getattr(user, 'plan', 'free')
    daily_limit = 5 if plan == 'free' else None
    remaining = (daily_limit - today_conversions) if daily_limit else 'Ilimitado'
    
    context = {
        'user': user,
        'today': today,
        'recent_conversions': recent_conversions,
        'total_conversions': total_conversions,
        'today_conversions': today_conversions,
        'daily_limit': daily_limit,
        'remaining': remaining,
        'plan': plan.capitalize(),
        'daily_stats': daily_stats,
    }
    return render(request, 'dashboard/index.html', context)