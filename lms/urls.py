from django.urls import path
from .views import (
    home, teacher_dashboard, student_dashboard, course_detail, module_detail,
    material_detail, create_material, edit_material, delete_material,
    create_assignment, edit_assignment, delete_assignment, grade_submission,
    submission_detail, submit_assignment, chat_detail, create_course,
    edit_course, delete_course, create_module, edit_module, delete_module,
    create_test_questions, edit_question, take_test
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),
    path('teacher/', teacher_dashboard, name='teacher_dashboard'),
    path('student/', student_dashboard, name='student_dashboard'),
    path('course/<int:course_id>/', course_detail, name='course_detail'),
    path('module/<int:module_id>/', module_detail, name='module_detail'),
    path('material/<int:material_id>/', material_detail, name='material_detail'),
    path('material/create/<int:module_id>/', create_material, name='create_material'),
    path('material/edit/<int:material_id>/', edit_material, name='edit_material'),
    path('material/delete/<int:material_id>/', delete_material, name='delete_material'),
    path('assignment/create/<int:material_id>/', create_assignment, name='create_assignment'),
    path('assignment/edit/<int:assignment_id>/', edit_assignment, name='edit_assignment'),
    path('assignment/delete/<int:assignment_id>/', delete_assignment, name='delete_assignment'),
    path('submission/grade/<int:submission_id>/', grade_submission, name='grade_submission'),
    path('submission/<int:submission_id>/', submission_detail, name='submission_detail'),
    path('assignment/submit/<int:assignment_id>/', submit_assignment, name='submit_assignment'),
    path('chat/<int:course_id>/<int:student_id>/', chat_detail, name='chat_detail'),
    path('course/create/', create_course, name='create_course'),
    path('course/edit/<int:course_id>/', edit_course, name='edit_course'),
    path('course/delete/<int:course_id>/', delete_course, name='delete_course'),
    path('module/create/<int:course_id>/', create_module, name='create_module'),
    path('module/edit/<int:module_id>/', edit_module, name='edit_module'),
    path('module/delete/<int:module_id>/', delete_module, name='delete_module'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('assignment/<int:assignment_id>/questions/', create_test_questions, name='create_test_questions'),
    path('question/<int:question_id>/edit/', edit_question, name='edit_question'),
    path('test/<int:assignment_id>/take/', take_test, name='take_test'),
]
