from django import template
from lms_cleint.models import Question

register = template.Library()

@register.filter
def get_question(questions, question_id):
    return questions.filter(id=question_id).first()

@register.filter
def is_list(value):
    return isinstance(value, list)