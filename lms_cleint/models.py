from django.db import models
from django.contrib.auth.models import AbstractUser
from tinymce.models import HTMLField
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class CustomUser(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

class StudentGroup(models.Model):
    group_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.group_number



class TeacherProfile(models.Model):
    CATEGORY_CHOICES = [
        ('1', 'Первая категория'),
        ('2', 'Вторая категория'),
        ('h', 'Высшая категория'),
        ('n', 'Без категории'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default='n')
    position = models.CharField(max_length=100)
    classroom = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    avatar = models.ImageField(upload_to='avatars_pre/', blank=True, null=True)

    def __str__(self):
        initials = f"{self.first_name[0]}.{self.middle_name[0]}." if self.middle_name else f"{self.first_name[0]}."
        return f"{self.last_name} {initials}"
    
    def generate_avatar_circle_pre(self):
        if self.last_name and self.first_name:
            initials = f"{self.last_name[0]}{self.first_name[0]}"
            return initials.upper()
        return "NN"

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(StudentGroup, on_delete=models.SET_NULL, null=True, blank=True)
    record_book_number = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.group})"

    def generate_avatar_circle(self):
        if self.last_name and self.first_name:
            initials = f"{self.last_name[0]}{self.first_name[0]}"
            return initials.upper()
        return "NN"
    

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_student:
            StudentProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'studentprofile'):
        instance.studentprofile.save()
    elif hasattr(instance, 'teacherprofile'):
        instance.teacherprofile.save()

class Course(models.Model):
    name = models.CharField(max_length=200)
    teachers = models.ManyToManyField(TeacherProfile)
    student_groups = models.ManyToManyField(StudentGroup)
    @property
    def teachers_display(self):
        return ", ".join([f"{t.last_name} {t.first_name[0]}." for t in self.teachers.all()])

    @property
    def groups_display(self):
        return ", ".join([g.group_number for g in self.student_groups.all()])
    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teachers = models.ManyToManyField(TeacherProfile)
    student_groups = models.ManyToManyField(StudentGroup)
    @property
    def teachers_display(self):
        return ", ".join([f"{t.last_name} {t.first_name[0]}." for t in self.teachers.all()])

    @property
    def groups_display(self):
        return ", ".join([g.group_number for g in self.student_groups.all()])
    def __str__(self):
        return self.name

class Chapter(models.Model):
    name = models.CharField(max_length=120)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teachers = models.ManyToManyField(TeacherProfile)
    student_groups = models.ManyToManyField(StudentGroup)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def teachers_display(self):
        return ", ".join([f"{t.last_name} {t.first_name[0]}." for t in self.teachers.all()])
    @property
    def teachers_display(self):
        return ", ".join([f"{t.last_name} {t.first_name[0]}." for t in self.teachers.all()])
    def __str__(self):
        return self.name


class ChapterFile(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    file = models.FileField(upload_to='chapter_files/')
    display_name = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    provide_answer = models.BooleanField(default=False)

    completed_by = models.ManyToManyField(
        CustomUser,
        through='FileCompletion',
        related_name='completed_files'
    )
    @property
    def safe_display_name(self):
        if self.display_name:
            return self.display_name
        if self.file and hasattr(self.file, 'name'):
            return os.path.basename(self.file.name)
        return "Без названия"
    @property
    def answer_file_name(self):
        # Используем related_name из FileAnswer для доступа к связанным ответам
        if hasattr(self, 'answers') and self.answers.exists():
            filename = os.path.basename(self.answers.first().file.name)
            if len(filename) > 15:
                return f"{filename[:7]}...{filename[-7:]}"
            return filename
        return None
    def get_display_name(self):
        return self.display_name or os.path.basename(self.file.name)

    def file_extension(self):
        return self.file.name.split('.')[-1].lower()

    def is_pdf(self):
        return self.file_extension() == 'pdf'

    def is_word(self):
        return self.file_extension() in ['doc', 'docx']

    def is_ppt(self):
        return self.file_extension() in ['ppt', 'pptx']


class FileCompletion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.ForeignKey(ChapterFile, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

class MaterialCompletion(models.Model):
    """Общая модель для отметки о выполнении любых материалов"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', 'content_type', 'object_id']),
        ]
        unique_together = ('user', 'content_type', 'object_id')


class Article(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = HTMLField(verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    position = models.PositiveIntegerField(default=0)  # Добавляем поле позиции
    completed = models.BooleanField(default=False)  # Добавляем поле completed
    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.title

class Test(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='tests')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    passing_score = models.IntegerField(default=70, help_text="Минимальный процент для зачета")
    completed = models.BooleanField(default=False)  # Добавляем поле completed

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.title

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=[
            ('single', 'Один правильный ответ'),
            ('multiple', 'Несколько правильных ответов'),
            ('text', 'Текстовый ответ')
        ],
        default='single'
    )
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{self.text[:50]}..."

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    ai_check_enabled = models.BooleanField(default=True, help_text="Использовать AI для проверки текстовых ответов")


    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{self.text[:50]}..."

class TestResult(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    test = models.ForeignKey('Test', on_delete=models.CASCADE)
    score = models.FloatField()
    max_score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField()  # Детализированные результаты

    def get_percentage(self):
        return round((self.score / self.max_score) * 100, 2)

class Video(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)  # Добавляем поле completed

    def __str__(self):
        return self.title

class Link(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='links')
    title = models.CharField(max_length=200)
    url = models.URLField()
    position = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)  # Добавляем поле completed

    def __str__(self):
        return self.title

class FileAnswer(models.Model):
    chapter_file = models.ForeignKey(
        ChapterFile,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        default=1
    )
    file = models.FileField(upload_to='student_answers/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    grade = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        TeacherProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='graded_answers'
    )
    is_new = models.BooleanField(default=True)  # Для отслеживания новых оценок
    class Meta:
        unique_together = ('chapter_file', 'student')

    def get_upload_path(instance, filename):
        """Генерирует путь для загрузки файла ответа"""
        student = instance.student.studentprofile
        chapter = instance.chapter_file.chapter
        
        # Получаем номер зачетной книги или используем 'unknown' если его нет
        record_book = student.record_book_number or 'unknown'
        
        # Создаем безопасное имя папки главы (удаляем спецсимволы)
        import re
        chapter_name = re.sub(r'[^\w\s-]', '', chapter.name).strip().replace(' ', '_')
        
        # Формируем путь: student_answers/<record_book>/<chapter_name>/<filename>
        return f'student_answers/{record_book}/{chapter_name}/{filename}'

    # Обновляем поле file с новым upload_to
    file = models.FileField(upload_to=get_upload_path)

class NotificationManager(models.Manager):
    def unread(self):
        return self.filter(is_read=False)
    
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    objects = NotificationManager()
    notification_type = models.CharField(max_length=50, choices=[
        ('grade', 'Оценка'),
        ('answer', 'Ответ студента'),
    ])
    
    class Meta:
        ordering = ['-created_at']  # Исправлено с uploaded_at на created_at
    
    def __str__(self):
        return f"{self.get_notification_type_display()} для {self.user}"
    
    