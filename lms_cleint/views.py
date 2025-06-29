from .decorators import teacher_required, student_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.forms import inlineformset_factory
from itertools import chain
from django.conf import settings
from lms_cleint.models import Course, Subject, Test, Question, Answer, TestResult, Chapter, ChapterFile, Article, Video,Link, TeacherProfile, StudentProfile, StudentGroup, Video,Link
from lms_cleint.forms import CourseForm, SubjectForm, TestForm, QuestionForm, ChapterForm, ChapterFileForm, ArticleForm, QuestionFormSet
import os
import json
import numpy as np
import logging
from lms_cleint.models import FileAnswer
from django.views.decorators.http import require_POST, require_GET

from django.db.models import Max, Avg
from django.contrib import messages
from django.utils import timezone

from lms_cleint.models import MaterialCompletion
from sentence_transformers import SentenceTransformer




from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey









logger = logging.getLogger(__name__)


@login_required
@student_required
@require_POST
def save_test_result(request, test_id):
    test = get_object_or_404(Test, pk=test_id)

    # Обновляем статус выполнения теста
    content_type = ContentType.objects.get_for_model(Test)
    MaterialCompletion.objects.get_or_create(
        user=request.user,
        content_type=content_type,
        object_id=test.id
    )

    # Обновляем прогресс
    files = ChapterFile.objects.filter(chapter=test.chapter)
    articles = Article.objects.filter(chapter=test.chapter)
    tests = Test.objects.filter(chapter=test.chapter)
    videos = Video.objects.filter(chapter=test.chapter)
    links = Link.objects.filter(chapter=test.chapter)

    file_ct = ContentType.objects.get_for_model(ChapterFile)
    article_ct = ContentType.objects.get_for_model(Article)
    test_ct = ContentType.objects.get_for_model(Test)
    video_ct = ContentType.objects.get_for_model(Video)
    link_ct = ContentType.objects.get_for_model(Link)

    completed = MaterialCompletion.objects.filter(
        user=request.user,
        content_type__in=[file_ct, article_ct, test_ct, video_ct, link_ct],
        object_id__in=[m.id for m in chain(files, articles, tests, videos, links)]
    ).values_list('content_type', 'object_id')

    completed_set = {(ct, obj_id) for ct, obj_id in completed}

    completed_count = sum(
        1 for m in chain(files, articles, tests, videos, links)
        if (ContentType.objects.get_for_model(m.__class__).id, m.id) in completed_set
    )

    total_materials = files.count() + articles.count() + tests.count() + videos.count() + links.count()
    progress = (completed_count / total_materials) * 100 if total_materials > 0 else 0

    messages.success(request, 'Результат теста успешно сохранен')
    return redirect('chapter_detail_student', chapter_id=test.chapter.id)


@login_required
def dashboard_full(request):
    # Получаем все тесты, связанные с преподавателем
    teacher_profile = request.user.teacherprofile
    tests = Test.objects.filter(chapter__subject__teachers=teacher_profile).distinct()

    return render(request, 'lms_cleint/dashboard_full.html', {
        'tests': tests
    })


@login_required
def test_users(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    results = TestResult.objects.filter(test=test).select_related('user')

    return render(request, 'lms_cleint/test_users.html', {
        'test': test,
        'results': results
    })

@require_POST
@login_required
@student_required
def complete_material(request, material_type, material_id):
    try:
        model_map = {
            'file': ChapterFile,
            'article': Article,
            'test': Test,
            'video': Video,
            'link': Link
        }
        
        if material_type not in model_map:
            return JsonResponse({'status': 'error', 'message': 'Неверный тип материала'}, status=400)
        
        model = model_map[material_type]
        material = get_object_or_404(model, pk=material_id)
        
        # Проверка доступа студента
        student_profile = get_object_or_404(StudentProfile, user=request.user)
        if not material.chapter.student_groups.filter(id=student_profile.group.id).exists():
            return JsonResponse({'status': 'error', 'message': 'Нет доступа к материалу'}, status=403)
        
        # Создаем отметку о выполнении
        content_type = ContentType.objects.get_for_model(model)
        MaterialCompletion.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=material.id
        )
        
        # Пересчитываем прогресс
        files = ChapterFile.objects.filter(chapter=material.chapter)
        articles = Article.objects.filter(chapter=material.chapter)
        tests = Test.objects.filter(chapter=material.chapter)
        videos = Video.objects.filter(chapter=material.chapter)
        links = Link.objects.filter(chapter=material.chapter)

        # Получаем ContentType для каждого типа
        file_ct = ContentType.objects.get_for_model(ChapterFile)
        article_ct = ContentType.objects.get_for_model(Article)
        test_ct = ContentType.objects.get_for_model(Test)
        video_ct = ContentType.objects.get_for_model(Video)
        link_ct = ContentType.objects.get_for_model(Link)

        # Получаем выполненные материалы для пользователя
        completed = MaterialCompletion.objects.filter(
            user=request.user,
            content_type__in=[file_ct, article_ct, test_ct, video_ct, link_ct],
            object_id__in=[m.id for m in chain(files, articles, tests, videos, links)]
        ).values_list('content_type', 'object_id')

        completed_set = {(ct, obj_id) for ct, obj_id in completed}
        
        completed_count = sum(
            1 for m in chain(files, articles, tests, videos, links)
            if (ContentType.objects.get_for_model(m.__class__).id, m.id) in completed_set
        )
        
        total_materials = files.count() + articles.count() + tests.count() + videos.count() + links.count()
        progress = (completed_count / total_materials) * 100 if total_materials > 0 else 0
        
        return JsonResponse({
            'status': 'success',
            'progress': progress,
            'material_id': material.id,
            'material_type': material_type
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_GET
@login_required
def get_progress(request):
    try:
        chapter_id = request.GET.get('chapter_id')

        if not chapter_id:
            return JsonResponse({'status': 'error', 'message': 'Chapter ID is required'}, status=400)

        # Get all materials for the chapter
        files = ChapterFile.objects.filter(chapter_id=chapter_id)
        articles = Article.objects.filter(chapter_id=chapter_id)
        tests = Test.objects.filter(chapter_id=chapter_id)
        videos = Video.objects.filter(chapter_id=chapter_id)
        links = Link.objects.filter(chapter_id=chapter_id)

        # Get ContentTypes for each material type
        file_ct = ContentType.objects.get_for_model(ChapterFile)
        article_ct = ContentType.objects.get_for_model(Article)
        test_ct = ContentType.objects.get_for_model(Test)
        video_ct = ContentType.objects.get_for_model(Video)
        link_ct = ContentType.objects.get_for_model(Link)

        # Get all completed materials for the user
        completed = MaterialCompletion.objects.filter(
            user=request.user,
            content_type__in=[file_ct, article_ct, test_ct, video_ct, link_ct],
            object_id__in=[m.id for m in chain(files, articles, tests, videos, links)]
        ).values_list('content_type', 'object_id')

        # Create a set of completed materials for faster lookup
        completed_set = {(ct, obj_id) for ct, obj_id in completed}

        # Count completed materials
        completed_count = 0
        total_materials = 0

        # Helper function to count materials
        def count_materials(materials, content_type):
            nonlocal completed_count, total_materials
            for material in materials:
                total_materials += 1
                if (content_type.id, material.id) in completed_set:
                    completed_count += 1

        # Count each type of material
        count_materials(files, file_ct)
        count_materials(articles, article_ct)
        count_materials(tests, test_ct)
        count_materials(videos, video_ct)
        count_materials(links, link_ct)

        # Calculate progress
        progress = (completed_count / total_materials) * 100 if total_materials > 0 else 0

        return JsonResponse({
            'status': 'success',
            'progress': progress,
            'completed': completed_count,
            'total': total_materials
        })
    except Exception as e:
        logger.error(f"Error calculating progress: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)




@login_required
def teacher_profile(request, teacher_id):
    teacher = get_object_or_404(TeacherProfile, pk=teacher_id)
    return render(request, 'lms_cleint/teacher_profile.html', {'teacher': teacher})



@login_required
def group_list(request, group_id):
    group = get_object_or_404(StudentGroup, pk=group_id)
    students = StudentProfile.objects.filter(group=group).select_related('user')
    logger.debug(f"Group: {group.group_number}, Students: {[student.user.get_full_name() for student in students]}")
    return render(request, 'lms_cleint/group_list.html', {'group': group, 'students': students})


@login_required
def student_profile(request, student_id):
    student = get_object_or_404(StudentProfile, pk=student_id)
    return render(request, 'lms_cleint/student_profile.html', {'student': student})


# Получение данных для редактирования
@login_required
def get_file_data(request, file_id):
    file = get_object_or_404(ChapterFile, pk=file_id)
    return JsonResponse({
        'display_name': file.display_name,
        'file_url': file.file.url if file.file else '',
        'file_name': file.file.name.split('/')[-1] if file.file else ''
    })

@login_required
def get_video_data(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    return JsonResponse({
        'title': video.title,
        'video_url': video.video_url or ''
    })

@login_required
def get_link_data(request, link_id):
    link = get_object_or_404(Link, pk=link_id)
    return JsonResponse({
        'title': link.title,
        'url': link.url
    })

# Обновление данных
@login_required
def update_file(request):
    if request.method == 'POST':
        try:
            file_id = request.POST.get('file_id')
            file = get_object_or_404(ChapterFile, pk=file_id)

            file.display_name = request.POST.get('display_name', file.display_name)

            if 'file' in request.FILES:
                file.file = request.FILES['file']

            file.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)




@login_required
def update_video(request):
    if request.method == 'POST':
        try:
            video_id = request.POST.get('video_id')
            video = get_object_or_404(Video, pk=video_id)

            video.title = request.POST.get('video_title', video.title)

            if 'video_file' in request.FILES:
                video.video_file = request.FILES['video_file']
                video.video_url = ''
            elif 'video_url' in request.POST and request.POST['video_url']:
                video.video_url = request.POST['video_url']
                video.video_file = None

            video.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def update_link(request):
    if request.method == 'POST':
        try:
            link_id = request.POST.get('link_id')
            link = get_object_or_404(Link, pk=link_id)

            link.title = request.POST.get('link_title', link.title)
            link.url = request.POST.get('link_url', link.url)

            link.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



@login_required
def upload_video(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    if request.method == 'POST':
        title = request.POST.get('video_title')
        video_file = request.FILES.get('video_file')
        video_url = request.POST.get('video_url')

        if not title:
            return JsonResponse({'status': 'error', 'message': 'Название видео обязательно'}, status=400)

        if not video_file and not video_url:
            return JsonResponse({'status': 'error', 'message': 'Необходимо загрузить видео или указать ссылку на YouTube'}, status=400)

        # Получаем все материалы главы для определения позиции
        files = ChapterFile.objects.filter(chapter=chapter)
        articles = Article.objects.filter(chapter=chapter)
        tests = Test.objects.filter(chapter=chapter)
        videos = Video.objects.filter(chapter=chapter)
        links = Link.objects.filter(chapter=chapter)

        # Находим максимальную позицию среди всех материалов
        max_position = max(
            max([f.position for f in files], default=0),
            max([a.position for a in articles], default=0),
            max([t.position for t in tests], default=0),
            max([v.position for v in videos], default=0),
            max([l.position for l in links], default=0)
        )

        # Создаем видео с новой позицией
        video = Video.objects.create(
            chapter=chapter,
            title=title,
            video_file=video_file,
            video_url=video_url,
            position=max_position + 1
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def add_link(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    if request.method == 'POST':
        title = request.POST.get('link_title')
        url = request.POST.get('link_url')

        if not title or not url:
            return JsonResponse({'status': 'error', 'message': 'Название и URL обязательны'}, status=400)

        # Получаем все материалы главы для определения позиции
        files = ChapterFile.objects.filter(chapter=chapter)
        articles = Article.objects.filter(chapter=chapter)
        tests = Test.objects.filter(chapter=chapter)
        videos = Video.objects.filter(chapter=chapter)
        links = Link.objects.filter(chapter=chapter)

        # Находим максимальную позицию среди всех материалов
        max_position = max(
            max([f.position for f in files], default=0),
            max([a.position for a in articles], default=0),
            max([t.position for t in tests], default=0),
            max([v.position for v in videos], default=0),
            max([l.position for l in links], default=0)
        )

        # Создаем ссылку с новой позицией
        link = Link.objects.create(
            chapter=chapter,
            title=title,
            url=url,
            position=max_position + 1
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



@login_required
def delete_video(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    chapter_id = video.chapter.id
    video.delete()
    messages.success(request, 'Видео успешно удалено')
    return redirect('chapter_detail', chapter_id=chapter_id)

@login_required
def delete_link(request, link_id):
    link = get_object_or_404(Link, pk=link_id)
    chapter_id = link.chapter.id
    link.delete()
    messages.success(request, 'Ссылка успешно удалена')
    return redirect('chapter_detail', chapter_id=chapter_id)



@require_GET
def get_groups_for_subject(request, course_id):
    course = Course.objects.get(pk=course_id)
    groups = course.student_groups.all()
    data = [{'id': group.id, 'name': group.group_number} for group in groups]
    return JsonResponse(data, safe=False)

@require_GET
def get_groups_for_chapter(request, subject_id):
    subject = Subject.objects.get(pk=subject_id)
    groups = subject.student_groups.all()
    data = [{'id': group.id, 'name': group.group_number} for group in groups]
    return JsonResponse(data, safe=False)

def view_test_result(request, result_id):
    result = get_object_or_404(TestResult, pk=result_id)
    test = result.test
    # Вычисляем количество попыток
    attempt_count = TestResult.objects.filter(user=request.user, test=test).count()

    # Вычисляем количество правильных и неправильных ответов
    correct_count = sum(1 for item in result.details['questions'] if item['is_correct'])
    incorrect_count = len(result.details['questions']) - correct_count
    correct_percent = (correct_count / len(result.details['questions'])) * 100 if result.details['questions'] else 0
    incorrect_percent = 100 - correct_percent

    passed = result.get_percentage() >= test.passing_score

    return render(request, 'lms_cleint/view_test_result.html', {
        'test': test,
        'result': result,
        'attempt_count': attempt_count,
        'correct_count': correct_count,
        'incorrect_count': incorrect_count,
        'correct_percent': correct_percent,
        'incorrect_percent': incorrect_percent,
        'passed': passed,
    })

#рефакторинг для ускорения запуска модели(вызываем, когда она необходима) Инициализация модели
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    return _model

def preprocess_text(text):
    """Нормализация текста перед сравнением"""
    if not text:
        return ""
    return text.lower().strip()

def check_text_similarity(user_answer, correct_answer):
    """Сравнение текстов с помощью SentenceTransformer"""
    model = get_model()
    try:
        emb_user = model.encode(user_answer)
        emb_correct = model.encode(correct_answer)
        similarity = np.dot(emb_user, emb_correct) / (np.linalg.norm(emb_user) * np.linalg.norm(emb_correct))
        return similarity
    except Exception as e:
        logger.error(f"Ошибка при сравнении текстов: {e}")
        return 0

def check_text_answer(user_answer, correct_answer, ai_check_enabled=True):
    """Проверка текстового ответа"""
    user_answer = preprocess_text(user_answer)
    correct_answer = preprocess_text(correct_answer)

    if not user_answer:
        return False

    # Если ответы полностью совпадают
    if user_answer == correct_answer:
        return True

    # Если AI проверка отключена
    if not ai_check_enabled:
        return False

    # Проверка с помощью SentenceTransformer
    similarity = check_text_similarity(user_answer, correct_answer)
    logger.debug(f"Сравнение: '{user_answer}' vs '{correct_answer}' - схожесть: {similarity:.2f}")

    # Подберите оптимальный порог для вашей предметной области
    return similarity > 0.60

    
@login_required
def submit_test(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    results = []
    total_score = 0

    if request.method == 'POST':
        for question in test.questions.all():
            question_data = {
                'question_id': question.id,
                'question_text': question.text,
                'is_correct': False,
                'score': 0
            }

            if question.question_type == 'text':
                user_answer = request.POST.get(f'question_{question.id}', '').strip()
                correct_answer_obj = question.answers.first()

                if correct_answer_obj:
                    is_correct = check_text_answer(
                        user_answer,
                        correct_answer_obj.text,
                        correct_answer_obj.ai_check_enabled
                    )
                    question_data.update({
                        'user_answer': user_answer,
                        'correct_answer': correct_answer_obj.text,
                        'is_correct': bool(is_correct),
                        'score': int(1 if is_correct else 0)
                    })
                else:
                    question_data.update({
                        'user_answer': user_answer,
                        'correct_answer': "",
                        'is_correct': False,
                        'score': 0
                    })
            else:
                selected_answers = []
                if question.question_type == 'single':
                    answer_id = request.POST.get(f'question_{question.id}')
                    if answer_id:
                        selected_answers.append(int(answer_id))
                else:
                    for answer in question.answers.all():
                        if request.POST.get(f'question_{question.id}_{answer.id}'):
                            selected_answers.append(answer.id)

                correct_answers = list(question.answers.filter(is_correct=True).values_list('id', flat=True))
                is_correct = set(selected_answers) == set(correct_answers)

                question_data.update({
                    'user_answer': selected_answers,
                    'correct_answer': correct_answers,
                    'is_correct': bool(is_correct),
                    'score': int(1 if is_correct else 0)
                })

            results.append(question_data)
            total_score += question_data['score']

        # Сохраняем результат теста
        test_result = TestResult.objects.create(
            user=request.user,
            test=test,
            score=total_score,
            max_score=test.questions.count(),
            details={'questions': results}
        )

        return redirect('test_result', test_id=test.id)

    return redirect('view_test', test_id=test.id)




@login_required
def test_result(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    result = TestResult.objects.filter(test=test, user=request.user).latest('submitted_at')

    # Получаем детали результатов
    questions_data = result.details.get('questions', [])

    correct_count = sum(1 for item in questions_data if item['is_correct'])
    incorrect_count = len(questions_data) - correct_count
    correct_percent = (correct_count / len(questions_data)) * 100 if questions_data else 0
    incorrect_percent = 100 - correct_percent

    return render(request, 'lms_cleint/view_test_result.html', {
        'test': test,
        'result': result,
        'passed': result.get_percentage() >= test.passing_score,
        'correct_count': correct_count,
        'incorrect_count': incorrect_count,
        'correct_percent': correct_percent,
        'incorrect_percent': incorrect_percent,
        'questions_data': questions_data
    })

@login_required
def teacher_dashboard(request):
    try:
        teacher_profile = request.user.teacherprofile
    except TeacherProfile.DoesNotExist:
        return HttpResponseForbidden("Доступ только для преподавателей")

    group_id = request.GET.get('group_id')
    tests = Test.objects.filter(chapter__subject__teachers=teacher_profile).distinct()

    # Получаем все группы, связанные с преподавателем
    groups = StudentGroup.objects.filter(subject__teachers=teacher_profile).distinct()

    # Получаем все файлы с ответами для преподавателя
    files_with_answers = ChapterFile.objects.filter(
        chapter__subject__teachers=teacher_profile,
        provide_answer=True
    ).exclude(file_answers__isnull=True).distinct().prefetch_related('file_answers')

    context = {
        'tests': tests,
        'groups': groups,
        'files_with_answers': files_with_answers
    }

    if group_id:
        group = get_object_or_404(StudentGroup, pk=group_id)
        context['selected_group'] = group

        # Фильтруем результаты по выбранной группе
        if 'test_id' in request.GET:
            test_id = request.GET.get('test_id')
            test = get_object_or_404(Test, pk=test_id, chapter__subject__teachers=teacher_profile)
            results = TestResult.objects.filter(test=test, user__studentprofile__group=group).select_related('user')

            avg_score = results.aggregate(avg=Avg('score'))['avg'] or 0
            pass_rate = results.filter(score__gte=test.passing_score).count() / results.count() * 100 if results.count() > 0 else 0
            attempt_count = results.count()

            question_stats = []
            for question in test.questions.all():
                correct_count = sum(1 for r in results if any(
                    q['question_id'] == question.id and q['is_correct']
                    for q in r.details['questions']
                ))
                question_stats.append({
                    'question': question,
                    'correct_rate': correct_count / results.count() * 100 if results.count() > 0 else 0
                })

            context.update({
                'test': test,
                'results': results,
                'avg_score': round(avg_score, 2),
                'pass_rate': round(pass_rate, 2),
                'attempt_count': attempt_count,
                'question_stats': sorted(question_stats, key=lambda x: x['correct_rate']),
                'selected_test': test
            })

    return render(request, 'lms_cleint/teacher_dashboard.html', context)





@login_required
@teacher_required
@require_POST
def grade_file_answer(request):
    try:
        answer_id = request.POST.get('answer_id')
        grade = int(request.POST.get('grade'))
        feedback = request.POST.get('feedback', '')
        
        if not (0 <= grade <= 10):
            raise ValueError("Оценка должна быть от 0 до 10")

        answer = get_object_or_404(
            FileAnswer, 
            pk=answer_id,
            chapter_file__chapter__subject__teachers=request.user.teacherprofile
        )

        answer.grade = grade
        answer.feedback = feedback
        answer.save()

        return JsonResponse({
            'status': 'success',
            'grade': grade,
            'feedback': feedback
        })
    except ValueError as e:
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': 'Произошла ошибка при сохранении оценки'},
            status=500
        )



@login_required
def edit_test(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    QuestionFormSet = inlineformset_factory(
        Test, Question, form=QuestionForm,
        extra=1, can_delete=True
    )

    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)
        question_formset = QuestionFormSet(request.POST, instance=test)

        if form.is_valid() and question_formset.is_valid():
            with transaction.atomic():
                test = form.save()
                questions = question_formset.save(commit=False)

                for i, question in enumerate(questions):
                    question.test = test
                    question.save()

                    # Handling answers
                    if question.question_type in ['single', 'multiple']:
                        # Delete old answers
                        question.answers.all().delete()

                        # Get all answers for this question
                        prefix = f'questions-{i}-answers'
                        answer_count = 0

                        while True:
                            text_key = f'{prefix}-{answer_count}-text'
                            is_correct_key = f'{prefix}-{answer_count}-is_correct'

                            if text_key not in request.POST:
                                break

                            answer_text = request.POST.get(text_key)
                            if answer_text:  # Check that the answer text is not empty
                                is_correct = request.POST.get(is_correct_key, 'false') == 'true'
                                Answer.objects.create(
                                    question=question,
                                    text=answer_text,
                                    is_correct=is_correct
                                )
                            answer_count += 1

                    elif question.question_type == 'text':
                        # Обработка текстового ответа
                        correct_answer_key = f'questions-{i}-correct_answer'
                        correct_answer = request.POST.get(correct_answer_key, '').strip()

                        if correct_answer:
                            Answer.objects.create(
                                question=question,
                                text=correct_answer,
                                is_correct=True
                            )

                # Delete marked questions
                for question in question_formset.deleted_objects:
                    question.delete()

                return redirect('chapter_detail', chapter_id=test.chapter.id)
        else:
            # Вывод ошибок валидации
            print("Form errors:", form.errors)
            print("Formset errors:", question_formset.errors)
    else:
        form = TestForm(instance=test)
        question_formset = QuestionFormSet(instance=test)

    return render(request, 'lms_cleint/test_edit.html', {
        'test': test,
        'form': form,
        'question_formset': question_formset
    })




@login_required
def create_test(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    if request.method == 'POST':
        form = TestForm(request.POST)
        question_formset = QuestionFormSet(request.POST, prefix='questions')

        if form.is_valid() and question_formset.is_valid():
            with transaction.atomic():
                test = form.save(commit=False)
                test.chapter = chapter

                # Получаем все материалы главы для определения позиции
                files = ChapterFile.objects.filter(chapter=chapter)
                articles = Article.objects.filter(chapter=chapter)
                tests = Test.objects.filter(chapter=chapter)
                videos = Video.objects.filter(chapter=chapter)
                links = Link.objects.filter(chapter=chapter)

                # Находим максимальную позицию среди всех материалов
                max_position = max(
                    max([f.position for f in files], default=0),
                    max([a.position for a in articles], default=0),
                    max([t.position for t in tests], default=0),
                    max([v.position for v in videos], default=0),
                    max([l.position for l in links], default=0)
                )

                test.position = max_position + 1
                test.save()

                # Остальной код создания теста
                for i, question_form in enumerate(question_formset):
                    if question_form.cleaned_data.get('DELETE', False):
                        continue

                    question = question_form.save(commit=False)
                    question.test = test
                    question.save()

                    # Обработка ответов
                    question_type = question.question_type

                    if question_type in ['single', 'multiple']:
                        answer_prefix = f'questions-{i}-answers'
                        answer_count = 0

                        while True:
                            text_key = f'{answer_prefix}-{answer_count}-text'
                            is_correct_key = f'{answer_prefix}-{answer_count}-is_correct'

                            if text_key not in request.POST:
                                break

                            answer_text = request.POST.get(text_key)
                            if answer_text:
                                is_correct = request.POST.get(is_correct_key, 'false') == 'true'
                                Answer.objects.create(
                                    question=question,
                                    text=answer_text,
                                    is_correct=is_correct
                                )
                            answer_count += 1

                    elif question_type == 'text':
                        correct_answer_key = f'questions-{i}-correct_answer'
                        correct_answer = request.POST.get(correct_answer_key, '').strip()

                        if correct_answer:
                            Answer.objects.create(
                                question=question,
                                text=correct_answer,
                                is_correct=True
                            )

                messages.success(request, 'Тест успешно создан')
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
    QuestionFormSet = inlineformset_factory(
        Test, Question, form=QuestionForm,
        extra=1, can_delete=True
    )

    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)
        question_formset = QuestionFormSet(request.POST, instance=test)

        if form.is_valid() and question_formset.is_valid():
            with transaction.atomic():
                test = form.save()
                questions = question_formset.save(commit=False)

                for question in questions:
                    question.test = test
                    question.save()

                    # Handling answers
                    if question.question_type in ['single', 'multiple']:
                        # Delete old answers
                        question.answers.all().delete()

                        # Get all answers for this question
                        prefix = f'questions-{question_formset.forms.index(question_formset.forms[questions.index(question)])}-answers'
                        answer_count = 0

                        while True:
                                text_key = f'{prefix}-{answer_count}-text'
                                is_correct_key = f'{prefix}-{answer_count}-is_correct'

                                if text_key not in request.POST:
                                    break

                                answer_text = request.POST.get(text_key)
                                if answer_text:  # Check that the answer text is not empty
                                    is_correct = request.POST.get(is_correct_key, 'false') == 'true'
                                    Answer.objects.create(
                                        question=question,
                                        text=answer_text,
                                        is_correct=is_correct
                                    )
                                answer_count += 1

                # Delete marked questions
                for question in question_formset.deleted_objects:
                    question.delete()
                messages.success(request, 'Тест успешно удален')
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
    messages.success(request, 'Тест успешно удален')

    return redirect('chapter_detail', chapter_id=chapter_id)

@login_required
def add_question(request, test_id):
    test = get_object_or_404(Test, pk=test_id)

    if request.method == 'POST':
        question_text = request.POST.get('text')
        question_type = request.POST.get('question_type')

        if question_text and question_type:
            question = Question.objects.create(
                test=test,
                text=question_text,
                question_type=question_type
            )

            # Handle answers only for questions with options
            if question_type in ['single', 'multiple']:
                answers = []
                # Collect all answer keys
                for key in request.POST:
                    if key.startswith('answers['):
                        # Example key: 'answers[0][text]'
                        parts = key.split('[')
                        index = parts[1].split(']')[0]
                        field = parts[2].split(']')[0]

                        # Create or get a dictionary for this answer
                        if index not in [a['index'] for a in answers]:
                            answers.append({'index': index})

                        # Find this answer in the list
                        answer = next(a for a in answers if a['index'] == index)
                        answer[field] = request.POST[key]

                # Create answers in the database
                for answer_data in answers:
                    if 'text' in answer_data and answer_data['text']:
                        Answer.objects.create(
                            question=question,
                            text=answer_data['text'],
                            is_correct=answer_data.get('is_correct', False) == 'on'
                        )

            return redirect('edit_test', test_id=test.id)

    return render(request, 'lms_cleint/question_form.html', {'test': test})

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    test_id = question.test.id
    question.delete()
    return redirect('edit_test', test_id=test_id)

# Обновленный обработчик порядка материалов


@csrf_exempt
@login_required
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
                        ChapterFile.objects.filter(id=file_id, chapter=chapter).update(position=index)
                    elif item_id.startswith('article_'):
                        article_id = item_id.replace('article_', '')
                        Article.objects.filter(id=article_id, chapter=chapter).update(position=index)
                    elif item_id.startswith('test_'):
                        test_id = item_id.replace('test_', '')
                        Test.objects.filter(id=test_id, chapter=chapter).update(position=index)
                    elif item_id.startswith('video_'):
                        video_id = item_id.replace('video_', '')
                        Video.objects.filter(id=video_id, chapter=chapter).update(position=index)
                    elif item_id.startswith('link_'):
                        link_id = item_id.replace('link_', '')
                        Link.objects.filter(id=link_id, chapter=chapter).update(position=index)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def edit_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статья успешно обновлена')
            return redirect('chapter_detail', chapter_id=article.chapter.id)
    else:
        form = ArticleForm(instance=article)
    
    return render(request, 'lms_cleint/article_form.html', {
        'form': form,
        'chapter': article.chapter
    })

@login_required
@teacher_required
def upload_file(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    
    if request.method == 'POST':
        form = ChapterFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = form.save(commit=False)
                file.chapter = chapter
                file.provide_answer = form.cleaned_data.get('provide_answer', False)
                
                # Получаем все материалы главы для определения позиции
                files = ChapterFile.objects.filter(chapter=chapter)
                articles = Article.objects.filter(chapter=chapter)
                tests = Test.objects.filter(chapter=chapter)
                videos = Video.objects.filter(chapter=chapter)
                links = Link.objects.filter(chapter=chapter)

                # Находим максимальную позицию среди всех материалов
                max_position = max(
                    max([f.position for f in files], default=0),
                    max([a.position for a in articles], default=0),
                    max([t.position for t in tests], default=0),
                    max([v.position for v in videos], default=0),
                    max([l.position for l in links], default=0)
                )

                file.position = max_position + 1
                file.save()

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'file_id': file.id})
                
                messages.success(request, 'Файл успешно загружен')
                return redirect('chapter_detail', chapter_id=chapter.id)
            
            except Exception as e:
                error_msg = f'Ошибка при загрузке файла: {str(e)}'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
                messages.error(request, error_msg)
                return redirect('chapter_detail', chapter_id=chapter.id)
        
        else:
            error_msg = 'Неверные данные формы'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': error_msg, 'errors': form.errors}, status=400)
            messages.error(request, error_msg)
            return redirect('chapter_detail', chapter_id=chapter.id)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    chapter_id = article.chapter.id
    article.delete()
    messages.success(request, 'Статья успешно удалена')
    return redirect('chapter_detail', chapter_id=chapter_id)

def save_uploaded_file(uploaded_file):
    # Create path for saving the file
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Save the file
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    # Return the file URL
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

            # Получаем все материалы главы для определения позиции
            files = ChapterFile.objects.filter(chapter=chapter)
            articles = Article.objects.filter(chapter=chapter)
            tests = Test.objects.filter(chapter=chapter)
            videos = Video.objects.filter(chapter=chapter)
            links = Link.objects.filter(chapter=chapter)

            # Находим максимальную позицию среди всех материалов
            max_position = max(
                max([f.position for f in files], default=0),
                max([a.position for a in articles], default=0),
                max([t.position for t in tests], default=0),
                max([v.position for v in videos], default=0),
                max([l.position for l in links], default=0)
            )

            article.position = max_position + 1
            article.save()
            messages.success(request, 'Статья успешно создана')
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
    chapters = Chapter.objects.filter(subject=subject).prefetch_related(
        'teachers',
        'student_groups'
    )
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
def redirect_to_chapter_view(request, chapter_id):
    """Перенаправляет на соответствующую view в зависимости от роли"""
    if hasattr(request.user, 'teacherprofile'):
        return redirect('chapter_detail', chapter_id=chapter_id)
    elif hasattr(request.user, 'studentprofile'):
        return redirect('chapter_detail_student', chapter_id=chapter_id)
    else:
        return HttpResponseForbidden("Доступ запрещен")
    


@login_required
@student_required
def chapter_detail_student(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    student_profile = get_object_or_404(StudentProfile, user=request.user)

    if not chapter.student_groups.filter(id=student_profile.group.id).exists():
        return HttpResponseForbidden("У вас нет доступа к этой главе")

    # Получаем все материалы главы
    files = ChapterFile.objects.filter(chapter=chapter).order_by('position')
    articles = Article.objects.filter(chapter=chapter).order_by('position')
    tests = Test.objects.filter(chapter=chapter).order_by('position')
    videos = Video.objects.filter(chapter=chapter).order_by('position')
    links = Link.objects.filter(chapter=chapter).order_by('position')  # Вот здесь получаем все ссылки

    # Получаем ContentType для каждого типа материала
    file_ct = ContentType.objects.get_for_model(ChapterFile)
    article_ct = ContentType.objects.get_for_model(Article)
    test_ct = ContentType.objects.get_for_model(Test)
    video_ct = ContentType.objects.get_for_model(Video)
    link_ct = ContentType.objects.get_for_model(Link)  # ContentType для ссылок

    # Получаем все отметки о выполнении для текущего пользователя
    completed_materials = MaterialCompletion.objects.filter(
        user=request.user,
        content_type__in=[file_ct, article_ct, test_ct, video_ct, link_ct],  # Включаем link_ct
        object_id__in=[m.id for m in chain(files, articles, tests, videos, links)]
    ).values_list('content_type', 'object_id')

    completed_set = {(ct, obj_id) for ct, obj_id in completed_materials}

    # Добавляем информацию о материалах
    all_materials = []
    for material in chain(files, articles, tests, videos, links):
        # Правильно определяем тип материала
        if isinstance(material, ChapterFile):
            material.material_type = 'file'
        elif isinstance(material, Article):
            material.material_type = 'article'
        elif isinstance(material, Test):
            material.material_type = 'test'
        elif isinstance(material, Video):
            material.material_type = 'video'
        elif isinstance(material, Link):
            material.material_type = 'link'
        
        # Получаем ContentType для текущего материала
        content_type = ContentType.objects.get_for_model(material.__class__)
        material.user_completed = (content_type.id, material.id) in completed_set
        
        all_materials.append(material)

    # Сортируем материалы по позиции
    all_materials.sort(key=lambda x: x.position)

    # Рассчитываем прогресс
    completed_count = sum(1 for m in all_materials if m.user_completed)
    progress = (completed_count / len(all_materials)) * 100 if all_materials else 0

    return render(request, 'lms_cleint/chapter_detail_student.html', {
        'chapter': chapter,
        'materials': all_materials,
        'progress': progress,
        'student': student_profile
    })


@require_POST
@login_required
@student_required
def complete_material(request, material_type, material_id):
    try:
        model_map = {
            'file': ChapterFile,
            'article': Article,
            'test': Test,
            'video': Video,
            'link': Link
        }
        
        if material_type not in model_map:
            return JsonResponse({'status': 'error', 'message': 'Неверный тип материала'}, status=400)
        
        model = model_map[material_type]
        material = get_object_or_404(model, pk=material_id)
        
        # Проверка доступа студента
        student_profile = get_object_or_404(StudentProfile, user=request.user)
        if not material.chapter.student_groups.filter(id=student_profile.group.id).exists():
            return JsonResponse({'status': 'error', 'message': 'Нет доступа к материалу'}, status=403)
        
        # Создаем отметку о выполнении
        content_type = ContentType.objects.get_for_model(model)
        MaterialCompletion.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=material.id
        )
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def chapter_detail(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    logger.debug(f"Loading chapter {chapter_id} for user {request.user}")

    if hasattr(request.user, 'teacherprofile'):
        teacher_profile = request.user.teacherprofile
        if not chapter.subject.teachers.filter(id=teacher_profile.id).exists():
            return HttpResponseForbidden("У вас нет доступа к этой главе")

        # Получаем все материалы
        files = ChapterFile.objects.filter(chapter=chapter).order_by('position')
        articles = Article.objects.filter(chapter=chapter).order_by('position')
        tests = Test.objects.filter(chapter=chapter).order_by('position')
        videos = Video.objects.filter(chapter=chapter).order_by('position')
        links = Link.objects.filter(chapter=chapter).order_by('position')

        # Объединяем материалы и добавляем информацию о типе материала
        materials = []
        for material in chain(files, articles, tests, videos, links):
            if isinstance(material, ChapterFile):
                material.material_type = 'file'
            else:
                material.material_type = material.__class__.__name__.lower()
            materials.append(material)

        # Сортируем материалы по позиции
        materials.sort(key=lambda x: x.position)

        logger.debug(f"Found {len(materials)} materials for chapter {chapter_id}")

        if request.method == 'POST':
            form = ChapterFileForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.save(commit=False)
                file.chapter = chapter
                file.provide_answer = form.cleaned_data['provide_answer']

                # Определяем новую позицию
                last_position = materials[-1].position if materials else 0
                file.position = last_position + 1

                file.save()

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'file_id': file.id})

                messages.success(request, 'Файл успешно загружен')
                return redirect('chapter_detail', chapter_id=chapter.id)
        else:
            form = ChapterFileForm()

        return render(request, 'lms_cleint/chapter_detail.html', {
            'chapter': chapter,
            'materials': materials,
            'form': form
        })

    elif hasattr(request.user, 'studentprofile'):
        return chapter_detail_student(request, chapter_id)

    return HttpResponseForbidden("Доступ запрещен")


def get_max_position(chapter):
    """Получает максимальную позицию среди всех материалов главы"""
    max_positions = [
        ChapterFile.objects.filter(chapter=chapter).aggregate(Max('position'))['position__max'] or 0,
        Article.objects.filter(chapter=chapter).aggregate(Max('position'))['position__max'] or 0,
        Test.objects.filter(chapter=chapter).aggregate(Max('position'))['position__max'] or 0,
        Video.objects.filter(chapter=chapter).aggregate(Max('position'))['position__max'] or 0,
        Link.objects.filter(chapter=chapter).aggregate(Max('position'))['position__max'] or 0
    ]
    return max(max_positions)

def get_materials_for_chapter(chapter, user):
    """Получает материалы главы с дополнительной информацией для пользователя"""
    files = ChapterFile.objects.filter(chapter=chapter).order_by('position')
    articles = Article.objects.filter(chapter=chapter).order_by('position')
    tests = Test.objects.filter(chapter=chapter).order_by('position')
    videos = Video.objects.filter(chapter=chapter).order_by('position')
    links = Link.objects.filter(chapter=chapter).order_by('position')

    # Добавляем информацию о типе материала и ответах пользователя
    for material in chain(files, articles, tests, videos, links):
        material.material_type = material.__class__.__name__.lower()
        
        if material.material_type == 'file' and user.is_student:
            material.user_answer = FileAnswer.objects.filter(
                chapter_file=material,
                student=user
            ).first()
    
    return sorted(chain(files, articles, tests, videos, links), key=lambda x: x.position)


@login_required
@student_required
@require_POST
def upload_answer(request):
    file_id = request.POST.get('file_id')
    answer_file = request.FILES.get('answer_file')

    if not file_id or not answer_file:
        return JsonResponse(
            {'status': 'error', 'message': 'Необходимо указать файл и ID файла'}, 
            status=400
        )

    chapter_file = get_object_or_404(ChapterFile, pk=file_id, provide_answer=True)
    
    # Проверка что студент имеет доступ к этому файлу
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    if not chapter_file.chapter.student_groups.filter(id=student_profile.group.id).exists():
        return JsonResponse(
            {'status': 'error', 'message': 'У вас нет доступа к этому файлу'},
            status=403
        )

    # Удаляем старый ответ если он есть
    FileAnswer.objects.filter(chapter_file=chapter_file, student=request.user).delete()

    # Создаем новый ответ
    try:
        file_answer = FileAnswer.objects.create(
            chapter_file=chapter_file,
            student=request.user,
            file=answer_file
        )
        
        file_name = os.path.basename(file_answer.file.name)
        return JsonResponse({
            'status': 'success',
            'file_name': file_name,
            'short_name': (file_name[:15] + '...') if len(file_name) > 15 else file_name,
            'answer_id': file_answer.id
        })
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=500
        )

@login_required
def delete_file(request, file_id):
    file = get_object_or_404(ChapterFile, pk=file_id)
    chapter_id = file.chapter.id
    file.delete()
    messages.success(request, 'Файл успешно удален')

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
def chapter_delete(request, chapter_id):
    chapter = get_object_or_404(Chapter, pk=chapter_id)
    subject_id = chapter.subject.id
    chapter.delete()
    return redirect('chapter_list', subject_id=subject_id)

@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    course.delete()
    return redirect('course_list')

@login_required
def subject_delete(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    course_id = subject.course.id
    subject.delete()
    return redirect('subject_list', course_id=course_id)

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
            form.save_m2m()  # Сохраняем связанные объекты
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