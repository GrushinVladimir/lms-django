from django.http import HttpResponseForbidden

def student_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Требуется авторизация")
        if not hasattr(request.user, 'studentprofile'):
            return HttpResponseForbidden("Доступ только для студентов")
        return view_func(request, *args, **kwargs)
    return wrapped_view

def teacher_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Требуется авторизация")
        if not hasattr(request.user, 'teacherprofile'):
            return HttpResponseForbidden("Доступ только для преподавателей")
        return view_func(request, *args, **kwargs)
    return wrapped_view