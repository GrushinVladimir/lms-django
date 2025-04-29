from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *

# Проверка на группы пользователя
def is_teacher(user):
    return user.is_authenticated and (
        user.is_superuser or
        user.groups.filter(name='Преподаватель').exists() or
        (hasattr(user, 'userprofiles') and user.userprofiles.user_type == 'teacher')
    )
def is_student(user):
    return user.is_authenticated and not user.is_superuser and (
        user.groups.filter(name='Студент').exists() or
        (hasattr(user, 'userprofiles') and user.userprofiles.user_type == 'student')
    )
def is_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
def home(request):
    if is_admin(request.user):
        return redirect('admin:index')
    elif is_teacher(request.user):
        return teacher_dashboard(request)
    elif is_student(request.user):
        return student_dashboard(request)
    return render(request, 'base.html')


# Авторизация - перенаправление ПРЕПОДАВАТЕЛИ
@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    # Получаем курсы, к которым у преподавателя есть доступ
    courses = Course.objects.filter(
        courseaccess__group__in=request.user.userprofiles.student_group.all(),
        courseaccess__revoked_at__isnull=True
    ).distinct()

    context = {
        'courses': courses,
        'is_teacher': True
    }
    return render(request, 'teacher/dashboard.html', context)


# Авторизация - перенаправление СТУДЕНТЫ
@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    # Получаем профиль пользователя (создастся автоматически если не существует)
    profile, created = UserProfiles.objects.get_or_create(user=request.user)

    student_groups = profile.student_group.all()
    courses = Course.objects.filter(
        courseaccess__group__in=student_groups,
        courseaccess__revoked_at__isnull=True
    ).distinct()

    context = {
        'courses': courses,
        'is_student': True
    }
    return render(request, 'student/dashboard.html', context)
