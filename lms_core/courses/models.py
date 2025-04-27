from django.db import models
from users.models import CustomUser

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='taught_courses')
    students = models.ManyToManyField(CustomUser, related_name='enrolled_courses', blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField()  # Для сортировки

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    video_url = models.URLField(blank=True)
    file = models.FileField(upload_to='lessons/', blank=True)