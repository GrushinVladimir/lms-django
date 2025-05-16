from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from lms_cleint.models import Course, Subject
from lms_cleint.forms import CourseForm, SubjectForm, TestForm, QuestionForm, AnswerForm, AnswerFormSet
from django.contrib.auth import logout
from .models import Chapter, ChapterFile, Article
from .forms import ChapterForm, ChapterFileForm, ArticleForm,Test, Question, Answer,QuestionFormSet
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os
from django.db import transaction
import json 
from django.forms import inlineformset_factory
from itertools import chain

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('edit_test', test_id=question.test.id)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)
    
    return render(request, 'lms_cleint/question_edit.html', {
        'question': question,
        'form': form,
        'formset': formset,
        'test': question.test
    })

@login_required
def submit_test(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    
    if request.method == 'POST':
        # Здесь будет логика обработки ответов
        # Пока просто редиректим обратно к тесту
        return redirect('view_test', test_id=test.id)
    
    return redirect('view_test', test_id=test.id)

@login_required
def create_test(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    if request.method == 'POST':
        form = TestForm(request.POST)
        question_formset = QuestionFormSet(request.POST, prefix='questions')
        
        if form.is_valid() and question_formset.is_valid():
            test = form.save(commit=False)
            test.chapter = chapter
            test.save()
            
            questions = question_formset.save(commit=False)
            for question in questions:
                question.test = test
                question.save()
                
                # Обработка ответов
                if question.question_type in ['single', 'multiple']:
                    answer_prefix = f'answers-{question.id}-'
                    answers_data = {}
                    
                    # Собираем данные ответов
                    for key, value in request.POST.items():
                        if key.startswith(answer_prefix):
                            parts = key.replace(answer_prefix, '').split('-')
                            index = parts[0]
                            field = parts[1] if len(parts) > 1 else 'text'
                            
                            if index not in answers_data:
                                answers_data[index] = {'is_correct': False}
                            
                            if field == 'text':
                                answers_data[index]['text'] = value
                            elif field == 'correct':
                                if question.question_type == 'single':
                                    answers_data[index]['is_correct'] = (value == index)
                                else:
                                    answers_data[index]['is_correct'] = True
                    
                    # Создаем ответы
                    for answer_data in answers_data.values():
                        if 'text' in answer_data:
                            Answer.objects.create(
                                question=question,
                                text=answer_data['text'],
                                is_correct=answer_data['is_correct']
                            )
            
            return redirect('chapter_detail', chapter_id=chapter.id)
    else:
        form = TestForm()
        question_formset = QuestionFormSet(prefix='questions', queryset=Question.objects.none())
    
    return render(request, 'lms_cleint/test_create.html', {
        'form': form,
        'question_formset': question_formset,
        'chapter': chapter
    })

@login_required
def view_test(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    return render(request, 'lms_cleint/test_view.html', {
        'test': test
    })
@login_required
def edit_test(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)
        question_formset = QuestionFormSet(request.POST, instance=test)
        
        if form.is_valid() and question_formset.is_valid():
            form.save()
            questions = question_formset.save(commit=False)
            
            for question in questions:
                question.test = test
                question.save()
                
            question_formset.save_m2m()
            
            for question in question_formset.deleted_objects:
                question.delete()
                
            return redirect('chapter_detail', chapter_id=test.chapter.id)
    else:
        form = TestForm(instance=test)
        question_formset = QuestionFormSet(instance=test)
    
    return render(request, 'lms_cleint/test_edit.html', {
        'test': test,
        'form': form,
        'question_formset': question_formset
    })

@login_required
def delete_test(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    chapter_id = test.chapter.id
    test.delete()
    return redirect('chapter_detail', chapter_id=chapter_id)

@login_required
def add_question(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.test = test
            question.position = Question.objects.filter(test=test).count() + 1
            question.save()
            
            # Обработка ответов для вопросов с вариантами
            if question.question_type in ['single', 'multiple']:
                answers_data = {}
                
                # Собираем данные ответов из POST-запроса
                for key, value in request.POST.items():
                    if key.startswith('answers['):
                        parts = key.split('[')
                        index = int(parts[1].split(']')[0])
                        field = parts[2].split(']')[0]
                        
                        if index not in answers_data:
                            answers_data[index] = {}
                        answers_data[index][field] = value
                
                # Создаем ответы
                for answer_data in answers_data.values():
                    answer = Answer(
                        question=question,
                        text=answer_data.get('text', ''),
                        is_correct=answer_data.get('is_correct', False) == 'on',
                        position=len(question.answers.all()) + 1
                    )
                    answer.save()
            
            return redirect('edit_test', test_id=test.id)
    else:
        form = QuestionForm()
    
    return render(request, 'lms_cleint/question_form.html', {
        'test': test,
        'form': form
    })

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    AnswerFormSet = inlineformset_factory(
        Question, Answer, form=AnswerForm,
        extra=1, can_delete=True
    )
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('edit_test', test_id=question.test.id)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)
    
    return render(request, 'lms_cleint/question_edit.html', {
        'question': question,
        'form': form,
        'formset': formset,
        'test': question.test
    })

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    test_id = question.test.id
    question.delete()
    return redirect('edit_test', test_id=test_id)

@csrf_exempt
def update_materials_order(request, chapter_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = data.get('order', [])
            chapter = get_object_or_404(Chapter, pk=chapter_id)

            with transaction.atomic():
                for index, item_id in enumerate(order, start=1):
                    if item_id.startswith('file_'):
                        file_id = item_id.replace('file_', '')
                        ChapterFile.objects.filter(
                            id=file_id, 
                            chapter=chapter
                        ).update(position=index)
                    elif item_id.startswith('article_'):
                        article_id = item_id.replace('article_', '')
                        Article.objects.filter(
                            id=article_id, 
                            chapter=chapter
                        ).update(position=index)
                    elif item_id.startswith('test_'):
                        test_id = item_id.replace('test_', '')
                        Test.objects.filter(
                            id=test_id, 
                            chapter=chapter
                        ).update(position=index)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)}, 
                status=400
            )
    return JsonResponse({'status': 'error'}, status=400)



@login_required
def edit_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return redirect('chapter_detail', chapter_id=article.chapter.id)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'lms_cleint/article_form.html', {
        'form': form,
        'chapter': article.chapter
    })

@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    chapter_id = article.chapter.id
    article.delete()
    return redirect('chapter_detail', chapter_id=chapter_id)




def save_uploaded_file(uploaded_file):
    # Создаем путь для сохранения файла
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Сохраняем файл
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    # Возвращаем URL файла
    return os.path.join(settings.MEDIA_URL, 'uploads', uploaded_file.name)


@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_url = save_uploaded_file(uploaded_file)
        return JsonResponse({'location': file_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def create_article(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.chapter = chapter
            # Получаем последний материал в главе и устанавливаем позицию
            last_material = Article.objects.filter(chapter=chapter).order_by('-position').first()
            article.position = last_material.position + 1 if last_material else 1
            article.save()
            return redirect('chapter_detail', chapter_id=chapter.id)
    else:
        form = ArticleForm()
    return render(request, 'lms_cleint/article_form.html', {
        'form': form,
        'chapter': chapter
    })


@login_required
def article_detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'lms_cleint/article_detail.html', {
        'article': article
    })


@login_required
def chapter_list(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    chapters = Chapter.objects.filter(subject=subject).prefetch_related('teachers', 'student_groups')
    return render(request, 'lms_cleint/chapter_list.html', {
        'subject': subject,
        'chapters': chapters
    })

@login_required
def chapter_create(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.method == 'POST':
        form = ChapterForm(request.POST, subject_id=subject_id)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.subject = subject
            chapter.save()
            form.save_m2m()
            return redirect('chapter_list', subject_id=subject.id)
    else:
        form = ChapterForm(subject_id=subject_id)
    return render(request, 'lms_cleint/chapter_form.html', {'form': form, 'subject': subject})


@login_required
def chapter_detail(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    files = ChapterFile.objects.filter(chapter=chapter).order_by('position')
    articles = Article.objects.filter(chapter=chapter).order_by('position')
    tests = Test.objects.filter(chapter=chapter).order_by('position')

    # Добавляем material_type к каждому объекту
    for f in files:
        f.material_type = 'file'
    for a in articles:
        a.material_type = 'article'
    for t in tests:
        t.material_type = 'test'

    # Объединяем и сортируем
    materials = sorted(
        chain(files, articles, tests),
        key=lambda x: x.position
    )

    if request.method == 'POST':
        form = ChapterFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.chapter = chapter
            file.position = materials[-1].position + 1 if materials else 1
            file.save()
            return redirect('chapter_detail', chapter_id=chapter.id)
    else:
        form = ChapterFileForm()

    return render(request, 'lms_cleint/chapter_detail.html', {
        'chapter': chapter,
        'materials': materials,
        'form': form
    })

@login_required
def delete_file(request, file_id):
    file = get_object_or_404(ChapterFile, pk=file_id)
    chapter_id = file.chapter.id
    file.delete()
    return redirect('chapter_detail', chapter_id=chapter_id)
def custom_logout(request):
    logout(request)
    return redirect('login')

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
    return render(request, 'lms_cleint/login.html', {'form': form})

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'lms_cleint/course_list.html', {'courses': courses})


@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'lms_cleint/course_form.html', {'form': form})

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
    return render(request, 'lms_cleint/course_form.html', {'form': form})

@login_required
def subject_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    subjects = Subject.objects.filter(course=course).prefetch_related('teachers', 'student_groups')
    return render(request, 'lms_cleint/subject_list.html', {
        'course': course,
        'subjects': subjects
    })

@login_required
def subject_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, course_id=course_id)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.course = course
            subject.save()
            return redirect('subject_list', course_id=course.id)
    else:
        form = SubjectForm(course_id=course_id)
    return render(request, 'lms_cleint/subject_form.html', {'form': form, 'course': course})

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
    return render(request, 'lms_cleint/subject_form.html', {'form': form, 'course': subject.course})