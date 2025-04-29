from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# ПРОФИЛЬ
class UserProfiles(models.Model):
    USER_TYPES = (
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Администратор'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofiles')
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    student_group = models.ManyToManyField('StudentGroup', blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.get_user_type_display()}: {self.user.username}"


# Если пользователь создан (created=True), создается связанный профиль UserProfiles с соответствующим типом пользователя.
# Если пользователь обновлен (created=False), сохраняется существующий профиль.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        user_type = 'admin' if instance.is_superuser else 'teacher' if instance.groups.filter(name='Преподаватель').exists() else 'student'
        UserProfiles.objects.create(user=instance, user_type=user_type)
    else:
        instance.userprofiles.save()


# ГРУППЫ
class StudentGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# КУРСЫ
class Course(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# МОДУЛЬ
class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    publish_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.course.name} - {self.title}"

# МАТЕРИАЛ
class Material(models.Model):
    MATERIAL_TYPES = (
        ('lecture', 'Лекция'),
        ('test', 'Тест'),
        ('assignment', 'Задание'),
        ('file', 'Файл'),
        ('link', 'Ссылка'),
    )

    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    material_type = models.CharField(max_length=50, choices=MATERIAL_TYPES)
    external_link = models.URLField(blank=True)
    file = models.FileField(upload_to='materials/', blank=True)
    is_published = models.BooleanField(default=False)
    publish_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.module.title} - {self.title}"


# ЗАДАНИЯ
class Assignment(models.Model):
    ASSIGNMENT_TYPES = (
        ('intermediate', 'Промежуточный тест'),
        ('control', 'Контрольный тест'),
        ('lab', 'Лабораторная работа'),
    )

    material = models.OneToOneField(Material, on_delete=models.CASCADE)
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPES)
    max_score = models.PositiveIntegerField(default=10)
    due_date = models.DateTimeField(null=True, blank=True)
    lab_file = models.FileField(upload_to='lab_files/', blank=True, null=True)
    submission_type = models.CharField(max_length=50, choices=(
        ('text', 'Текст'),
        ('file', 'Файл'),
        ('both', 'Текст и файл'),
    ), default='file')
    attempts_allowed = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.get_assignment_type_display()}: {self.material.title}"



# Модель для тестовых вопросов
class TestQuestion(models.Model):
    QUESTION_TYPES = (
        ('single', 'Один правильный ответ'),
        ('multiple', 'Несколько правильных ответов'),
        ('text', 'Текстовый ответ'),
    )

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Вопрос: {self.question_text[:50]}..."


class AnswerOption(models.Model):
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.option_text[:50]}... ({'✓' if self.is_correct else '✗'})"


# СДАЧА ЗАДАНИЯ
class Submission(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Отправлено'),
        ('graded', 'Оценено'),
        ('rejected', 'Отклонено'),
    )

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    submission_text = models.TextField(blank=True)
    submission_file = models.FileField(upload_to='submissions/', blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='submitted')
    attempt_number = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('assignment', 'student', 'attempt_number')

    def __str__(self):
        return f"{self.student.username} - {self.assignment.material.title}"


# ОЦЕНКА
class Grade(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, null=True, blank=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_works')
    graded_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Оценка {self.score} для {self.student.username}"


# ДОСТУП
class CourseAccess(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=50)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('course', 'group', 'access_type')

    def __str__(self):
        return f"{self.group.name} доступ к {self.course.name}"


# ЧАТ
class Chat(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_chats')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_chats')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'student')

    def __str__(self):
        return f"Чат по {self.course.name}"
# СООБЩЕНИЕ 
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщение от {self.sender.username}"

# ПРОСМОТРЫ
class MaterialView(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    first_viewed_at = models.DateTimeField(auto_now_add=True)
    last_viewed_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('material', 'student')

    def __str__(self):
        return f"Просмотр {self.material.title} студентом {self.student.username}"

# ПРОГРЕСС
class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    materials_viewed = models.PositiveIntegerField(default=0)
    materials_total = models.PositiveIntegerField(default=0)
    assignments_completed = models.PositiveIntegerField(default=0)
    assignments_total = models.PositiveIntegerField(default=0)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"Прогресс {self.student.username} по {self.course.name}"
