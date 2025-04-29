from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfiles, StudentGroup

# Инлайн-профиль для отображения внутри пользователя
class UserProfilesInline(admin.StackedInline):
    model = UserProfiles
    can_delete = False
    filter_horizontal = ('student_group',)  # Для удобного выбора групп

# Расширяем стандартный UserAdmin
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfilesInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type', 'get_groups')
    
    def get_user_type(self, obj):
        return obj.userprofiles.get_user_type_display() if hasattr(obj, 'userprofiles') else '-'
    get_user_type.short_description = 'Тип пользователя'
    
    def get_groups(self, obj):
        if hasattr(obj, 'userprofiles'):
            return ", ".join([group.name for group in obj.userprofiles.student_group.all()])
        return '-'
    get_groups.short_description = 'Группы'

# Перерегистрируем UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Регистрируем StudentGroup
admin.site.register(StudentGroup)