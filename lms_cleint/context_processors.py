from datetime import datetime

def greeting_context(request):
    current_hour = datetime.now().hour
    
    if 5 <= current_hour < 12:
        greeting = "Доброе утро"
    elif 12 <= current_hour < 18:
        greeting = "Добрый день"
    else:
        greeting = "Добрый вечер"
    
    return {'greeting': greeting}


def user_profile_info(request):
    """Безопасно проверяет наличие профилей пользователя"""
    has_student_profile = hasattr(request.user, 'studentprofile')
    has_teacher_profile = hasattr(request.user, 'teacherprofile')
    
    return {
        'has_student_profile': has_student_profile,
        'has_teacher_profile': has_teacher_profile,
        'is_student': has_student_profile,
        'is_teacher': has_teacher_profile,
        'user_profile': request.user.studentprofile if has_student_profile else 
                        (request.user.teacherprofile if has_teacher_profile else None)
    }