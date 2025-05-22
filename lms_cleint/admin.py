from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (CustomUser, StudentProfile, TeacherProfile, 
                    StudentGroup, Course, Subject)
from .models import Test, Question, Answer
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_student', 'is_teacher')
    actions = ['make_teacher', 'make_student']
    
    def make_teacher(self, request, queryset):
        queryset.update(is_teacher=True, is_student=False)
    make_teacher.short_description = "Сделать преподавателем"
    
    def make_student(self, request, queryset):
        queryset.update(is_student=True, is_teacher=False)
    make_student.short_description = "Сделать студентом"

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'group')
    list_filter = ('group',)
    search_fields = ('user__username', 'user__last_name', 'user__first_name')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'position', 'classroom')
    search_fields = ('last_name', 'first_name', 'middle_name')
    list_filter = ('category', 'position')
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

admin.site.register(Test)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(StudentGroup)
admin.site.register(Course)
admin.site.register(Subject)