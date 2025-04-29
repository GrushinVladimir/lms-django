from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class UserCreateForm(UserCreationForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.filter(name__in=['Студент', 'Преподаватель']),
        required=True,
        label='Тип пользователя'
    )
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'group')