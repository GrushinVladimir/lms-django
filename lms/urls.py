from django.urls import path
from .views import home, teacher_dashboard, student_dashboard
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),
    path('teacher/', teacher_dashboard, name='teacher_dashboard'),
    path('student/', student_dashboard, name='student_dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # Убрал лишнюю скобку
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]