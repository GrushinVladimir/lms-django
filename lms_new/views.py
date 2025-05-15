from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import Course, Subject
from .forms import CourseForm, SubjectForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('course_list')
    else:
        form = AuthenticationForm()
    return render(request, 'elearning/login.html', {'form': form})

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'elearning/course_list.html', {'courses': courses})

@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'elearning/course_form.html', {'form': form})

@login_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'elearning/course_form.html', {'form': form})

@login_required
def subject_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    subjects = Subject.objects.filter(course=course)
    return render(request, 'elearning/subject_list.html', {'course': course, 'subjects': subjects})

@login_required
def subject_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.course = course
            subject.save()
            return redirect('subject_list', course_id=course.id)
    else:
        form = SubjectForm()
    return render(request, 'elearning/subject_form.html', {'form': form, 'course': course})

@login_required
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('subject_list', course_id=subject.course.id)
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'elearning/subject_form.html', {'form': form, 'course': subject.course})