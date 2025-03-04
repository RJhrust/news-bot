from flask import Blueprint, render_template, request
from flask_login import login_required
from .models import BotStats, SearchQuery
from sqlalchemy import func, distinct
from datetime import datetime, timedelta
from . import limiter

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
@limiter.limit("60/minute")
def dashboard():
    # Статистика за последние 24 часа
    last_24h = datetime.utcnow() - timedelta(hours=24)
    
    # Общая статистика
    total_users = BotStats.query.with_entities(func.count(distinct(BotStats.user_id))).scalar()
    total_commands = BotStats.query.count()
    total_searches = SearchQuery.query.count()
    
    # Статистика команд
    command_stats = BotStats.query.with_entities(
        BotStats.command,
        func.count(BotStats.id)
    ).group_by(BotStats.command).all()
    
    # Последние поисковые запросы
    recent_searches = SearchQuery.query.order_by(SearchQuery.timestamp.desc()).limit(10).all()
    
    # Активность за последние 24 часа
    recent_activity = BotStats.query.filter(BotStats.timestamp >= last_24h).count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_commands=total_commands,
                         total_searches=total_searches,
                         command_stats=command_stats,
                         recent_searches=recent_searches,
                         recent_activity=recent_activity)

@admin_bp.route('/users')
@login_required
@limiter.limit("60/minute")
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users_pagination = BotStats.query.with_entities(
        BotStats.user_id,
        func.count(BotStats.id).label('command_count'),
        func.max(BotStats.timestamp).label('last_activity')
    ).group_by(BotStats.user_id).paginate(page=page, per_page=per_page)
    
    return render_template('admin/users.html', 
                         users=users_pagination.items,
                         pagination=users_pagination)

@admin_bp.route('/searches')
@login_required
@limiter.limit("60/minute")
def searches():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    searches_pagination = SearchQuery.query.order_by(
        SearchQuery.timestamp.desc()
    ).paginate(page=page, per_page=per_page)
    
    return render_template('admin/searches.html',
                         searches=searches_pagination.items,
                         pagination=searches_pagination) 