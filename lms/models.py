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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofiles') # каждый пользователь может иметь только один профиль.
    user_type = models.CharField(max_length=10, choices=USER_TYPES) # Поле для хранения типа пользователя (студент, преподаватель, администратор)
    student_group = models.ManyToManyField('StudentGroup', blank=True) # Многие-ко-многим связь с моделью StudentGroup. Позволяет пользователю быть частью нескольких групп
    phone = models.CharField(max_length=20, blank=True) # Поле для хранения номера телефона пользователя.

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
    name = models.CharField(max_length=50, unique=True) # Уникальное имя группы
    description = models.TextField(blank=True) # Описание группы
    created_at = models.DateTimeField(auto_now_add=True) # Дата и время создания группы

    def __str__(self):
        return self.name

# КУРСЫ
class Course(models.Model):
    name = models.CharField(max_length=255) # Название курса
    code = models.CharField(max_length=50, unique=True, blank=True) # Уникальный код курса
    description = models.TextField(blank=True) # Описание курса
    is_active = models.BooleanField(default=True) # Флаг, указывающий, активен ли курс
    created_at = models.DateTimeField(auto_now_add=True) # Дата и время создания курса
    updated_at = models.DateTimeField(auto_now=True) # Дата и время последнего обновления курса

    def __str__(self):
        return self.name

# МОДУЛЬ
class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE) # Связь с моделью Course. Указывает, к какому курсу принадлежит модуль
    title = models.CharField(max_length=255) # Название модуля
    description = models.TextField(blank=True) # Описание модуля
    order_number = models.PositiveIntegerField() # Порядковый номер модуля
    is_published = models.BooleanField(default=False) # Флаг, указывающий, опубликован ли модуль
    publish_date = models.DateTimeField(null=True, blank=True) # Дата и время публикации модуля
    created_at = models.DateTimeField(auto_now_add=True) # Дата и время создания модуля.
    updated_at = models.DateTimeField(auto_now=True) # Дата и время последнего обновления модуля

    class Meta:
        ordering = ['order_number']

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

    module = models.ForeignKey(Module, on_delete=models.CASCADE) #  Связь с моделью Module. Указывает, к какому модулю принадлежит материал
    title = models.CharField(max_length=255) # Название материала
    content = models.TextField(blank=True) # Содержимое материала
    material_type = models.CharField(max_length=50, choices=MATERIAL_TYPES) # Тип материала (лекция, тест, задание, файл, ссылка)
    external_link = models.URLField(blank=True) # Внешняя ссылка на материал
    file = models.FileField(upload_to='materials/', blank=True) # Файл, прикрепленный к материалу
    order_number = models.PositiveIntegerField() #  Порядковый номер материала
    is_published = models.BooleanField(default=False) #  Флаг, указывающий, опубликован ли материал
    publish_date = models.DateTimeField(null=True, blank=True) # Дата и время публикации материала.
    created_at = models.DateTimeField(auto_now_add=True) # Дата и время создания материала.
    updated_at = models.DateTimeField(auto_now=True) # Дата и время последнего обновления материала

    class Meta:
        ordering = ['order_number']

    def __str__(self):
        return f"{self.module.title} - {self.title}"

# ЗАДАНИЯ
class Assignment(models.Model):
    SUBMISSION_TYPES = (
        ('text', 'Текст'),
        ('file', 'Файл'),
        ('both', 'Текст и файл'),
    )

    material = models.OneToOneField(Material, on_delete=models.CASCADE) #  Связь один-к-одному с моделью Material. Указывает, к какому материалу принадлежит задание
    max_score = models.PositiveIntegerField(null=True, blank=True) # Максимальный балл за задание.
    due_date = models.DateTimeField(null=True, blank=True) # Крайний срок сдачи задания.
    submission_type = models.CharField(max_length=50, choices=SUBMISSION_TYPES) #  Тип сдачи задания (текст, файл, текст и файл).
    attempts_allowed = models.PositiveIntegerField(default=1) #  Количество попыток, разрешенных для сдачи задания.
    grading_type = models.CharField(max_length=50, blank=True) # Тип оценки задания.

    def __str__(self):
        return f"Задание: {self.material.title}"

# СДАЧА ЗАДАНИЯ
class Submission(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Отправлено'),
        ('graded', 'Оценено'),
        ('rejected', 'Отклонено'),
    )

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE) #  Связь с моделью Assignment. Указывает, к какому заданию принадлежит сдача.
    student = models.ForeignKey(User, on_delete=models.CASCADE) # Связь с моделью User. Указывает, какой студент сдал задание.
    submission_text = models.TextField(blank=True) #  Текст сдачи.
    submission_file = models.FileField(upload_to='submissions/', blank=True) # Файл, прикрепленный к сдаче.
    submitted_at = models.DateTimeField(auto_now_add=True) #  Дата и время сдачи.
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='submitted') #  Статус сдачи (отправлено, оценено, отклонено).
    attempt_number = models.PositiveIntegerField(default=1) # Номер попытки сдачи.

    class Meta:
        unique_together = ('assignment', 'student', 'attempt_number')

    def __str__(self):
        return f"{self.student.username} - {self.assignment.material.title}"

# ОЦЕНКА
class Grade(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, null=True, blank=True) # Связь один-к-одному с моделью Submission. Указывает, к какой сдаче принадлежит оценка.
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE) # Связь с моделью Assignment. Указывает, к какому заданию принадлежит оценка.
    student = models.ForeignKey(User, on_delete=models.CASCADE) # Связь с моделью User. Указывает, какой студент получил оценку.
    score = models.PositiveIntegerField(null=True, blank=True) # Оценка за задание.
    feedback = models.TextField(blank=True) # Обратная связь по заданию.
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_works') # Связь с моделью User. Указывает, кто оценил задание.
    graded_at = models.DateTimeField(null=True, blank=True) # Дата и время оценки.
    status = models.CharField(max_length=50, blank=True) # Статус оценки.

    def __str__(self):
        return f"Оценка {self.score} для {self.student.username}"

# ДОСТУП
class CourseAccess(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE) # Связь с моделью Course. Указывает, к какому курсу принадлежит доступ.
    group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE) # Связь с моделью StudentGroup. Указывает, какая группа имеет доступ.
    access_type = models.CharField(max_length=50) # Тип доступа.
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Связь с моделью User. Указывает, кто предоставил доступ.
    granted_at = models.DateTimeField(auto_now_add=True) #  Дата и время предоставления доступа.
    revoked_at = models.DateTimeField(null=True, blank=True) # Дата и время отзыва доступа.

    class Meta:
        unique_together = ('course', 'group', 'access_type')

    def __str__(self):
        return f"{self.group.name} доступ к {self.course.name}"

# ЧАТ
class Chat(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE) # Связь с моделью Course. Указывает, к какому курсу принадлежит чат.
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_chats') #  Связь с моделью User. Указывает, какой студент участвует в чате.
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_chats') # Связь с моделью User. Указывает, какой преподаватель участвует в чате.
    is_active = models.BooleanField(default=True) # Флаг, указывающий, активен ли чат.
    created_at = models.DateTimeField(auto_now_add=True) # Дата и время создания чата.


    class Meta:
        unique_together = ('course', 'student')

    def __str__(self):
        return f"Чат по {self.course.name}"
# СООБЩЕНИЕ 
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE) # связь с моделью Chat. Указывает, к какому чату принадлежит сообщение.
    sender = models.ForeignKey(User, on_delete=models.CASCADE) # Связь с моделью User. Указывает, кто отправил сообщение.
    content = models.TextField() # Содержимое сообщения.
    is_read = models.BooleanField(default=False) # Флаг, указывающий, прочитано ли сообщение.
    sent_at = models.DateTimeField(auto_now_add=True) # Дата и время отправки сообщения.

    def __str__(self):
        return f"Сообщение от {self.sender.username}"

# ПРОСМОТРЫ
class MaterialView(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE) #  Связь с моделью Material. Указывает, какой материал был просмотрен.
    student = models.ForeignKey(User, on_delete=models.CASCADE) #  Связь с моделью User. Указывает, какой студент просмотрел материал.
    first_viewed_at = models.DateTimeField(auto_now_add=True) # Дата и время первого просмотра материала.
    last_viewed_at = models.DateTimeField(auto_now=True) # Дата и время последнего просмотра материала.
    view_count = models.PositiveIntegerField(default=1) # Количество просмотров материала.

    class Meta:
        unique_together = ('material', 'student')

    def __str__(self):
        return f"Просмотр {self.material.title} студентом {self.student.username}"
# ПРОГРЕСС
class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE) # Связь с моделью User. Указывает, какой студент имеет прогресс.
    course = models.ForeignKey(Course, on_delete=models.CASCADE) # Связь с моделью Course. Указывает, к какому курсу относится прогресс.
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) # Процент завершения курса.
    materials_viewed = models.PositiveIntegerField(default=0) # Количество просмотренных материалов.
    materials_total = models.PositiveIntegerField(default=0) #  Общее количество материалов в курсе.
    assignments_completed = models.PositiveIntegerField(default=0) #  Количество выполненных заданий.
    assignments_total = models.PositiveIntegerField(default=0) # Общее количество заданий в курсе.
    average_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # Средний балл за курс.
    last_updated = models.DateTimeField(auto_now=True) # Дата и время последнего обновления прогресса.

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"Прогресс {self.student.username} по {self.course.name}"
