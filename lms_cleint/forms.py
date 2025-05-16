from django import forms
from tinymce.widgets import TinyMCE
from .models import (
    Course, Subject, StudentGroup, TeacherProfile,
    Chapter, ChapterFile, Article, Test, Question, Answer
)

class CourseForm(forms.ModelForm):
    teachers = forms.ModelMultipleChoiceField(
        queryset=TeacherProfile.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select-multiple'}),
        required=True
    )
    student_groups = forms.ModelMultipleChoiceField(
        queryset=StudentGroup.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select-multiple'}),
        required=True
    )
    
    class Meta:
        model = Course
        fields = ['name', 'teachers', 'student_groups']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'teachers', 'student_groups']
        widgets = {
            'teachers': forms.SelectMultiple(attrs={'class': 'select-multiple'}),
            'student_groups': forms.SelectMultiple(attrs={'class': 'select-multiple'})
        }
    
    def __init__(self, *args, **kwargs):
        course_id = kwargs.pop('course_id', None)
        super().__init__(*args, **kwargs)
        
        if course_id:
            course = Course.objects.get(id=course_id)
            self.fields['student_groups'].queryset = course.student_groups.all()
            self.fields['teachers'].queryset = course.teachers.all()

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['name', 'teachers', 'student_groups']
        widgets = {
            'teachers': forms.SelectMultiple(attrs={'class': 'select-multiple'}),
            'student_groups': forms.SelectMultiple(attrs={'class': 'select-multiple'})
        }
    
    def __init__(self, *args, **kwargs):
        subject_id = kwargs.pop('subject_id', None)
        super().__init__(*args, **kwargs)
        
        if subject_id:
            subject = Subject.objects.get(id=subject_id)
            self.fields['student_groups'].queryset = subject.student_groups.all()
            self.fields['teachers'].queryset = subject.teachers.all()

class ChapterFileForm(forms.ModelForm):
    class Meta:
        model = ChapterFile
        fields = ['file', 'display_name']
        widgets = {
            'file': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'})
        }

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']
        widgets = {
            'content': TinyMCE(attrs={'cols': 80, 'rows': 30}),
        }

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'question_type': forms.Select(attrs={
                'class': 'form-select',
                'onchange': "toggleAnswerFields(this)"
            }),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.RadioSelect(choices=[(True, 'Правильный ответ')]),
        }

QuestionFormSet = forms.inlineformset_factory(
    Test, Question, form=QuestionForm, 
    extra=1, can_delete=True
)

AnswerFormSet = forms.inlineformset_factory(
    Question, Answer, form=AnswerForm,
    extra=1, can_delete=True
)