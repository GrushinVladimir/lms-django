from datetime import datetime

def greeting_context(request):
    current_hour = datetime.now().hour
    
    if 5 <= current_hour < 12:
        greeting = "Доброе утро"
    elif 12 <= current_hour < 18:
        greeting = "Добрый день"
    else:
        greeting = "Добрый вечер"
    
    return {'greeting': greeting}