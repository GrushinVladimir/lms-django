from django.apps import AppConfig

class LmsCleintConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lms_cleint'
    
    def ready(self):
        import lms_cleint.signals