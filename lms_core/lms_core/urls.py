from django.contrib import admin

from django.urls import path, include
from courses.views import home

from django.conf import settings 
from django.conf.urls.static import static 



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('courses/', include('courses.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # Добавьте эту строку
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)