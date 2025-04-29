from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import *
from .forms import *

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

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    courses = Course.objects.all()  # Все курсы без фильтрации
    context = {
        'courses': courses,
        'is_teacher': True
    }
    return render(request, 'teacher/dashboard.html', context)

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

@login_required
@user_passes_test(is_teacher)
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = Module.objects.filter(course=course)
    context = {
        'course': course,
        'modules': modules
    }
    return render(request, 'teacher/course_detail.html', context)

@login_required
@user_passes_test(is_teacher)
def module_detail(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    materials = Material.objects.filter(module=module)
    context = {
        'module': module,
        'materials': materials
    }
    return render(request, 'teacher/module_detail.html', context)

@login_required
@user_passes_test(is_teacher)
def material_detail(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    context = {
        'material': material
    }
    return render(request, 'teacher/material_detail.html', context)

@login_required
@user_passes_test(is_teacher)
def create_material(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.module = module
            material.save()
            return redirect('module_detail', module_id=module.id)
    else:
        form = MaterialForm()
    context = {
        'form': form,
        'module': module
    }
    return render(request, 'teacher/create_material.html', context)

@login_required
@user_passes_test(is_teacher)
def edit_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            return redirect('material_detail', material_id=material.id)
    else:
        form = MaterialForm(instance=material)
    context = {
        'form': form,
        'material': material
    }
    return render(request, 'teacher/edit_material.html', context)

@login_required
@user_passes_test(is_teacher)
def delete_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    module_id = material.module.id
    material.delete()
    return redirect('module_detail', module_id=module_id)

@login_required
@user_passes_test(is_teacher)
def create_assignment(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.material = material
            assignment.save()
            return redirect('material_detail', material_id=material.id)
    else:
        form = AssignmentForm()
    context = {
        'form': form,
        'material': material
    }
    return render(request, 'teacher/create_assignment.html', context)

@login_required
@user_passes_test(is_teacher)
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            return redirect('material_detail', material_id=assignment.material.id)
    else:
        form = AssignmentForm(instance=assignment)
    context = {
        'form': form,
        'assignment': assignment
    }
    return render(request, 'teacher/edit_assignment.html', context)

@login_required
@user_passes_test(is_teacher)
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    material_id = assignment.material.id
    assignment.delete()
    return redirect('material_detail', material_id=material_id)

@login_required
@user_passes_test(is_teacher)
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.submission = submission
            grade.assignment = submission.assignment
            grade.student = submission.student
            grade.graded_by = request.user
            grade.graded_at = timezone.now()
            grade.save()
            return redirect('submission_detail', submission_id=submission.id)
    else:
        form = GradeForm()
    context = {
        'form': form,
        'submission': submission
    }
    return render(request, 'teacher/grade_submission.html', context)

@login_required
@user_passes_test(is_student)
def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    context = {
        'submission': submission
    }
    return render(request, 'student/submission_detail.html', context)

@login_required
@user_passes_test(is_student)
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            return redirect('submission_detail', submission_id=submission.id)
    else:
        form = SubmissionForm()
    context = {
        'form': form,
        'assignment': assignment
    }
    return render(request, 'student/submit_assignment.html', context)

@login_required
def chat_detail(request, course_id, student_id):
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(User, id=student_id)
    chat, created = Chat.objects.get_or_create(course=course, student=student, teacher=request.user)
    messages = Message.objects.filter(chat=chat).order_by('sent_at')
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.sender = request.user
            message.save()
            return redirect('chat_detail', course_id=course.id, student_id=student.id)
    else:
        form = MessageForm()
    context = {
        'chat': chat,
        'messages': messages,
        'form': form
    }
    return render(request, 'chat_detail.html', context)

@login_required
@user_passes_test(is_teacher)
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            # Убедитесь, что у пользователя есть группы
            if hasattr(request.user, 'userprofiles'):
                for group in request.user.userprofiles.student_group.all():
                    CourseAccess.objects.create(
                        course=course, 
                        group=group, 
                        access_type='edit', 
                        granted_by=request.user
                    )
            return redirect('teacher_dashboard')
    else:
        form = CourseForm()
    context = {
        'form': form
    }
    return render(request, 'teacher/create_course.html', context)

@login_required
@user_passes_test(is_teacher)
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)
    context = {
        'form': form,
        'course': course
    }
    return render(request, 'teacher/edit_course.html', context)

@login_required
@user_passes_test(is_teacher)
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return redirect('teacher_dashboard')

@login_required
@user_passes_test(is_teacher)
def create_module(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = ModuleForm()
    context = {
        'form': form,
        'course': course
    }
    return render(request, 'teacher/create_module.html', context)

@login_required
@user_passes_test(is_teacher)
def edit_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            return redirect('module_detail', module_id=module.id)
    else:
        form = ModuleForm(instance=module)
    context = {
        'form': form,
        'module': module
    }
    return render(request, 'teacher/edit_module.html', context)

@login_required
@user_passes_test(is_teacher)
def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    course_id = module.course.id
    module.delete()
    return redirect('course_detail', course_id=course_id)
