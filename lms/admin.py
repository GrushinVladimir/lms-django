# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfiles

class UserProfilesInline(admin.StackedInline):
    model = UserProfiles
    can_delete = False
    verbose_name_plural = 'Профиль'
    fk_name = 'user'
    filter_horizontal = ('student_group',)

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfilesInline,)
    list_display = ('username', 'email', 'get_user_type', 'is_staff')
    list_filter = ('userprofiles__user_type', 'is_staff', 'is_superuser')
    
    def get_user_type(self, obj):
        return obj.userprofiles.get_user_type_display()
    get_user_type.short_description = 'Тип пользователя'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)