from django import template
from django.urls import resolve, Resolver404
from django.utils.text import capfirst
from django.apps import apps

register = template.Library()


@register.simple_tag(takes_context=True)
def dynamic_breadcrumbs(context):
    request = context['request']
    breadcrumbs = [{'title': 'Главная', 'url': '/'}]
    
    # Словарь для перевода стандартных URL-имен в читаемые названия
    VIEW_NAME_TRANSLATIONS = {
        'course_list': 'Дисциплины',
        'student_profile': 'Профиль студента',
        'teacher_profile': 'Профиль преподавателя',
        'group_list' : 'Группа', 
        'notifications' : 'Уведомления'}
    
    try:
        resolver_match = resolve(request.path_info)
        url_name = resolver_match.url_name
        url_kwargs = resolver_match.kwargs
        
        # Обработка специальных случаев (профили)
        if url_name in ['student_profile', 'student_detail', 'teacher_profile', 'teacher_detail']:
            breadcrumbs.append({
                'title': VIEW_NAME_TRANSLATIONS.get(url_name, 'Профиль'),
                'url': request.path
            })
            return breadcrumbs
        
        # Анализируем параметры URL
        for param, value in url_kwargs.items():
            if param.endswith('_id'):
                model_name = param[:-3].capitalize()
                
                # Специальные случаи
                if model_name == 'Chapter':
                    model_name = 'Chapter'
                elif model_name == 'Student':
                    model_name = 'StudentProfile'
                elif model_name == 'Teacher':
                    model_name = 'TeacherProfile'
                
                try:
                    model = apps.get_model('lms_cleint', model_name)
                    obj = model.objects.get(pk=value)
                    
                    # Пропускаем добавление группы студента в хлебные крошки
                    if model_name == 'StudentProfile' and param == 'student_id':
                        continue
                        
                    breadcrumbs.append({
                        'title': str(obj),
                        'url': request.path if param == list(url_kwargs.keys())[-1] else ''
                    })
                except:
                    continue
        
        # Добавляем текущий view с переводом, если не добавлен через параметры
        if len(breadcrumbs) == 1:  # Только "Главная"
            view_name = VIEW_NAME_TRANSLATIONS.get(
                resolver_match.url_name,
                resolver_match.url_name.replace('_', ' ').title()
            )
            breadcrumbs.append({'title': view_name, 'url': ''})
    
    except (Resolver404, Exception) as e:
        pass
    
    return breadcrumbs