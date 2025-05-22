from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),

    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:course_id>/subjects/', views.subject_list, name='subject_list'),
    path('courses/<int:course_id>/subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),

    path('subjects/<int:subject_id>/chapters/', views.chapter_list, name='chapter_list'),
    path('subjects/<int:subject_id>/chapters/create/', views.chapter_create, name='chapter_create'),
    path('chapters/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    path('files/<int:file_id>/delete/', views.delete_file, name='delete_file'),

    path('chapter/<int:chapter_id>/article/create/', views.create_article, name='create_article'),
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),
    path('upload_image/', views.upload_image, name='upload_image'),
    path('article/<int:article_id>/edit/', views.edit_article, name='edit_article'),
    path('article/<int:article_id>/delete/', views.delete_article, name='delete_article'),
    path('chapter/<int:chapter_id>/update_materials_order/', views.update_materials_order, name='update_materials_order'),

    path('test/edit/<int:test_id>/', views.edit_test, name='edit_test'),
    path('question/add/<int:test_id>/', views.add_question, name='add_question'),

    path('test/create/<int:chapter_id>/', views.create_test, name='create_test'),
    path('test/delete/<int:test_id>/', views.delete_test, name='delete_test'),
    path('question/delete/<int:question_id>/', views.delete_question, name='delete_question'),
    path('test/view/<int:test_id>/', views.view_test, name='view_test'),
    path('test/submit/<int:test_id>/', views.submit_test, name='submit_test'),

    path('test/<int:test_id>/submit/', views.submit_test, name='submit_test'),
    path('test/<int:test_id>/result/', views.test_result, name='test_result'),
    path('test/result/<int:result_id>/', views.view_test_result, name='view_test_result'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
]
