from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLES = (
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Администратор'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='student')
    profile_pic = models.ImageField(upload_to='profiles/', blank=True)