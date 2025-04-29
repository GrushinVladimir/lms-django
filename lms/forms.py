from django import forms
from .models import Material, Assignment, Submission, Grade, Message, Course, Module
from .models import Assignment, TestQuestion, AnswerOption
from django.forms import inlineformset_factory

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['title', 'content', 'material_type', 'external_link', 'file', 'is_published', 'publish_date']
        widgets = {
            'publish_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        material_type = cleaned_data.get('material_type')
        
        if material_type == 'lecture' and not cleaned_data.get('content'):
            raise forms.ValidationError("Для лекции необходимо заполнить содержание")
            
        if material_type == 'file' and not cleaned_data.get('file'):
            raise forms.ValidationError("Для типа 'Файл' необходимо загрузить файл")
            
        if material_type == 'link' and not cleaned_data.get('external_link'):
            raise forms.ValidationError("Для типа 'Ссылка' необходимо указать URL")
            
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False
        
        # Динамическое обновление полей в зависимости от типа материала
        if 'material_type' in self.data:
            material_type = self.data.get('material_type')
            self.update_fields(material_type)
        elif self.instance.pk:
            self.update_fields(self.instance.material_type)

    def update_fields(self, material_type):
        if material_type == 'lecture':
            self.fields['content'].required = True
            self.fields['file'].required = False
            self.fields['external_link'].required = False
        elif material_type == 'file':
            self.fields['file'].required = True
            self.fields['content'].required = False
            self.fields['external_link'].required = False
        elif material_type == 'link':
            self.fields['external_link'].required = True
            self.fields['content'].required = False
            self.fields['file'].required = False
        elif material_type in ['test', 'assignment']:
            self.fields['content'].required = False
            self.fields['file'].required = False
            self.fields['external_link'].required = False

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['assignment_type', 'max_score', 'due_date', 'lab_file', 'submission_type', 'attempts_allowed']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['max_score'].initial = 10
        self.fields['max_score'].widget.attrs['readonly'] = True
        if 'assignment_type' in self.data:
            assignment_type = self.data.get('assignment_type')
            self.update_fields(assignment_type)
        elif self.instance.pk:
            self.update_fields(self.instance.assignment_type)

    def update_fields(self, assignment_type):
        if assignment_type == 'lab':
            self.fields['lab_file'].required = True
        else:
            self.fields['lab_file'].required = False
            self.fields['lab_file'].widget = forms.HiddenInput()

        if assignment_type in ['intermediate', 'control']:
            self.fields['attempts_allowed'].required = True
        else:
            self.fields['attempts_allowed'].required = False
            self.fields['attempts_allowed'].widget = forms.HiddenInput()


class TestQuestionForm(forms.ModelForm):
    class Meta:
        model = TestQuestion
        fields = ['question_text', 'question_type']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control'}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
        }


class AnswerOptionForm(forms.ModelForm):
    class Meta:
        model = AnswerOption
        fields = ['option_text', 'is_correct']
        widgets = {
            'option_text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
# Создаем formset для вариантов ответов
AnswerOptionFormSet = inlineformset_factory(
    TestQuestion,
    AnswerOption,
    form=AnswerOptionForm,
    extra=1,
    can_delete=True
)
class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['submission_text', 'submission_file']

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['score', 'feedback']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'description', 'is_active']

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'is_published', 'publish_date']
