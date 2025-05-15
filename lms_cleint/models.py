from django.db import models
from django.contrib.auth.models import AbstractUser
from tinymce.models import HTMLField

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
    
    def __str__(self):
        initials = f"{self.first_name[0]}.{self.middle_name[0]}." if self.middle_name else f"{self.first_name[0]}."
        return f"{self.last_name} {initials}"

class StudentProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(StudentGroup, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.group})"

class Course(models.Model):
    name = models.CharField(max_length=100)
    teachers = models.ManyToManyField(TeacherProfile)
    student_groups = models.ManyToManyField(StudentGroup)
    
    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teachers = models.ManyToManyField(TeacherProfile)
    student_groups = models.ManyToManyField(StudentGroup)
    
    def __str__(self):
        return self.name

class Chapter(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teachers = models.ManyToManyField(TeacherProfile)
    student_groups = models.ManyToManyField(StudentGroup)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ChapterFile(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    file = models.FileField(upload_to='chapter_files/')
    display_name = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField(default=0)  # Добавляем поле позиции

    def __str__(self):
        return self.display_name
    
    def file_extension(self):
        return self.file.name.split('.')[-1].lower()
    
    def is_pdf(self):
        return self.file_extension() == 'pdf'
    
    def is_word(self):
        return self.file_extension() in ['doc', 'docx']

class Article(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = HTMLField(verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    position = models.PositiveIntegerField(default=0)  # Добавляем поле позиции

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.title