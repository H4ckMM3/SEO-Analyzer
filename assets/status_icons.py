"""
Иконки статусов для SEO Автотестера Pro
"""

from flet import Icons

# Иконки для различных статусов
STATUS_ICONS = {
    'success': Icons.CHECK_CIRCLE,
    'error': Icons.ERROR,
    'warning': Icons.WARNING,
    'info': Icons.INFO,
    'loading': Icons.HOURGLASS_EMPTY,
    'ok': Icons.CHECK_CIRCLE,
    'failed': Icons.CANCEL,
    'pending': Icons.SCHEDULE,
    'seo': Icons.SEARCH,
    'speed': Icons.SPEED,
    'security': Icons.SECURITY,
    'mobile': Icons.PHONE_ANDROID,
    'desktop': Icons.DESKTOP_WINDOWS,
    'link': Icons.LINK,
    'broken_link': Icons.LINK_OFF,
    'redirect': Icons.REDIRECT,
    'duplicate': Icons.CONTENT_COPY,
    'missing': Icons.MISSING_AV,
    'optimized': Icons.TRENDING_UP,
    'not_optimized': Icons.TRENDING_DOWN,
    'high_priority': Icons.PRIORITY_HIGH,
    'medium_priority': Icons.PRIORITY_HIGH,
    'low_priority': Icons.PRIORITY_LOW,
    'score_a': Icons.STAR,
    'score_b': Icons.STAR_HALF,
    'score_c': Icons.STAR_BORDER,
    'score_d': Icons.STAR_BORDER,
    'score_f': Icons.STAR_BORDER,
}

# Цвета для различных статусов
STATUS_COLORS = {
    'success': '#4CAF50',  # Зеленый
    'error': '#F44336',    # Красный
    'warning': '#FF9800',  # Оранжевый
    'info': '#2196F3',     # Синий
    'loading': '#9E9E9E',  # Серый
    'ok': '#4CAF50',       # Зеленый
    'failed': '#F44336',   # Красный
    'pending': '#FF9800',  # Оранжевый
    'seo': '#FFC107',      # Желтый
    'speed': '#00BCD4',    # Голубой
    'security': '#9C27B0', # Фиолетовый
    'mobile': '#3F51B5',   # Индиго
    'desktop': '#607D8B',  # Сине-серый
    'link': '#4CAF50',     # Зеленый
    'broken_link': '#F44336', # Красный
    'redirect': '#FF9800', # Оранжевый
    'duplicate': '#9C27B0', # Фиолетовый
    'missing': '#F44336',  # Красный
    'optimized': '#4CAF50', # Зеленый
    'not_optimized': '#F44336', # Красный
    'high_priority': '#F44336', # Красный
    'medium_priority': '#FF9800', # Оранжевый
    'low_priority': '#4CAF50', # Зеленый
    'score_a': '#4CAF50',  # Зеленый
    'score_b': '#8BC34A',  # Светло-зеленый
    'score_c': '#FFC107',  # Желтый
    'score_d': '#FF9800',  # Оранжевый
    'score_f': '#F44336',  # Красный
}

def get_status_icon(status, size=20):
    """Возвращает иконку статуса с соответствующим цветом."""
    from flet import Icon
    
    icon_name = STATUS_ICONS.get(status.lower(), Icons.HELP)
    color = STATUS_COLORS.get(status.lower(), '#9E9E9E')
    
    return Icon(
        name=icon_name,
        color=color,
        size=size,
        tooltip=status
    )

def get_status_color(status):
    """Возвращает цвет для статуса."""
    return STATUS_COLORS.get(status.lower(), '#9E9E9E')

def get_status_icon_name(status):
    """Возвращает имя иконки для статуса."""
    return STATUS_ICONS.get(status.lower(), Icons.HELP) 