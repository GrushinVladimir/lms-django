from django import forms
from .models import Material, Assignment, Submission, Grade, Message, Course, Module

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['title', 'content', 'material_type', 'external_link', 'file', 'order_number', 'is_published', 'publish_date']

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['max_score', 'due_date', 'submission_type', 'attempts_allowed', 'grading_type']

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
        fields = ['title', 'description', 'order_number', 'is_published', 'publish_date']
